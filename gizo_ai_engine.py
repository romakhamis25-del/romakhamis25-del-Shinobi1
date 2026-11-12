#!/usr/bin/env python3
import os
import csv
from datetime import datetime

def read_file_safely(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return "No data available or tool was not executed."

def process_gizo_core(target, output_dir):
    print("    [*] Analyzing collected data with Gizo AI Core...")
    
    nmap_data = read_file_safely(os.path.join(output_dir, "nmap_scan.txt"))
    nuclei_data = read_file_safely(os.path.join(output_dir, "nuclei_report.txt"))
    sqlmap_data = read_file_safely(os.path.join(output_dir, "sqlmap_log.txt"))
    
    ports_open = "No open ports detected"
    if "open" in nmap_data.lower():
        ports_open = "Open ports and active services detected (see nmap_scan.txt)"
    
    vuln_found = "No critical vulnerabilities detected automatically"
    if "vulnerability" in nuclei_data.lower() or "vulnerable" in sqlmap_data.lower() or "is vulnerable" in sqlmap_data.lower():
        vuln_found = "Potential vulnerabilities detected (see Nuclei/Sqlmap reports)"

    iso_status = "Compliant (Initial Assessment)"
    iso_control = "A.12.6.1 (Management of Technical Vulnerabilities)"
    
    if "vulnerable" in sqlmap_data.lower() or len(nuclei_data) > 200: 
        iso_status = "Non-Compliant - Immediate Action Required"
    
    gizo_directive = (
        f"Gizo AI Analysis: Target {target} audited. "
        f"Network Status: {ports_open}. "
        f"Vulnerability Status: {vuln_found}. "
        f"Recommended Action: Review WAF configurations, enforce parameterized queries, "
        f"and consult output directory logs to remediate identified vulnerabilities."
    )

    report_file = os.path.join(output_dir, f"SHINOBI_ISO27001_REPORT_{target.replace('.', '_')}.csv")
    
    with open(report_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SHINOBI Intelligent Cognitive Penetration Test Report"])
        writer.writerow(["Target", "Date", "ISO 27001 Status", "Control Mapping", "Gizo AI Directive"])
        writer.writerow([target, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), iso_status, iso_control, gizo_directive])
        writer.writerow([])
        writer.writerow(["Detailed Findings Summary"])
        writer.writerow(["Nmap Status", "Nuclei Status", "Sqlmap Status"])
        writer.writerow(["Completed" if "open" in nmap_data.lower() else "Failed", 
                         "Completed" if os.path.exists(os.path.join(output_dir, "nuclei_report.txt")) else "Skipped",
                         "Completed" if os.path.exists(os.path.join(output_dir, "sqlmap_log.txt")) else "Skipped"])

    print(f"    [+] ISO 27001 intelligent report generated: {report_file}")
    return report_file
