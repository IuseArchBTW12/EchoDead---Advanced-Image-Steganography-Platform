#!/usr/bin/env python3
"""
Advanced cryptography and obfuscation module for payload protection
"""

import hashlib
import os
import base64
import zlib

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class PayloadEncryption:
    """Handles encryption, compression, and obfuscation of payloads"""
    
    def __init__(self, password=None):
        self.password = password
        self.salt = os.urandom(32)
    
    def derive_key(self, password, salt):
        """Derive encryption key from password"""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple XOR
            return hashlib.sha256(password.encode() + salt).digest()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data, password=None):
        """
        Encrypt data with optional password
        Returns: (salt, encrypted_data)
        """
        if password is None and self.password is None:
            # No encryption, just return data
            return None, data
        
        pwd = password or self.password
        
        if not CRYPTO_AVAILABLE:
            # Fallback to XOR encryption
            return self._xor_encrypt(data, pwd)
        
        # Generate salt
        salt = os.urandom(32)
        
        # Derive key
        key = self.derive_key(pwd, salt)
        
        # Encrypt
        f = Fernet(key)
        encrypted = f.encrypt(data)
        
        return salt, encrypted
    
    def decrypt_data(self, encrypted_data, salt, password=None):
        """Decrypt data with password"""
        if salt is None:
            # No encryption was used
            return encrypted_data
        
        pwd = password or self.password
        
        if not CRYPTO_AVAILABLE:
            # Fallback to XOR decryption
            return self._xor_decrypt(encrypted_data, pwd, salt)
        
        # Derive key
        key = self.derive_key(pwd, salt)
        
        # Decrypt
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data)
        
        return decrypted
    
    def compress_data(self, data):
        """Compress data using zlib"""
        return zlib.compress(data, level=9)
    
    def decompress_data(self, data):
        """Decompress zlib data"""
        return zlib.decompress(data)
    
    def _xor_encrypt(self, data, password):
        """Simple XOR encryption as fallback"""
        salt = os.urandom(16)
        key = hashlib.sha256(password.encode() + salt).digest()
        
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        return salt, bytes(encrypted)
    
    def _xor_decrypt(self, data, password, salt):
        """Simple XOR decryption as fallback"""
        key = hashlib.sha256(password.encode() + salt).digest()
        
        decrypted = bytearray()
        for i, byte in enumerate(data):
            decrypted.append(byte ^ key[i % len(key)])
        
        return bytes(decrypted)
    
    def obfuscate_filename(self, original_name):
        """Generate obfuscated but plausible filename"""
        common_names = [
            "document.pdf", "invoice.xlsx", "report.docx", "photo.jpg",
            "backup.zip", "config.json", "data.csv", "notes.txt",
            "presentation.pptx", "screenshot.png", "readme.md"
        ]
        
        # Hash the original name to pick a consistent fake name
        hash_val = int(hashlib.md5(original_name.encode()).hexdigest(), 16)
        return common_names[hash_val % len(common_names)]

class StealthFeatures:
    """Advanced anti-forensics and stealth capabilities"""
    
    @staticmethod
    def randomize_lsb_pattern(pixels_total):
        """Generate random LSB embedding pattern for stealth"""
        # Instead of sequential embedding, use pseudo-random positions
        import random
        positions = list(range(pixels_total * 3))  # All RGB channels
        random.shuffle(positions)
        return positions
    
    @staticmethod
    def add_noise_layer(image_data):
        """Add imperceptible noise to avoid statistical detection"""
        # This would add random LSB changes to unused pixels
        pass
    
    @staticmethod
    def strip_metadata(image_path):
        """Remove EXIF and metadata from image"""
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            # Remove metadata
            data = list(img.getdata())
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(data)
            
            return image_without_exif
        except:
            return None
    
    @staticmethod
    def generate_cover_story():
        """Generate plausible explanation for image"""
        stories = [
            "Family vacation photos from summer 2025",
            "Work project screenshots for documentation",
            "Stock photos for website redesign",
            "Photography portfolio backup",
            "Scanned documents for tax records",
            "Recipe collection screenshots",
            "Memes and funny pictures collection"
        ]
        
        import random
        return random.choice(stories)

