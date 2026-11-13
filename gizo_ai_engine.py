"""
SHINOBI :: AICognitiveAnalyzer
Simulates senior defensive analyst reasoning via LLM (OpenAI-compatible API).
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import httpx

from config_parser import Finding


SYSTEM_PROMPT = """You are a SENIOR DEFENSIVE SECURITY ANALYST with 15+ years of
experience in blue-team operations, threat modeling, and ISO/IEC 27001:2022
compliance auditing. You reason step-by-step, conservatively, and you NEVER
recommend destructive actions.

You will receive structured JSON findings from a defensive scanner. Respond
ONLY with a valid JSON object (no markdown fences, no prose outside JSON)
using this exact schema:

{
  "false_positives": [
    {"finding_index": int, "reason": str}
  ],
  "correlated_risks": [
    {
      "title": str,
      "affected_endpoints": [str],
      "architectural_impact": str,
      "confidence": "low|medium|high"
    }
  ],
  "next_verification_steps": [
    {"step": str, "rationale": str, "non_destructive": true}
  ],
  "iso_27001_mapping": [
    {"control": "A.x.y", "control_name": str, "justification": str}
  ],
  "executive_summary": str
}

REASONING PROTOCOL (follow internally, do not output reasoning text):
  Step 1 — Context analysis & false-positive filtering:
    Discard findings caused by network errors (status_code=0), CDN default
    headers, or duplicate gaps on redirected endpoints.
  Step 2 — Architectural correlation:
    Group findings that share infrastructure (same server header, same
    redirect chain) to expose systemic misconfigurations.
  Step 3 — Next verification:
    Recommend only NON-DESTRUCTIVE checks.
  Step 4 — ISO/IEC 27001:2022 mapping:
    Map each confirmed risk to a real Annex A control.
"""


class AICognitiveAnalyzer:
    def __init__(
        self,
        endpoint: str,
        model: str = "llama-3.1-70b-versatile",
        api_key_env: str = "GROQ_API_KEY",
        timeout: float = 60.0,
        max_retries: int = 2,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger("shinobi.ai")

        api_key = os.getenv(api_key_env, "")
        if not api_key:
            self.logger.warning(
                f"Env var '{api_key_env}' is empty — AI calls will likely 401."
            )
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _build_user_payload(self, findings: List[Finding]) -> str:
        compact = []
        for i, f in enumerate(findings):
            compact.append({
                "index": i,
                "url": f.url,
                "status": f.status_code,
                "server": f.server,
                "x_powered_by": f.powered_by,
                "redirected": f.redirected,
                "error": f.error,
                "gaps": [
                    {"header": g.header, "severity": g.severity, "iso": g.iso_control}
                    for g in f.header_gaps
                ],
            })
        return json.dumps(
            {"findings": compact, "count": len(compact)},
            ensure_ascii=False, indent=2,
        )

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        text = text.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if fence:
            text = fence.group(1)
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"No JSON object found: {text[:200]}")
        return json.loads(text[start:end + 1])

    async def _call_llm(self, user_payload: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_payload},
            ],
            "temperature": 0.2,
            "max_tokens": 2048,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            last_error: Optional[Exception] = None
            for attempt in range(1, self.max_retries + 2):
                try:
                    r = await client.post(
                        f"{self.endpoint}/chat/completions",
                        headers=self._headers, json=body,
                    )
                    if r.status_code == 429 or r.status_code >= 500:
                        wait = 2 ** attempt
                        self.logger.warning(
                            f"AI endpoint {r.status_code} — retry "
                            f"{attempt}/{self.max_retries + 1} in {wait}s"
                        )
                        await asyncio.sleep(wait)
                        continue
                    r.raise_for_status()
                    data = r.json()
                    return data["choices"][0]["message"]["content"]

                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_error = exc
                    wait = 2 ** attempt
                    self.logger.warning(
                        f"AI network error ({type(exc).__name__}) — retry in {wait}s"
                    )
                    await asyncio.sleep(wait)
                except httpx.HTTPStatusError as exc:
                    self.logger.error(f"AI HTTP error: {exc}")
                    raise

            raise RuntimeError(f"AI call failed after retries: {last_error}")

    async def analyze_findings(self, findings: List[Finding]) -> Dict[str, Any]:
        if not findings:
            return {"executive_summary": "No findings to analyze."}

        try:
            user_payload = self._build_user_payload(findings)
            raw = await self._call_llm(user_payload)
            result = self._extract_json(raw)

            required = {
                "false_positives", "correlated_risks",
                "next_verification_steps", "iso_27001_mapping",
                "executive_summary",
            }
            missing = required - result.keys()
            if missing:
                self.logger.warning(f"AI response missing keys: {missing}")
            return result

        except json.JSONDecodeError as exc:
            self.logger.error(f"AI returned invalid JSON: {exc}")
            return {"error": "invalid_json", "raw_excerpt": str(exc)[:300]}
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"AI analysis failed: {exc}")
            return {"error": type(exc).__name__, "message": str(exc)}
