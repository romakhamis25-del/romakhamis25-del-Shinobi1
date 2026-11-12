#!/usr/bin/env python3
import subprocess
import os

def run_katana(target, output_dir):
    output_file = os.path.join(output_dir, "katana_urls.txt")
    print(f"    [*] Initiating deep web crawl on target: {target}")
    
    # خيارات Katana المتقدمة للقوة القصوى:
    # -d 5: عمق زحف 5 مستويات (بدلاً من 3)
    # -jc: تفعيل JavaScript crawling لاكتشاف الروابط الديناميكية
    # -form: استخراج نماذج HTML تلقائياً
    # -kf all: استخراج جميع أنواع المعلمات
    # -timeout 30: مهلة أطول للصفحات البطيئة
    command = [
        "katana", "-u", target, 
        "-d", "5", 
        "-jc", 
        "-form", 
        "-kf", "all",
        "-timeout", "30",
        "-silent", 
        "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"    [+] Katana crawl completed.")
        
        urls_with_params = []
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '?' in line:
                        urls_with_params.append(line.strip())
        
        print(f"    [+] Discovered {len(urls_with_params)} URLs with query parameters.")
        return urls_with_params
        
    except subprocess.CalledProcessError as e:
        print(f"    [-] Katana failed. Ensure it is installed. Error: {e}")
        return []
