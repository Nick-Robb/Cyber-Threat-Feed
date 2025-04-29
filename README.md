# 🛰️ Cyber Threat Intel Bot

An **automated threat intelligence feed system** designed to fetch and log the latest cybersecurity news and CVEs — without human intervention.

---

## 📌 Project Summary

This project demonstrates **real-world automation of threat intelligence operations** using Python. It pulls cybersecurity news from trusted sources and fetches the latest Common Vulnerabilities and Exposures (CVEs) from the NVD API. All data is automatically pushed to a Google Sheet and updated on a schedule.

> Built to showcase practical automation skills in threat intelligence, API handling, and system scheduling.

---

## ⚙️ Core Features

- 🔍 **Scrapes cybersecurity news headlines** from top industry sites  
- 🧠 **Fetches recent CVEs** from the National Vulnerability Database  
- 📊 **Automatically updates a Google Sheet** with live threat data  
- 🕓 **Runs twice daily** using Windows Task Scheduler  
- 🔐 Secure configuration using external credential files

---

## 🚀 Why This Matters

Most SOCs and analysts rely on manual threat feed review — this bot eliminates that inefficiency. It's a **proof of concept** for building internal automation tools to support security operations.

---

## 🧰 Tech Stack

- Python 3  
- Google Sheets API  
- NVD (National Vulnerability Database) API  
- BeautifulSoup & Requests (for scraping)  
- Windows Task Scheduler (for automation)

---

## 💡 Key Learning & Security Concepts

- Threat intelligence automation  
- API integration and authentication  
- Scheduling and persistent data sync  
- Securing credentials using `.env` files (post-remediation)

---

## 📁 File Structure (Safe Version)

```plaintext
├── cyber_threat_feed.py         # Main script
├── run_cyber_feed.bat           # Simple execution wrapper
├── .gitignore                   # Ensures sensitive data is excluded
├── README.md                    # This file
