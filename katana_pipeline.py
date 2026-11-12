#!/usr/bin/env python3
import subprocess
import os

def run_katana(target, output_dir):
    output_file = os.path.join(output_dir, "katana_urls.txt")
    print(f"    [*] جاري زحف الويب لاكتشاف المسارات والمعلمات للهدف: {target}")
    
    # تشغيل Katana بعمق 3 مستويات وإخراج النتائج لملف
    command = [
        "katana", "-u", target, "-d", "3", "-silent", "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"    [+] اكتمل زحف Katana بنجاح.")
        
        # قراءة الملف واستخراج الروابط التي تحتوي على معلمات (تحتوي على '?') فقط
        urls_with_params = []
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '?' in line:
                        urls_with_params.append(line.strip())
        
        print(f"    [+] تم اكتشاف {len(urls_with_params)} رابط يحتوي على معلمات قابلة للفحص.")
        return urls_with_params
        
    except subprocess.CalledProcessError as e:
        print(f"    [-] فشل تشغيل Katana. تأكد من تثبيتها. الخطأ: {e}")
        return []
