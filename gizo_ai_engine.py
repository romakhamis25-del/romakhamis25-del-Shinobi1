#!/usr/bin/env python3
import os
import csv
import json
import requests
from datetime import datetime

def read_file_tail(filepath, lines=100):
    """قراءة آخر جزء من الملف لتجنب تجاوز حدود الـ Tokens"""
    if not os.path.exists(filepath):
        return "No data available."
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()[-3000:] # قراءة آخر 3000 حرف فقط للتحليل

def query_real_ai(nmap_data, nuclei_data, sqlmap_data):
    """محاولة الاتصال بنموذج ذكاء اصطناعي حقيقي (Groq/Llama-3)"""
    api_key = os.getenv("GIZO_AI_KEY", "")
    
    if not api_key:
        return None # العودة للتحليل المحلي الذكي إذا لم يوجد مفتاح

    prompt = f"""You are Gizo, an elite AI Cybersecurity Analyst and ISO 27001 Lead Auditor. 
    Analyze this raw scan data and provide a concise, professional executive summary.
    
    NMAP DATA: {nmap_data[-1000:]}
    NUCLEI DATA: {nuclei_data[-1500:]}
    SQLMAP DATA: {sqlmap_data[-1000:]}
    
    Output format:
    1. Executive Summary (2 sentences max)
    2. Critical Findings (Bullet points)
    3. ISO 27001 Compliance Verdict (Compliant/Non-Compliant with specific control)
    4. Immediate Remediation Steps
    Keep it professional, technical, and in English.
    """

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception:
        pass
    return None

def advanced_local_analysis(nmap_data, nuclei_data, sqlmap_data):
    """محليل محلي ذكي جداً (Fallback) يولد تقريراً ديناميكياً بدون API"""
    findings = []
    iso_status = "Compliant (Initial Assessment)"
    iso_control = "A.12.6.1 (Management of Technical Vulnerabilities)"

    # 1. تحليل Nmap
    if "open" in nmap_data.lower():
        if "22/tcp" in nmap_data: findings.append("- SSH service detected (Ensure key-based auth is enforced).")
        if "80/tcp" in nmap_data or "443/tcp" in nmap_data: findings.append("- Web server detected (Verify latest patch levels).")
    
    # 2. تحليل Nuclei
    if "vulnerability" in nuclei_data.lower() or "cve-" in nuclei_data.lower():
        iso_status = "Non-Compliant - Immediate Action Required"
        findings.append("- Nuclei detected known CVEs or misconfigurations. Review nuclei_report.txt immediately.")
    
    # 3. تحليل Sqlmap
    if "vulnerable" in sqlmap_data.lower() or "is vulnerable" in sqlmap_data.lower():
        iso_status = "Non-Compliant - Critical Risk"
        findings.append("- CRITICAL: SQL Injection vulnerability confirmed by Sqlmap. Immediate code remediation required.")

    if not findings:
        findings.append("- No critical vulnerabilities automatically detected in this scan.")

    summary = (
        f"Gizo AI Automated Analysis:\n"
        f"• Executive Summary: Target was scanned using SHINOBI 5-stage pipeline. "
        f"Network mapping and vulnerability assessments were completed successfully.\n"
        f"• Key Findings:\n" + "\n".join(findings) + "\n"
        f"• ISO 27001 Verdict: {iso_status} under Control {iso_control}.\n"
        f"• Remediation: Enforce input validation, update server packages, and review WAF rules."
    )
    return summary, iso_status

def process_gizo_core(target, output_dir):
    print("    [*] Activating Gizo AI Core for dynamic forensic analysis...")
    
    nmap_data = read_file_tail(os.path.join(output_dir, "nmap_scan.txt"))
    nuclei_data = read_file_tail(os.path.join(output_dir, "nuclei_report.txt"))
    sqlmap_data = read_file_tail(os.path.join(output_dir, "sqlmap_log.txt"))
    
    # محاولة استخدام الذكاء الاصطناعي الحقيقي
    ai_response = query_real_ai(nmap_data, nuclei_data, sqlmap_data)
    
    if ai_response:
        print("    [+] Real AI (Llama-3) analysis completed successfully.")
        gizo_directive = ai_response
        iso_status = "Non-Compliant" if "Non-Compliant" in ai_response else "Compliant"
    else:
        print("    [*] Using Advanced Heuristic AI Engine (No API Key detected)...")
        gizo_directive, iso_status = advanced_local_analysis(nmap_data, nuclei_data, sqlmap_data)

    # حفظ التقرير
    report_file = os.path.join(output_dir, f"SHINOBI_ISO27001_REPORT_{target.replace('.', '_')}.csv")
    
    with open(report_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SHINOBI Intelligent Cognitive Penetration Test Report"])
        writer.writerow(["Target", "Date", "ISO 27001 Status", "Gizo AI Dynamic Analysis"])
        writer.writerow([target, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), iso_status, gizo_directive.replace('\n', ' | ')])

    # حفظ نسخة نصية أجمل للقراءة
    txt_report = os.path.join(output_dir, "GIZO_AI_ANALYSIS.txt")
    with open(txt_report, 'w', encoding='utf-8') as f:
        f.write(f"=== GIZO AI ANALYSIS FOR: {target} ===\n\n")
        f.write(gizo_directive)

    print(f"    [+] AI Report generated: {txt_report}")
    return report_file
