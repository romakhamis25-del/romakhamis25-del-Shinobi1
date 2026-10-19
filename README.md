# 🥷 SHINOBI: Intelligent Cognitive Penetration Testing Pipeline
### Developed by: Abdulrahman Abu Haiba (عبدالرحمن أبوهيبة)
  
SHINOBI is an advanced, automated multi-tool penetration testing framework designed with **Pipeline Architecture** for the ISEF 2026 Innovation Competition [tMYnjW]. It orchestrates industry-standard network and web auditing utilities, dynamically parsing their concurrent telemetry into a centralized **Cognitive Threat Intelligence Engine** powered by the open-source **Gizo AI Kernel** [tMYnjW].

Unlike standard single-threaded scripts, SHINOBI functions as an autonomous pipeline where each tool serves as an interactive node feeding the next, transforming automated data collection into localized, actionable vulnerability mapping.

---

## 🚀 The 5-Stage Automated Cyber Lifecycle

SHINOBI divides the comprehensive penetration testing lifecycle into **5 automated stages**, processing input domains dynamically from start to finish:


  ### 🎯 Stage 1: Cloud-Native Passive Reconnaissance (`katana_pipeline.py`)
* **Engine:** `Katana Advanced Crawler Engine` [tMYnjW]
* **Operation:** Scrapes target domain boundaries and charts surface architecture. It operates in advanced cloud-compatible scrape and passive modes to pull archived parameters, displaying live status codes without dropping connections [tMYnjW].

### 🔍 Stage 2: Network & Protocol Mapping (`nmap_pipeline.py`)
* **Engine:** `Nmap Scanning Engine` [tMYnjW]
* **Operation:** Invokes an aggressive non-root mapping routine that identifies open ports, live communication protocols, and underlying server daemons (e.g., Apache Traffic Server) [tMYnjW].

### 🛡️ Stage 3: High-Intensity Vulnerability Injection (`sqlmap_pipeline.py`)
* **Engine:** `Sqlmap Anti-WAF Exploit Matrix` [tMYnjW]
* **Operation:** Receives parameterized endpoints dynamically from the pipeline link [tMYnjW]. Deploys optimized, heavily threaded injection routines (`--threads=5`, `--timeout=5`) coupled with advanced obfuscation tampers (`space2comment`) to safely bypass active Web Application Firewalls (WAF) [9ZDVyZ, Vx20Ea].

### 🧠 Stage 4: Advanced Cyber Threat Forensics (`shinobi.py`)
* **Engine:** `SHINOBI Forensics Core` [tMYnjW]
* **Operation:** Merges the automated triad feedback matrices, analyzes error behavioral symptoms (like HTTP 500/403 controls), isolates the host system's **Weakest Link**, and classifies the precise threat profiles under standard vulnerability classifications [Vx20Ea].

### 📊 Stage 5: ISO Governance & Automated Cleanup (`gizo_ai_engine.py`)
* **Engine:** `Gizo AI Engine & ISO Compliance Module` [tMYnjW]
* **Operation:** Maps final structural flaws to international compliance frameworks (**ISO 27001 Control A.12.6.1**) [Vx20Ea]. Generates a clean administrative CSV report and purges execution artifacts to maintain system tracking hygiene [Vx20Ea].

---

## 📊 Live Execution Examples & Telemetry Analysis

### Example 1: Auditing `yahoo.com` (Hardened Enterprise Infrastructure)
When running SHINOBI against a massive infrastructure like Yahoo, the pipeline demonstrates adaptive cognitive resilience [tMYnjW]:
* **Katana Node Output:** Successfully targets structural parameters and handles redirection matrices [tMYnjW].
```text
  • [Katana URL] https://yahoo.com  - [200 OK]
  • [Katana URL] https://yahoo.com  - [301 Moved Permanently]
```
* **Nmap Node Output:** Maps network endpoints and detects active enterprise web servers [tMYnjW].
```text
  PORT    STATE SERVICE      VERSION
  80/tcp  open  http-proxy   Apache Traffic Server
  443/tcp open  ssl/http-proxy Apache Traffic Server
```
* **Sqlmap Node Feedback:** Triggers WAF behavioral blocks (`HTTP 500 Internal Error`), proving active infrastructure filtering [Vx20Ea].
* **SHINOBI Forensic Engine Verdict:** Automatically learns from the WAF block, determines that the web application parameters are filtered, targets **Apache Traffic Server** as the primary exposed attack surface, and logs the CVE vulnerability blueprint into the final report [Vx20Ea].

### Example 2: Auditing `scanme.nmap.org` (Standard Utility Host)
* **Nmap Node Output:** Resolves active open network daemons [tMYnjW].
```text
  [Port Found] 22/tcp open ssh OpenSSH 7.4 (protocol 2.0)
  [Port Found] 80/tcp open http Apache httpd 2.4.6
```
* **SHINOBI Forensic Engine Verdict:** Identifies the open port HTTP daemon as the weakest link, initiates precision automated strike vectors, and maps it directly to the local compliance matrix.

---

## 🖥️ Operational Launch & Installation

Ensure native environment utilities are verified within your Linux environment before invocation:
```bash
sudo apt update && sudo apt install nmap sqlmap -y
```

### Running the Architecture
To trigger the full 5-stage automated recognition pipeline against an authorized host, launch the main controller from your terminal:
```bash
python3 shinobi.py
```
Simply input your target domain when prompted (e.g., `yahoo.com`) and witness the automated orchestration lifecycle execute seamlessly [tMYnjW].

---

## 📜 International CSV Report Mapping
Upon deployment lifecycle conclusion, SHINOBI exports a formal executive metrics report structured directly for institutional compliance auditing [Vx20Ea]:
* **Output Path:** `SHINOBI_5STAGES_REPORT_[target].csv` [Vx20Ea]
* **Compliance Matrix Alignment:** ISO/IEC 27001 Technical Vulnerability Management Standard [Vx20Ea].

## ⚖️ Legal Disclaimer
Usage of SHINOBI for attacking targets without prior mutual consent is strictly illegal. The developer (**Abdulrahman Abu Haiba
