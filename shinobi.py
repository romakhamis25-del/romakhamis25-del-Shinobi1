#!/usr/bin/env python3
import os
import sys
import time

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
    if os.geteuid() != 0:
        print(f"{RED}[-] Error: This tool requires root privileges.{RESET}")
        print(f"{YELLOW}[!] Please run with: sudo python3 shinobi.py{RESET}")
        sys.exit(1)

def main():
    check_root()
    print_banner()
    
    try:
        target = input(f"{YELLOW}[?] Enter target domain/URL (e.g., example.com): {RESET}").strip()
        if not target:
            print(f"{RED}[-] Error: Target cannot be empty.{RESET}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{RED}[-] Aborted by user.{RESET}")
        sys.exit(0)

    output_dir = f"shinobi_output_{target.replace('.', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"{GREEN}[+] Output directory created: {output_dir}{RESET}\n")

    import nmap_pipeline
    import katana_pipeline
    import nuclei_pipeline
    import sqlmap_pipeline
    import gizo_ai_engine

    print(f"{CYAN}{'='*60}")
    print(f" Starting 5-Stage Automated Penetration Test on: {target}")
    print(f"{'='*60}{RESET}\n")

    print(f"{BLUE}[Stage 1] Network & Service Discovery (Nmap Brute-Force Mode)...{RESET}")
    nmap_pipeline.run_nmap(target, output_dir)
    time.sleep(1)

    print(f"{BLUE}[Stage 2] Deep Web Crawling & Parameter Discovery (Katana)...{RESET}")
    urls_with_params = katana_pipeline.run_katana(target, output_dir)
    time.sleep(1)

    print(f"{BLUE}[Stage 3] Known Vulnerability Scanning (Nuclei)...{RESET}")
    nuclei_pipeline.run_nuclei(target, output_dir)
    time.sleep(1)

    print(f"{BLUE}[Stage 4] SQL Injection Assessment (Sqlmap)...{RESET}")
    if urls_with_params:
        print(f"{YELLOW}[!] Discovered {len(urls_with_params)} URLs with parameters. Launching Sqlmap.{RESET}")
        sqlmap_pipeline.run_sqlmap(urls_with_params, output_dir)
    else:
        print(f"{GREEN}[+] No injectable URL parameters detected. Safely skipping Sqlmap.{RESET}")
    time.sleep(1)

    print(f"{MAGENTA}[Stage 5] Gizo AI Forensic Analysis & ISO 27001 Report Generation...{RESET}")
    gizo_ai_engine.process_gizo_core(target, output_dir)

    print(f"\n{GREEN}[*] Pipeline completed successfully. All reports saved in: {output_dir}{RESET}")

if __name__ == "__main__":
    main()
