#!/usr/bin/env python3
import subprocess
import os

def run_nuclei(target, output_dir):
    output_file = os.path.join(output_dir, "nuclei_report.txt")
    print(f"    [*] Scanning for known vulnerabilities using Nuclei...")
    
    command = [
        "nuclei", "-u", target, "-silent", "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"    [+] Nuclei scan completed. Results saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"    [-] Nuclei scan failed or no vulnerabilities found. Error: {e}")
