<p align="center">
  <img src="logo/logo.svg" width="150" height="150">
</p>

# WPHunter  
*Mass WordPress Vulnerability Scanner*  

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-GPLv3-orange.svg)](LICENSE) 

---

## 📖 Overview  

**WPHunter** is fastest WordPress vulnerability scanner designed for **Penetration Testers**  

It allows **mass scanning of WordPress sites**.

---

## ✨ Features  

✔ **Mass Scanning** – multi sites scan at one time.  
✔ **High Performance** – Asynchronous I/O with configurable concurrency.  
✔ **Vulnerability Detection** – Compare plugin versions against a local vulnerability database.  
✔ **User Enumeration** – Discover usernames via the WordPress REST API.  
✔ **Flexible Output** – Export reports in **TXT**, **CSV**, or **JSON**.  
✔ **Plugin/CVE-Specific Scanning** – Focus scans on a given plugin slug or CVE ID.  
✔ **Professional Packaging** – Installable via `pip` and usable globally as `wphunter`.  

---

## 🚀 Installation  

We recommend installing WPHunter inside a **virtual environment**.  

```bash
# Clone the repository
git clone https://github.com/BharatCyberForce/wp-hunter.git
cd wp-hunter

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Requirements Install
pip3 install -r requirements.txt

#Run Tool
python3 wphunter.py

```
## 💻 Usage

### See available options:

```wphunter.py --help```
### Scan Single Target
```wphunter.py --url https://pkmkb.pk```
### Mass Scan
```wphunter.py --targets targets.txt --threads 200 --output output.txt```
### Mass Scan With Threads
```wphunter.py --targets targets.txt --threads 200 --output output.txt```
### User Enumurate
```wphunter.py --url https://pkmkb.pk --users```
### Specific Plugin Scan
```wphunter.py --url https://pkmkb.pk --plugin woocommerce```
### Specific CVE Scan
```wphunter.py --url https://pkmkb.pk --cve CVE-2021-34624```
### Save Vulnerable Sites In Vulnerable Plugin Name
```wphunter.py --targets targets.txt --save-by-plugin```


## ⚙️ Command-Line Options  

| Option               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--url <URL>`         | Scan a single WordPress site.                                               |
| `--targets <FILE>`    | File with multiple target URLs (one per line).                              |
| `--threads <INT>`     | Number of concurrent connections (default: `50`).                           |
| `--silent`            | Suppress all console output.                                                |
| `--verbose`           | Enable detailed logging, including debug messages.                          |
| `--users`             | Enumerate WordPress users via the REST API.                                |
| `--output <FILE>`     | Save scan report (`.txt`, `.csv`, `.json`).                                |
| `--timeout <INT>`     | HTTP request timeout in seconds (default: `5`).                             |
| `--retries <INT>`     | Retry attempts for failed requests (default: `2`).                          |
| `--plugin <SLUG>`     | Scan for vulnerabilities in a specific plugin slug (`woocommerce`).   |
| `--cve <CVE-ID>`      | Scan for a specific CVE ID (`CVE-2021-34624`).                        |
| `--save-by-plugin`    | Save a separate `.txt` file for each vulnerable plugin discovered.           |
| `--update`            | Check for updates and display upgrade instructions.                         |


## 📂 Output Formats  

WPHunter supports multiple output formats for flexible reporting:  

- **TXT** → Saves only vulnerable site URLs (minimal report).  
- **CSV** → Saves vulnerable sites with details (plugins, versions, CVEs).  
- **JSON** → Saves full structured scan data (recommended for automation & integrations).  

---

## 📸 Example Output  

Example of scanning a target:  

```bash
$ wphunter --url https://pkmkb.pk


│ Vulnerable Targets                                                                                                                                                             
│ └── Target: http://pkmkb.pk                                                                                                                                                  
│     ├── Plugin: revslider (Version: 6.6.20)                                                                                                                                    
│     │   ├── ID: CVE-2024-8107                                                                                                                                                  
│     │   ├── Type: CWE-79                                                                                                                                                      
│     │   ├── Severity: HIGH                                                                                                                                                     
│     │   ├── Affected Versions: <= 6.7.18                                                                                                                                       
│     │   └── Description: Stored XSS via SVG uploads (2024 disclosures).                                                                                                        
│     ├── Plugin: revslider (Version: 6.6.20)                                                                                                                                    
│     │   ├── ID: CVE-2024-34444                                                                                                                                                 
│     │   ├── Type: CWE-862                                                                                                                                                      
│     │   ├── Severity: HIGH                                                                                                                                                     
│     │   ├── Affected Versions: <= 6.7.0                                                                                                                                       
│     │   └── Description: Missing authorization in Slider Revolution (reported 2024).                                                                                           
│     ├── Plugin: revslider (Version: 6.6.20)                                                                                                                                    
│     │   ├── ID: CVE-2025-9217                                                                                                                                                  
│     │   ├── Type: CWE-22                                                                                                                                                       
│     │   ├── Severity: HIGH                                                                                                                                                     
│     │   ├── Affected Versions: <= 6.7.36                                                                                                                                       
│     │   └── Description: Path traversal in Slider Revolution via 'used_svg' and 'used_images' params (2025 disclosure).                                                        
│     ├── Plugin: elementor (Version: 3.18.3)                                                                                                                                    
│     │   ├── ID: CVE-2024-5416                                                                                                                                                  
│     │   ├── Type: CWE-79                                                                                                                                                       
│     │   ├── Severity: HIGH                                                                                                                                                     
│     │   ├── Affected Versions: <= 3.23.4                                                                                                                                       
│     │   └── Description: Stored XSS in multiple widgets' URL parameter in Elementor.                                                                                          
│     ├── Plugin: elementor (Version: 3.18.3)                                                                                                                                    
│     │   ├── ID: CVE-2024-37437                                                                                                                                                 
│     │   ├── Type: CWE-79                                                                                                                                                       
│     │   ├── Severity: HIGH                                                                                                                                                     
│     │   ├── Affected Versions: <= 3.22.1                                                                                                                                       
│     │   └── Description: Stored XSS in Elementor (reported July 2024).                                                                                                         
│     ├── Plugin: contact-form-7 (Version: 5.8.5)                                                                                                                                
│     │   ├── ID: CVE-2024-2242                                                                                                                                                  
│     │   ├── Type: CWE-79                                                                                                                                                       
│     │   ├── Severity: MEDIUM                                                                                                                                                  
│     │   ├── Affected Versions: <= 5.9                                                                                                                                          
│     │   └── Description: Reflected XSS via 'active-tab' parameter (fixed in 5.9.2+).                                                                                           
│     └── Plugin: contact-form-7 (Version: 5.8.5)                                                                                                                                
│         ├── ID: CVE-2024-4704                                                                                                                                                  
│         ├── Type: CWE-601                                                                                                                                                      
│         ├── Severity: MEDIUM                                                                                                                                                   
│         ├── Affected Versions: <= 5.9.4                                                                                                                                        
│         └── Description: Open redirect in Contact Form 7 before 5.9.5.  

```

## ⚠️ Disclaimer  

This project is for **educational and authorized penetration testing purposes only**.  
Unauthorized usage may violate laws.  

---

## ⭐ Support  

If you find **WPHunter** useful:  

- ⭐ **Star the repo on GitHub**  
- 🔗 **Share it with your community**  
- 💬 **Contribute or provide feedback**  

Your support helps the project grow! 🚀
