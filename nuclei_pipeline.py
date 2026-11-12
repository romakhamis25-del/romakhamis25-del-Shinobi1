#!/usr/bin/env python3
import subprocess
import os

def run_nuclei(target, output_dir):
    output_file = os.path.join(output_dir, "nuclei_report.txt")
    print(f"    [*] جاري فحص الثغرات المعروفة باستخدام Nuclei...")
    
    # تشغيل Nuclei مع تصدير النتائج بصيغة نصية واضحة
    command = [
        "nuclei", "-u", target, "-silent", "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"    [+] اكتمل فحص Nuclei بنجاح. النتائج محفوظة في: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"    [-] فشل تشغيل Nuclei أو لم يتم العثور على ثغرات. الخطأ: {e}")
