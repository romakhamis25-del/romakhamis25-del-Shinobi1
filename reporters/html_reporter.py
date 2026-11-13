"""SHINOBI :: HTML Report Generator."""

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Template

from config_parser import Finding


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SHINOBI Report</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; margin: 40px; background:#f7f9fc; color:#1a1a2e; }
  h1 { color:#0f3460; border-bottom:3px solid #e94560; padding-bottom:10px; }
  .card { background:#fff; border-radius:12px; padding:20px; margin:15px 0;
          box-shadow:0 2px 8px rgba(0,0,0,.08); }
  .severity-HIGH { border-left:6px solid #e94560; }
  .severity-MEDIUM { border-left:6px solid #f39c12; }
  .severity-LOW { border-left:6px solid #16a085; }
  code { background:#eef1f7; padding:2px 6px; border-radius:4px; }
  .summary { background:#0f3460; color:#fff; padding:20px; border-radius:12px; }
</style>
</head>
<body>
<h1>🥷 SHINOBI — Defensive Audit Report</h1>
<p>Generated: {{ generated_at }}</p>
<div class="summary">
  <h2>Executive Summary</h2>
  <p>{{ ai_summary }}</p>
</div>
<h2>Findings ({{ findings|length }})</h2>
{% for f in findings %}
<div class="card severity-{{ f.highest_severity }}">
  <h3>{{ f.url }} — <code>{{ f.status_code }}</code></h3>
  <p><strong>Server:</strong> {{ f.server or 'N/A' }}</p>
  <ul>
  {% for gap in f.header_gaps %}
    <li><strong>[{{ gap.severity }}]</strong> Missing <code>{{ gap.header }}</code>
        — {{ gap.description }} <em>(ISO {{ gap.iso_control }})</em></li>
  {% endfor %}
  </ul>
</div>
{% endfor %}
</body>
</html>
"""


def render_html_report(
    findings: List[Finding], ai_result: Dict[str, Any], output_path: str
) -> Path:
    sev_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    enriched = []
    for f in findings:
        highest = max(
            (g.severity for g in f.header_gaps),
            key=lambda s: sev_order.get(s, 0),
            default="LOW",
        )
        enriched.append({
            "url": f.url,
            "status_code": f.status_code,
            "server": f.server,
            "header_gaps": [asdict(g) for g in f.header_gaps],
            "highest_severity": highest,
        })

    html = Template(HTML_TEMPLATE).render(
        generated_at=datetime.now(timezone.utc).isoformat(),
        findings=enriched,
        ai_summary=ai_result.get("executive_summary", "No AI summary available."),
    )
    path = Path(output_path)
    path.write_text(html, encoding="utf-8")
    return path
