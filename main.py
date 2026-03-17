import time
import re
import subprocess
import requests
import json
import os

#cfg

LOG_FILE = "/var/log/auth.log"

WEBHOOK_URL = <you webhook url here>

TIME_WINDOW = 60          # seconds
MAX_ATTEMPTS = 5
BLOCK_DURATION = 600      # seconds (10 mins)

WHITELIST = ["127.0.0.1", "YOUR_IP"]

LOG_JSON = "attack_log.json"

#storage

attempts = {}
blocked_ips = {}

#discord

def send_discord_alert(title, message, color=16711680):
    data = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color
            }
        ]
    }

    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"[ERROR] Discord alert failed: {e}")

#geoIP

def get_geoip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if res["status"] == "success":
            return f"{res['country']} | {res['isp']}"
    except:
        pass
    return "Unknown"

#logging

def log_event(data):
    try:
        if not os.path.exists(LOG_JSON):
            with open(LOG_JSON, "w") as f:
                json.dump([], f)

        with open(LOG_JSON, "r+") as f:
            logs = json.load(f)
            logs.append(data)
            f.seek(0)
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Logging failed: {e}")

#firewall

def block_ip(ip):

    if ip in blocked_ips or ip in WHITELIST:
        return

    print(f"[ACTION] Blocking IP: {ip}")

    subprocess.run([
        "sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"
    ])

    blocked_ips[ip] = time.time()

    geo = get_geoip(ip)

    send_discord_alert(
        "🚫 IP BLOCKED",
        f"IP: `{ip}`\nGeo: {geo}\nReason: SSH brute-force",
        16711680
    )

    log_event({
        "event": "blocked",
        "ip": ip,
        "geo": geo,
        "time": time.ctime()
    })


def unblock_ips():
    current_time = time.time()

    for ip in list(blocked_ips.keys()):
        if current_time - blocked_ips[ip] > BLOCK_DURATION:

            print(f"[ACTION] Unblocking IP: {ip}")

            subprocess.run([
                "sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"
            ])

            del blocked_ips[ip]

            send_discord_alert(
                "🔓 IP UNBLOCKED",
                f"IP: `{ip}`\nUnblocked after timeout",
                65280
            )

#detection

def process_line(line):

    if "Invalid user" in line or "Failed password" in line:

        ip_match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)

        if ip_match:
            ip = ip_match.group(1)

            if ip in WHITELIST:
                return

            current_time = time.time()

            if ip not in attempts:
                attempts[ip] = []

            attempts[ip].append(current_time)

            # keep only recent attempts
            attempts[ip] = [
                t for t in attempts[ip]
                if current_time - t <= TIME_WINDOW
            ]

            count = len(attempts[ip])

            print(f"[!] {ip} attempts: {count}")

            if count >= MAX_ATTEMPTS:

                geo = get_geoip(ip)

                send_discord_alert(
                    "⚠️ BRUTE FORCE DETECTED",
                    f"IP: `{ip}`\nAttempts: {count} in {TIME_WINDOW}s\nGeo: {geo}",
                    16753920
                )

                log_event({
                    "event": "bruteforce",
                    "ip": ip,
                    "attempts": count,
                    "geo": geo,
                    "time": time.ctime()
                })

                block_ip(ip)

#main

def monitor():

    with open(LOG_FILE, "r") as f:

        f.seek(0, 2)

        while True:

            line = f.readline()

            if not line:
                unblock_ips()
                time.sleep(1)
                continue

            process_line(line)


if __name__ == "__main__":
    print("[STARTED] SSH Intrusion Detection System Running...")
    monitor()
