#!/usr/bin/env python3
"""
Creates a test image for Steganography
"""
from PIL import Image

# Create a simple test image
img = Image.new('RGB', (800, 600), color=(73, 109, 137))
img.save('test_image.png')
print("✓ Created test_image.png (800x600)")
print(f"  Capacity: {(800 * 600 * 3) // 8} bytes (~{(800 * 600 * 3) // 8 // 1024} KB)")
