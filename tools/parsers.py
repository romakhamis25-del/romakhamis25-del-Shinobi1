"""
SHINOBI :: Output parsers for Nmap XML and Nuclei JSONL.
"""

import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


def parse_nmap_xml(xml_text: str) -> List[Dict[str, Any]]:
    services: List[Dict[str, Any]] = []
    if not xml_text.strip():
        return services
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return services

    for host in root.findall("host"):
        for port in host.findall(".//port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue
            service = port.find("service")
            services.append({
                "port": int(port.get("portid", 0)),
                "protocol": port.get("protocol", ""),
                "service": service.get("name", "") if service is not None else "",
                "version": service.get("version", "") if service is not None else "",
                "product": service.get("product", "") if service is not None else "",
            })
    return services


def parse_nuclei_jsonl(jsonl_text: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            findings.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return findings
