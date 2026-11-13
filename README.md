# 🥷 SHINOBI: Intelligent Cognitive Penetration Testing Pipeline

**Repository:** Shinobi1 | **Author:** Abdulrahman Abu Haiba | **Event:** ISEF 2026

SHINOBI is a 5-stage automated defensive audit framework with AI-powered
forensic reasoning, mapped to **ISO/IEC 27001:2022**.

## The 5-Stage Lifecycle

1. **Passive Recon** — Katana crawler
2. **Network Mapping** — Nmap (SYN + service detection)
3. **Vulnerability Injection** — Sqlmap + Nuclei
4. **HTTP Audit + AI Forensics** — Header analysis + LLM reasoning
5. **ISO 27001 Report** — JSON + HTML + CSV

## Installation

```bash
git clone https://github.com/romakhamis25-del/Shinobi1.git
cd Shinobi1
pip install -r requirements.txt

# Install tools (Debian/Ubuntu)
sudo apt install nmap sqlmap -y
# Then install Katana + Nuclei from ProjectDiscovery releases.