class AntiAnalysis:
    """Features to evade detection and analysis"""
    
    @staticmethod
    def check_sandbox_environment():
        """Detect if running in analysis environment"""
        indicators = []
        
        # Check for common VM/sandbox indicators
        try:
            import platform
            import psutil
            
            # Check RAM (VMs usually have low RAM)
            if psutil.virtual_memory().total < 4 * 1024 * 1024 * 1024:  # < 4GB
                indicators.append("low_ram")
            
            # Check CPU cores
            if psutil.cpu_count() < 2:
                indicators.append("low_cpu")
            
            # Check username
            suspicious_users = ['sandbox', 'malware', 'virus', 'test', 'user']
            import os
            if any(s in os.getlogin().lower() for s in suspicious_users):
                indicators.append("suspicious_username")
            
        except:
            pass
        
        return indicators
    
    @staticmethod
    def delay_execution(seconds):
        """Sleep to evade time-based detection"""
        import time
        time.sleep(seconds)
    
    @staticmethod
    def check_debugger():
        """Detect if being debugged"""
        import sys
        return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def create_encrypted_payload(data, password=None, compress=True):
    """
    Complete payload preparation pipeline
    - Optional compression
    - Optional encryption
    - Metadata prepending
    """
    encryptor = PayloadEncryption(password)
    
    # Compress if requested
    if compress:
        data = encryptor.compress_data(data)
        flags = b'\x01'  # Flag: compressed
    else:
        flags = b'\x00'  # Flag: not compressed
    
    # Encrypt if password provided
    if password:
        salt, encrypted_data = encryptor.encrypt_data(data, password)
        flags = bytes([flags[0] | 0x02])  # Set encryption flag
        
        # Prepend: flags + salt + data
        final_data = flags + salt + encrypted_data
    else:
        # Prepend: flags + data
        final_data = flags + data
    
    return final_data

def extract_encrypted_payload(data, password=None):
    """
    Extract and decrypt payload
    """
    # Read flags
    flags = data[0]
    compressed = bool(flags & 0x01)
    encrypted = bool(flags & 0x02)
    
    offset = 1
    
    # Extract salt if encrypted
    if encrypted:
        salt = data[offset:offset + 32]
        offset += 32
        payload_data = data[offset:]
        
        # Decrypt
        encryptor = PayloadEncryption(password)
        payload_data = encryptor.decrypt_data(payload_data, salt, password)
    else:
        payload_data = data[offset:]
    
    # Decompress if needed
    if compressed:
        encryptor = PayloadEncryption()
        payload_data = encryptor.decompress_data(payload_data)
    
    return payload_data

# Test
if __name__ == "__main__":
    print("Testing encryption module...")
    
    # Test encryption
    test_data = b"This is a secret message!"
    password = "super_secret_password"
    
    encryptor = PayloadEncryption(password)
    
    # Encrypt
    salt, encrypted = encryptor.encrypt_data(test_data, password)
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    
    # Decrypt
    decrypted = encryptor.decrypt_data(encrypted, salt, password)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {decrypted == test_data}")
    
    # Test compression
    compressed = encryptor.compress_data(test_data * 100)
    decompressed = encryptor.decompress_data(compressed)
    print(f"\nOriginal size: {len(test_data * 100)} bytes")
    print(f"Compressed: {len(compressed)} bytes")
    print(f"Ratio: {len(compressed) / len(test_data * 100) * 100:.1f}%")
    
    # Test full pipeline
    prepared = create_encrypted_payload(test_data * 10, password, compress=True)
    extracted = extract_encrypted_payload(prepared, password)
    print(f"\nFull pipeline test: {extracted == test_data * 10}")
