"""
SHINOBI :: Intelligent Cognitive Penetration Testing Pipeline
Repository: Shinobi1
5-stage automated defensive audit with AI reasoning (ISEF 2026).
"""

import asyncio
import csv
import json
import logging
import signal
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from session_manager import SessionManager
from config_parser import ConfigParser, Finding
from ai_analyzer import AICognitiveAnalyzer
from tools.katana_runner import KatanaRunner
from tools.nmap_runner import NmapRunner
from tools.sqlmap_runner import SqlmapRunner
from tools.nuclei_runner import NucleiRunner
from tools.parsers import parse_nmap_xml, parse_nuclei_jsonl
from reporters.html_reporter import render_html_report
from reporters.diff_reporter import diff_reports


# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
def setup_logging(level: str = "INFO") -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("shinobi")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    fh = logging.FileHandler(
        log_dir / f"shinobi_audit_{datetime.now(timezone.utc):%Y%m%d}.log",
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
@dataclass
class ShinobiConfig:
    target_urls: List[str] = field(default_factory=list)
    timeout: float = 15.0
    max_concurrent: int = 5
    rate_limit_delay: float = 1.5
    user_agents: List[str] = field(default_factory=list)
    log_level: str = "INFO"
    ai_enabled: bool = True
    ai_model: str = "llama-3.1-70b-versatile"
    ai_endpoint: str = "https://api.groq.com/openai/v1"
    ai_api_key_env: str = "GROQ_API_KEY"
    output_dir: str = "reports"
    tools_enabled: List[str] = field(default_factory=lambda: ["katana", "nmap"])
    tools_timeout: int = 600

    @classmethod
    def load(cls, path: str = "config.json") -> "ShinobiConfig":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"config.json not found at {path}")
        raw = json.loads(p.read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in raw.items() if k in known})


