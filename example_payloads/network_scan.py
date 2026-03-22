#!/usr/bin/env python3
"""
Network Scanner Payload - Scans local network for active hosts
"""

import socket
import subprocess
import platform

def ping_host(host):
    """Ping a single host"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '1000', host]
    
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        return result.returncode == 0
    except:
        return False

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

print("=" * 60)
print("NETWORK SCANNER PAYLOAD")
print("=" * 60)

local_ip = get_local_ip()
print(f"\nLocal IP: {local_ip}")

# Extract network prefix (e.g., 192.168.1)
network_prefix = '.'.join(local_ip.split('.')[:-1])
print(f"Scanning network: {network_prefix}.0/24")
print("\nActive hosts:")

active_hosts = []
for i in range(1, 255):
    host = f"{network_prefix}.{i}"
    if ping_host(host):
        active_hosts.append(host)
        print(f"  ✓ {host}")

print(f"\nTotal active hosts: {len(active_hosts)}")
print("=" * 60)
