#!/usr/bin/env python3
"""
Screenshot Capture
Takes a screenshot and saves it (optionally sends to Discord)
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def take_screenshot(filename=None):
    """Take a screenshot using PIL"""
    try:
        from PIL import ImageGrab
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Capture screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        
        return filename, screenshot.size
        
    except ImportError:
        print("Error: PIL/Pillow not installed")
        print("Install with: pip install pillow")
        return None, None
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None, None

def main():
    print("=" * 60)
    print("SCREENSHOT CAPTURE")
    print("=" * 60)
    
    print("\nCapturing screenshot...")
    
    filename, size = take_screenshot()
    
    if filename:
        print(f"✓ Screenshot saved: {filename}")
        print(f"  Resolution: {size[0]}x{size[1]}")
        
        if WEBHOOK_AVAILABLE:
            print("\nSending notification to Discord...")
            data = {
                "Filename": filename,
                "Resolution": f"{size[0]}x{size[1]}",
                "Size": f"{os.path.getsize(filename) // 1024} KB",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            success = send_to_discord("Screenshot Captured", data)
            
            if success:
                print("✓ Notification sent to Discord")
            else:
                print("✗ Failed to send to Discord")
        else:
            print("\n⚠️  Webhook not available - screenshot saved locally only")
    else:
        print("✗ Failed to capture screenshot")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
