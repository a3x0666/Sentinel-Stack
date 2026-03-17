# SSH Intrusion Detection & Automated Response System

A real-time Python-based security automation tool that monitors SSH login activity, detects brute-force attacks, and automatically blocks malicious IPs using firewall rules.

---

## Overview

This project simulates a lightweight SOC (Security Operations Center) workflow by combining:

* Real-time log monitoring
* Threat detection (brute-force attacks)
* Automated response (IP blocking)
* Threat intelligence (GeoIP lookup)
* Alerting system (Discord integration)
* Persistent logging for analysis

---

## Features

* Real-time monitoring of `/var/log/auth.log`
* Brute-force detection using time-based thresholds
* Automatic IP blocking via iptables
* GeoIP enrichment (country and ISP of attacker)
* Discord alerts with structured embeds
* JSON logging for attack tracking
* Auto-unblock system after timeout
* Whitelist support to prevent self-blocking

---

## Detection Logic

* Tracks login attempts per IP
* Applies a time window (e.g., 5 attempts in 60 seconds)
* Flags and blocks IPs exceeding threshold

---

## Tech Stack

* Python 3
* Linux (Ubuntu/Kali recommended)
* iptables (firewall)
* Discord Webhooks
* IP-API (GeoIP lookup)

---

## Installation

```bash
git clone https://github.com/yourusername/ssh-intrusion-detector.git
cd ssh-intrusion-detector

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file:

```env
DISCORD_WEBHOOK=your_webhook_url
```

Update whitelist in script:

```python
WHITELIST = ["your_ip"]
```

---

## Usage

Run the script with elevated privileges:

```bash
sudo python3 main.py
```

---

## Disclaimer

This tool modifies firewall rules and should be used in a controlled environment. Misconfiguration may result in loss of SSH access.

---

## Future Improvements

* Web dashboard (Flask with charts)
* Integration with SIEM tools (Wazuh / ELK)
* Advanced anomaly detection
* Multi-log monitoring (sudo, authentication anomalies)

---

## Demo

(Add screenshots here)

---

## Author

Abhay Aneesh
Cybersecurity Enthusiast | SOC Automation | Threat Detection
