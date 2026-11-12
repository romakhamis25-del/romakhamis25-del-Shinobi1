#!/usr/bin/env python3
import os
import sys
import time
import shutil

# ألوان الطرفية الاحترافية
MAGENTA = "\033[1;35m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

def print_banner():
    print(f"{MAGENTA}")
    print(" ██████  ██    ██  ██████  ██    ██  ██████  ███████  ██████  ██ ")
    print(" ██      ██    ██  ██   ██ ███   ██  ██   ██ ██      ██       ██ ")
    print(" █████   ██    ██  ██████  ██ ██ ██  ██   ██ █████   ██   ███ ██ ")
    print(" ██      ██    ██  ██   ██ ██  ████  ██   ██ ██      ██    ██ ██ ")
    print(" ██       ██████   ██████  ██   ███  ██████  ███████  ██████  ██ ")
    print(f" === SHINOBI INTELLIGENT PIPELINE (Root Mode Enabled) === {RESET}\n")

def check_root():
    """التحقق من صلاحيات الجذر (sudo) لضمان عمل الفحص الشامل"""
    if os.geteuid() != 0:
        print(f"{RED}[-] خطأ: يجب تشغيل هذه الأداة بصلاحيات الجذر (Root).{RESET}")
        print(f"{YELLOW}[!] يرجى التشغيل باستخدام: sudo python3 shinobi.py{RESET}")
        sys.exit(1)

def main():
    check_root()
    print_banner()
    
    try:
        target = input(f"{YELLOW}[?] أدخل النطاق أو الهدف المراد فحصه (مثال: example.com): {RESET}").strip()
        if not target:
            print(f"{RED}[-] خطأ: لا يمكن ترك الهدف فارغاً.{RESET}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{RED}[-] تم الإلغاء بواسطة المستخدم.{RESET}")
        sys.exit(0)

    # إنشاء مجلد مخصص لمخرجات هذا الفحص
    output_dir = f"shinobi_output_{target.replace('.', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"{GREEN}[+] تم إنشاء مجلد المخرجات: {output_dir}{RESET}\n")

    # استيراد وحدات خط الأنابيب
    import nmap_pipeline
    import katana_pipeline
    import nuclei_pipeline
    import sqlmap_pipeline
    import gizo_ai_engine

    print(f"{CYAN}{'='*60}")
    print(f" بدء دورة حياة الاختراق الآلية (5 مراحل) للهدف: {target}")
    print(f"{'='*60}{RESET}\n")

    # المرحلة 1: فحص المنافذ والخدمات (Nmap) - يجب أن يكون أولاً
    print(f"{BLUE}[Stage 1] بدء الفحص الشامل للشبكة والخدمات (Nmap Brute-Force Mode)...{RESET}")
    nmap_pipeline.run_nmap(target, output_dir)
    time.sleep(1)

    # المرحلة 2: زحف الويب واكتشاف المعلمات (Katana)
    print(f"{BLUE}[Stage 2] بدء زحف الويب واكتشاف المسارات والمعلمات (Katana)...{RESET}")
    urls_with_params = katana_pipeline.run_katana(target, output_dir)
    time.sleep(1)

    # المرحلة 3: فحص الثغرات المعروفة (Nuclei)
    print(f"{BLUE}[Stage 3] بدء فحص الثغرات المعروفة وإعدادات الخادم الخاطئة (Nuclei)...{RESET}")
    nuclei_pipeline.run_nuclei(target, output_dir)
    time.sleep(1)

    # المرحلة 4: الاستغلال المستهدف (Sqlmap) - مشروط بوجود معلمات
    print(f"{BLUE}[Stage 4] تقييم إمكانية حقن SQL (Sqlmap)...{RESET}")
    if urls_with_params:
        print(f"{YELLOW}[!] تم اكتشاف {len(urls_with_params)} رابط يحتوي على معلمات. بدء فحص Sqlmap المكثف.{RESET}")
        sqlmap_pipeline.run_sqlmap(urls_with_params, output_dir)
    else:
        print(f"{GREEN}[+] لم يتم اكتشاف معلمات URL قابلة للحقن. تخطي مرحلة Sqlmap بأمان.{RESET}")
    time.sleep(1)

    # المرحلة 5: التحليل الجنائي والذكاء الاصطناعي (Gizo AI)
    print(f"{MAGENTA}[Stage 5] تشغيل محرك Gizo AI لتحليل المخرجات وتوليد تقرير ISO 27001...{RESET}")
    gizo_ai_engine.process_gizo_core(target, output_dir)

    print(f"\n{GREEN}[*] اكتملت عملية خط الأنابيب بنجاح. تم حفظ جميع التقارير في: {output_dir}{RESET}")

if __name__ == "__main__":
    main()
