#!/usr/bin/env python3
import subprocess
import os

def run_sqlmap(urls_with_params, output_dir):
    if not urls_with_params:
        return
        
    output_file = os.path.join(output_dir, "sqlmap_log.txt")
    print(f"    [*] بدء فحص حقن SQL المستهدف على {len(urls_with_params)} رابط...")
    
    # نفحص أول 3 روابط فقط لتوفير الوقت وتجنب الحظر، يمكنك إزالة الشريحة [:3] لفحص الكل
    targets_to_scan = urls_with_params[:3] 
    
    for url in targets_to_scan:
        print(f"    [*] فحص: {url}")
        command = [
            "sudo", "sqlmap", "-u", url,
            "--batch", "--level=2", "--risk=1",
            "--threads=5", "--timeout=5",
            "--random-agent", "--tamper=space2comment",
            "--answers", "follow=N", # عدم متابعة التوجيهات تلقائياً لتوفير الوقت
            "-o" # استخدام التحسينات الافتراضية
        ]
        
        try:
            # إعادة توجيه المخرجات إلى ملف السجل
            with open(output_file, 'a') as log_file:
                subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT, check=False)
        except Exception as e:
            print(f"    [-] حدث خطأ أثناء فحص {url}: {e}")
            
    print(f"    [+] اكتملت دورة فحص Sqlmap. السجلات محفوظة في: {output_file}")
