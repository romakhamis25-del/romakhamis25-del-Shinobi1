"""
SHINOBI :: Config & Response Parser
Parses HTTP responses into structured security findings.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


RECOMMENDED_HEADERS = {
    "strict-transport-security": {
        "iso_control": "A.8.20",
        "description": "Missing HSTS — allows SSL-strip downgrade attacks.",
        "severity": "HIGH",
    },
    "content-security-policy": {
        "iso_control": "A.8.28",
        "description": "Missing CSP — XSS payloads execute unrestricted.",
        "severity": "HIGH",
    },
    "x-content-type-options": {
        "iso_control": "A.8.28",
        "description": "Missing nosniff — MIME-confusion possible.",
        "severity": "MEDIUM",
    },
    "x-frame-options": {
        "iso_control": "A.8.28",
        "description": "Missing X-Frame-Options — clickjacking possible.",
        "severity": "MEDIUM",
    },
    "referrer-policy": {
        "iso_control": "A.8.11",
        "description": "Missing Referrer-Policy — data leakage via Referer.",
        "severity": "LOW",
    },
    "permissions-policy": {
        "iso_control": "A.8.28",
        "description": "Missing Permissions-Policy — browser features unrestricted.",
        "severity": "LOW",
    },
}


@dataclass
class HeaderGap:
    header: str
    severity: str
    iso_control: str
    description: str


@dataclass
class Finding:
    url: str
    status_code: int
    server: Optional[str] = None
    powered_by: Optional[str] = None
    header_gaps: List[HeaderGap] = field(default_factory=list)
    present_headers: Dict[str, str] = field(default_factory=dict)
    redirected: bool = False
    error: Optional[str] = None
    scanned_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConfigParser:
    def __init__(self, custom_baseline: Optional[Dict[str, Dict]] = None):
        self.logger = logging.getLogger("shinobi.parser")
        self.baseline = custom_baseline or RECOMMENDED_HEADERS

    @staticmethod
    def load_targets(path: str = "config.json") -> List[str]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid config.json: {exc}") from exc
        targets = data.get("target_urls", [])
        if not isinstance(targets, list):
            raise ValueError("config.json: 'target_urls' must be a list")
        return [str(t).strip() for t in targets if t]

    def evaluate(self, url: str, response: httpx.Response) -> Finding:
        finding = Finding(
            url=url,
            status_code=response.status_code,
            redirected=bool(response.history),
            scanned_at=datetime.now(timezone.utc).isoformat(),
        )

        if response.status_code == 0:
            finding.error = response.headers.get("x-shinobi-error", "unknown_error")
            return finding

        headers = {k.lower(): v for k, v in response.headers.items()}
        finding.server = headers.get("server")
        finding.powered_by = headers.get("x-powered-by")

        for header_name, meta in self.baseline.items():
            if header_name in headers:
                finding.present_headers[header_name] = headers[header_name]
            else:
                finding.header_gaps.append(
                    HeaderGap(
                        header=header_name,
                        severity=meta["severity"],
                        iso_control=meta["iso_control"],
                        description=meta["description"],
                    )
                )
        return finding

    @staticmethod
    def findings_to_json(findings: List[Finding], indent: int = 2) -> str:
        return json.dumps(
            [f.to_dict() for f in findings], indent=indent, ensure_ascii=False
      )
