#!/usr/bin/env python3
import subprocess
import os

def run_nmap(target, output_dir):
    output_file = os.path.join(output_dir, "nmap_scan.txt")
    print(f"    [*] جاري فحص المنافذ والخدمات للهدف: {target}")
    
    # أمر Nmap قوي وشامل: فحص SYN Stealth، اكتشاف الإصدارات، توقيت T4، وأهم 1000 منفذ
    # ملاحظة: يمكنك تغيير --top-ports 1000 إلى -p- لفحص جميع المنافذ الـ 65535 (فحص قوة غاشمة كامل)
    command = [
        "nmap", "-sS", "-sV", "-T4", "--top-ports", "1000", 
        "-oN", output_file, target
    ]
    
    try:
        # نستخدم sudo هنا بشكل احتياطي، رغم أن السكريبت الرئيسي يفرض تشغيله كـ root
        subprocess.run(["sudo"] + command, check=True, capture_output=False)
        print(f"    [+] اكتمل فحص Nmap بنجاح. النتائج محفوظة في: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"    [-] فشل فحص Nmap. تأكد من تثبيت الأداة وصحة الهدف. الخطأ: {e}")
