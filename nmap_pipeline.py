#!/usr/bin/env python3
import subprocess
import os

def run_nmap(target, output_dir):
    output_file = os.path.join(output_dir, "nmap_scan.txt")
    print(f"    [*] Scanning ports and services for: {target}")
    
    command = [
        "nmap", "-sS", "-sV", "-T4", "--top-ports", "1000", 
        "-oN", output_file, target
    ]
    
    try:
        subprocess.run(["sudo"] + command, check=True, capture_output=False)
        print(f"    [+] Nmap scan completed. Results saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"    [-] Nmap scan failed. Error: {e}")
