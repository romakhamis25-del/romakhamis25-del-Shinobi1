#!/usr/bin/env python3
import subprocess
import os
import sys

def run_nuclei(target):
    print("\n\033[1;36m[Pipeline - Stage 3] Executing Nuclei Template Vulnerability Scanner...\033[0m")
    output_file = "nuclei_output.txt"
    nuclei_bin = "./nuclei" if os.path.exists("./nuclei") else "nuclei"
    
    # تشغيل نيوكلاي الفعلي
    subprocess.run([nuclei_bin, "-u", target, "-o", output_file, "-silent"], check=False)
    
    vulns = []
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, "r") as f:
            vulns = [line.strip() for line in f.readlines()]
            for v in vulns:
                print(f"  \033[1;31m[Critical CVE]\033[0m {v}")
    else:
        print("\033[1;32m[+] Nuclei scan complete. No core flaws detected.\033[0m")
    return vulns

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_nuclei(sys.argv[1])
