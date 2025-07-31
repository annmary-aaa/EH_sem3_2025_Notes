# Admin Privilege Monitoring Report

## Methodology
To monitor admin (sudo) access on a Kali Linux system, I:
1. Verified logging files (`/var/log/auth.log`) and found they were not present.
2. Identified systemd journal logging (`journalctl`) as the alternative.
3. Wrote a Python script that:
   - Checks for sudo events using `journalctl` every 30 seconds.
   - Logs each sudo usage attempt (success/failure) to a custom file with user and timestamp.

## Screenshot
<img width="429" height="552" alt="Screenshot 2025-07-31 133324" src="https://github.com/user-attachments/assets/3a32894b-5aac-4ef9-89e7-eb8b11bbb09b" />


## Findings
- System uses `journalctl` instead of traditional log files.
- Both successful and failed sudo attempts are traceable.
- Logs provide exact usernames and timestamps.

**Example logs:**
Jul 31 11:00:23 | USER: kali | STATUS: SUCCESS
Jul 31 11:05:10 | USER: kali | STATUS: FAILURE

## Conclusion
- Monitoring admin access is essential for system integrity and detecting potential insider threats.
- `journalctl` offers a more robust and modern logging approach.
- This system is expandable to support alerts or reporting features.

## Python Script: `sudo_monitor.py`
```python
#!/usr/bin/env python3
import subprocess, time, re

CHECK_INTERVAL = 30
OUTPUT_LOG = "/home/kali/Documents/sudo_monitor.log"
already_seen = set()

def extract_info(line):
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
            result = subprocess.run(
                ["journalctl", "-n", "20", "_COMM=sudo", "--no-pager"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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




