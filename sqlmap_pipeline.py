#!/usr/bin/env python3
import subprocess
import os

def run_sqlmap(urls_with_params, output_dir):
    if not urls_with_params:
        return
        
    output_file = os.path.join(output_dir, "sqlmap_log.txt")
    print(f"    [*] Initiating targeted SQL injection testing on {len(urls_with_params)} URLs...")
    
    targets_to_scan = urls_with_params[:3] 
    
    for url in targets_to_scan:
        print(f"    [*] Testing: {url}")
        command = [
            "sudo", "sqlmap", "-u", url,
            "--batch", "--level=2", "--risk=1",
            "--threads=5", "--timeout=5",
            "--random-agent", "--tamper=space2comment",
            "--answers", "follow=N",
            "-o"
        ]
        
        try:
            with open(output_file, 'a') as log_file:
                subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT, check=False)
        except Exception as e:
            print(f"    [-] Error testing {url}: {e}")
            
    print(f"    [+] Sqlmap cycle completed. Logs saved to: {output_file}")
