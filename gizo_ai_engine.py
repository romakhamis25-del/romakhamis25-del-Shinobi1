#!/usr/bin/env python3
import os
import csv
from datetime import datetime

def read_file_safely(filepath):
    """قراءة محتوى الملف بأمان"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return "لم يتم العثور على بيانات أو لم يتم تشغيل الأداة."

def process_gizo_core(target, output_dir):
    print("    [*] جاري تحليل البيانات المجمعة بواسطة نواة Gizo AI...")
    
    # 1. قراءة المخرجات الفعلية من الأدوات
    nmap_data = read_file_safely(os.path.join(output_dir, "nmap_scan.txt"))
    nuclei_data = read_file_safely(os.path.join(output_dir, "nuclei_report.txt"))
    sqlmap_data = read_file_safely(os.path.join(output_dir, "sqlmap_log.txt"))
    
    # 2. تحليل ديناميكي بسيط (يمكن استبداله باستدعاء LLM API حقيقي هنا)
    ports_open = "N/A"
    if "open" in nmap_data.lower():
        # استخراج بسيط للمنافذ المفتوحة من مخرجات Nmap
        ports_open = "تم اكتشاف منافذ مفتوحة وخدمات نشطة (راجع ملف nmap_scan.txt للتفاصيل)"
    
    vuln_found = "لا توجد ثغرات حرجة مكتشفة تلقائياً"
    if "vulnerability" in nuclei_data.lower() or "vulnerable" in sqlmap_data.lower():
        vuln_found = "تم رصد مؤشرات على ثغرات محتملة (راجع تقارير Nuclei/Sqlmap)"

    # 3. تحديد حالة التوافق مع ISO 27001 بناءً على النتائج الفعلية
    iso_status = "متوافق مبدئياً (Compliant)"
    iso_control = "A.12.6.1 (إدارة الثغرات التقنية)"
    
    if "vulnerable" in sqlmap_data.lower() or len(nuclei_data) > 500: # افتراض وجود ثغرات إذا كان التقرير طويلاً
        iso_status = "غير متوافق (Non-Compliant) - يتطلب تدخلاً فورياً"
    
    # 4. صياغة التوصية الذكية الديناميكية
    gizo_directive = (
        f"تحليل Gizo AI: تم فحص الهدف {target}. "
        f"حالة الشبكة: {ports_open}. "
        f"حالة الثغرات: {vuln_found}. "
        f"الإجراء الموصى به: مراجعة إعدادات جدار الحماية (WAF)، وتفعيل الاستعلامات المparameterized، ومراجعة ملف nmap_scan.txt و sqlmap_log.txt لإغلاق الثغرات المحددة."
    )

    # 5. تصدير التقرير النهائي بصيغة CSV احترافية
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

    print(f"    [+] تم توليد تقرير ISO 27001 الذكي بنجاح: {report_file}")
    return report_file