# ─────────────────────────────────────────────────────────────
# SHINOBI Engine — 5-Stage Pipeline
# ─────────────────────────────────────────────────────────────
class ShinobiEngine:
    """
    Stage 1 → Passive Recon (Katana)
    Stage 2 → Network Mapping (Nmap)
    Stage 3 → Vulnerability Injection (Sqlmap / Nuclei)
    Stage 4 → HTTP Audit + AI Cognitive Forensics
    Stage 5 → ISO 27001 Report Generation
    """

    def __init__(self, config: ShinobiConfig):
        self.config = config
        self.logger = logging.getLogger("shinobi")
        self.session_mgr: Optional[SessionManager] = None
        self.parser = ConfigParser()
        self.ai: Optional[AICognitiveAnalyzer] = None
        self.findings: List[Finding] = []
        self.tool_outputs: Dict[str, Any] = {}
        self._shutdown = asyncio.Event()

        self.runners = {
            "katana": KatanaRunner(timeout=config.tools_timeout),
            "nmap": NmapRunner(timeout=config.tools_timeout),
            "sqlmap": SqlmapRunner(timeout=config.tools_timeout),
            "nuclei": NucleiRunner(timeout=config.tools_timeout),
        }

    async def _initialize(self) -> None:
        self.logger.info("Initializing SHINOBI engine...")
        self.session_mgr = SessionManager(
            user_agents=self.config.user_agents,
            rate_limit_delay=self.config.rate_limit_delay,
            timeout=self.config.timeout,
        )
        if self.config.ai_enabled:
            self.ai = AICognitiveAnalyzer(
                endpoint=self.config.ai_endpoint,
                model=self.config.ai_model,
                api_key_env=self.config.ai_api_key_env,
            )
        self.logger.info("Initialization complete.")

    async def _stage1_passive_recon(self) -> None:
        if "katana" not in self.config.tools_enabled:
            self.logger.info("[Stage 1] Katana disabled — skipping.")
            return
        self.logger.info("[Stage 1] Passive reconnaissance (Katana)...")
        for target in self.config.target_urls:
            result = await self.runners["katana"].scan(target)
            self.tool_outputs.setdefault("katana", {})[target] = result
            if not result.success:
                self.logger.warning(f"[Stage 1] Katana failed on {target}")

    async def _stage2_network_mapping(self) -> None:
        if "nmap" not in self.config.tools_enabled:
            self.logger.info("[Stage 2] Nmap disabled — skipping.")
            return
        self.logger.info("[Stage 2] Network mapping (Nmap)...")
        for target in self.config.target_urls:
            result = await self.runners["nmap"].scan(target)
            self.tool_outputs.setdefault("nmap", {})[target] = result
            if result.success:
                services = parse_nmap_xml(result.stdout)
                self.logger.info(
                    f"[Stage 2] {target}: {len(services)} open port(s)"
                )

    async def _stage3_vulnerability_scan(self) -> None:
        self.logger.info("[Stage 3] Vulnerability injection (Sqlmap + Nuclei)...")
        enabled = [t for t in ("sqlmap", "nuclei") if t in self.config.tools_enabled]
        if not enabled:
            self.logger.info("[Stage 3] All injection tools disabled — skipping.")
            return

        sem = asyncio.Semaphore(self.config.max_concurrent)

        async def _run(tool: str, target: str):
            async with sem:
                if self._shutdown.is_set():
                    return
                result = await self.runners[tool].scan(target)
                self.tool_outputs.setdefault(tool, {})[target] = result
                if result.success and tool == "nuclei":
                    vulns = parse_nuclei_jsonl(result.stdout)
                    self.logger.info(
                        f"[Stage 3] Nuclei {target}: {len(vulns)} finding(s)"
                    )

        tasks = [_run(t, target) for t in enabled for target in self.config.target_urls]
        await asyncio.gather(*tasks)

    async def _stage4_http_audit(self) -> None:
        self.logger.info("[Stage 4] HTTP header audit + AI forensics...")
        for url in self.config.target_urls:
            try:
                response = await self.session_mgr.fetch(url)
                finding = self.parser.evaluate(url, response)
                self.findings.append(finding)
                self.logger.info(
                    f"[Stage 4] {url} → {finding.status_code} "
                    f"({len(finding.header_gaps)} gap(s))"
                )
            except Exception as exc:  # noqa: BLE001
                self.logger.error(f"[Stage 4] {url} failed: {exc}")

    async def _stage5_report(self) -> None:
        self.logger.info("[Stage 5] Generating ISO 27001 compliance report...")
        ai_result: Dict[str, Any] = {}
        if self.ai and self.findings:
            try:
                ai_result = await self.ai.analyze_findings(self.findings)
            except Exception as exc:  # noqa: BLE001
                self.logger.error(f"[Stage 5] AI analysis failed: {exc}")

        out_dir = Path(self.config.output_dir)
        out_dir.mkdir(exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        payload = {
            "framework": "SHINOBI",
            "repository": "Shinobi1",
            "generated_at": ts,
            "targets": self.config.target_urls,
            "findings": [asdict(f) for f in self.findings],
            "tool_outputs": {
                tool: {
                    tgt: {
                        "success": r.success,
                        "returncode": r.returncode,
                        "duration": round(r.duration, 2),
                    }
                    for tgt, r in targets.items()
                }
                for tool, targets in self.tool_outputs.items()
            },
            "ai_analysis": ai_result,
        }
        json_path = out_dir / f"SHINOBI_REPORT_{ts}.json"
        json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        html_path = out_dir / f"SHINOBI_REPORT_{ts}.html"
        try:
            render_html_report(self.findings, ai_result, str(html_path))
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"HTML report failed: {exc}")

        csv_path = out_dir / f"SHINOBI_5STAGES_REPORT_{ts}.csv"
        self._write_csv(csv_path)

        self.logger.info(f"✔ Reports: {json_path} | {html_path} | {csv_path}")

    def _write_csv(self, path: Path) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "Target", "Status", "Server", "Missing Header",
                "Severity", "ISO 27001:2022 Control", "Description",
            ])
            for finding in self.findings:
                if not finding.header_gaps:
                    w.writerow([
                        finding.url, finding.status_code, finding.server or "",
                        "N/A", "NONE", "N/A", "No header gaps detected",
                    ])
                    continue
                for gap in finding.header_gaps:
                    w.writerow([
                        finding.url, finding.status_code, finding.server or "",
                        gap.header, gap.severity, gap.iso_control, gap.description,
                    ])

    async def run(self) -> None:
        try:
            await self._initialize()
            await self._stage1_passive_recon()
            if self._shutdown.is_set():
                return
            await self._stage2_network_mapping()
            if self._shutdown.is_set():
                return
            await self._stage3_vulnerability_scan()
            if self._shutdown.is_set():
                return
            await self._stage4_http_audit()
            await self._stage5_report()
            self.logger.info("✔ SHINOBI pipeline complete.")
        finally:
            if self.session_mgr:
                await self.session_mgr.close()


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
async def async_main() -> None:
    config = ShinobiConfig.load("config.json")
    setup_logging(config.log_level)
    engine = ShinobiEngine(config)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, engine._shutdown.set)
        except NotImplementedError:
            pass

    await engine.run()


def main() -> None:
    # --diff mode: python shinobi.py --diff old.json new.json
    if len(sys.argv) == 4 and sys.argv[1] == "--diff":
        result = diff_reports(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
