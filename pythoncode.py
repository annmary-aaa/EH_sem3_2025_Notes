#!/usr/bin/env python3

import subprocess
import time
import re

CHECK_INTERVAL = 30  # in seconds
OUTPUT_LOG = "/home/kali/Documents/sudo_monitor.log"  # Change path if needed
already_seen = set()

def extract_info(line):
    # Try to extract time, user, and status
    timestamp_match = re.match(r'^\w{3} \d{1,2} \d{2}:\d{2}:\d{2}', line)
    user_match = re.search(r'by\s+(\w+)\(uid=0\)', line)
    status = "SUCCESS" if "session opened" in line else "FAILURE" if "authentication failure" in line else "UNKNOWN"

    timestamp = timestamp_match.group(0) if timestamp_match else "UNKNOWN_TIME"
    user = user_match.group(1) if user_match else "UNKNOWN_USER"

    return f"{timestamp} | USER: {user} | STATUS: {status}"

def monitor():
    print(f"[+] Monitoring started (journalctl mode)")
    while True:
        try:
            # Get last 20 lines of sudo-related logs
            result = subprocess.run(
                ["journalctl", "-n", "20", "_COMM=sudo", "--no-pager"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            lines = result.stdout.strip().split("\n")

            with open(OUTPUT_LOG, "a") as out:
                for line in lines:
                    if "sudo" in line and line not in already_seen:
                        already_seen.add(line)
                        parsed = extract_info(line)
                        print("[LOG]", parsed)
                        out.write(parsed + "\n")

        except Exception as e:
            print("[-] Error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()










