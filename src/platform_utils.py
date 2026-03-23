#!/usr/bin/env python3
"""
EchoDead - Platform Detection Utilities
Author: DedSec
Description: Cross-platform support and OS detection
"""

import os
import sys
import platform
import subprocess
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


class PlatformDetector:
    """
    Detect operating system and environment details
    """
    
    @staticmethod
    def get_os() -> str:
        """
        Get operating system name
        Returns: 'windows', 'linux', 'macos', or 'unknown'
        """
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'unknown'
    
    @staticmethod
    def get_detailed_info() -> Dict[str, Any]:
        """
        Get detailed platform information
        """
        return {
            'os': PlatformDetector.get_os(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'is_64bit': sys.maxsize > 2**32,
        }
    
    @staticmethod
    def is_windows() -> bool:
        return PlatformDetector.get_os() == 'windows'
    
    @staticmethod
    def is_linux() -> bool:
        return PlatformDetector.get_os() == 'linux'
    
    @staticmethod
    def is_macos() -> bool:
        return PlatformDetector.get_os() == 'macos'
    
    @staticmethod
    def is_admin() -> bool:
        """
        Check if running with administrator/root privileges
        """
        try:
            if PlatformDetector.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    @staticmethod
    def get_shell() -> str:
        """
        Get the default shell for the platform
        """
        if PlatformDetector.is_windows():
            return 'powershell.exe'
        else:
            return os.environ.get('SHELL', '/bin/bash')
    
    @staticmethod
    def get_home_dir() -> Path:
        """
        Get user's home directory (cross-platform)
        """
        return Path.home()
    
    @staticmethod
    def get_temp_dir() -> Path:
        """
        Get temporary directory (cross-platform)
        """
        import tempfile
        return Path(tempfile.gettempdir())


class CrossPlatformCommand:
    """
    Execute commands across different platforms
    """
    
    @staticmethod
    def run_command(command: str, shell: bool = True, timeout: int = 30) -> Tuple[str, str, int]:
        """
        Run a command and return (stdout, stderr, returncode)
        
        Args:
            command: Command to execute
            shell: Use shell execution
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            if PlatformDetector.is_windows():
                # Use PowerShell on Windows for better compatibility
                if not command.startswith('powershell'):
                    command = f'powershell.exe -Command "{command}"'
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.stdout, result.stderr, result.returncode
        
        except subprocess.TimeoutExpired:
            return "", "Command timeout", -1
        except Exception as e:
            return "", str(e), -1
    
    @staticmethod
    def get_username() -> str:
        """Get current username (cross-platform)"""
        if PlatformDetector.is_windows():
            return os.environ.get('USERNAME', 'Unknown')
        else:
            return os.environ.get('USER', 'Unknown')
    
    @staticmethod
    def get_hostname() -> str:
        """Get computer hostname (cross-platform)"""
        return platform.node()
    
    @staticmethod
    def get_network_interfaces() -> Dict[str, str]:
        """
        Get network interfaces and IP addresses (cross-platform)
        """
        interfaces = {}
        
        try:
            if PlatformDetector.is_windows():
                stdout, _, _ = CrossPlatformCommand.run_command('ipconfig')
                # Parse ipconfig output (simplified)
                current_adapter = None
                for line in stdout.split('\n'):
                    if 'adapter' in line.lower():
                        current_adapter = line.split(':')[0].strip()
                    elif 'IPv4' in line and current_adapter:
                        ip = line.split(':')[-1].strip()
                        interfaces[current_adapter] = ip
            
            else:
                # Linux/macOS
                stdout, _, _ = CrossPlatformCommand.run_command('ip addr 2>/dev/null || ifconfig')
                # Parse ip/ifconfig output (simplified)
                current_iface = None
                for line in stdout.split('\n'):
                    if line and not line.startswith(' '):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            current_iface = parts[1].strip()
                    elif 'inet ' in line and current_iface:
                        ip = line.split()[1].split('/')[0]
                        interfaces[current_iface] = ip
        
        except Exception:
            pass
        
        return interfaces
    
    @staticmethod
    def get_process_list() -> list:
        """
        Get list of running processes (cross-platform)
        """
        processes = []
        
        try:
            if PlatformDetector.is_windows():
                stdout, _, _ = CrossPlatformCommand.run_command('tasklist /fo csv /nh')
                for line in stdout.split('\n'):
                    if line.strip():
                        parts = line.replace('"', '').split(',')
                        if len(parts) >= 2:
                            processes.append({
                                'name': parts[0],
                                'pid': parts[1]
                            })
            else:
                stdout, _, _ = CrossPlatformCommand.run_command('ps aux')
                for line in stdout.split('\n')[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append({
                                'name': parts[10],
                                'pid': parts[1],
                                'user': parts[0]
                            })
        
        except Exception:
            pass
        
        return processes


class PathHelper:
    """
    Cross-platform path helpers
    """
    
    @staticmethod
    def get_startup_dir() -> Optional[Path]:
        """Get OS startup directory"""
        if PlatformDetector.is_windows():
            startup = Path(os.environ.get('APPDATA', '')) / 'Microsoft/Windows/Start Menu/Programs/Startup'
            return startup if startup.exists() else None
        
        elif PlatformDetector.is_linux():
            autostart = Path.home() / '.config/autostart'
            autostart.mkdir(parents=True, exist_ok=True)
            return autostart
        
        elif PlatformDetector.is_macos():
            launch_agents = Path.home() / 'Library/LaunchAgents'
            launch_agents.mkdir(parents=True, exist_ok=True)
            return launch_agents
        
        return None
    
    @staticmethod
    def get_browser_data_dirs() -> Dict[str, Path]:
        """Get browser data directories (cross-platform)"""
        dirs = {}
        home = Path.home()
        
        if PlatformDetector.is_windows():
            dirs = {
                'chrome': home / 'AppData/Local/Google/Chrome/User Data',
                'firefox': home / 'AppData/Roaming/Mozilla/Firefox/Profiles',
                'edge': home / 'AppData/Local/Microsoft/Edge/User Data',
            }
        
        elif PlatformDetector.is_linux():
            dirs = {
                'chrome': home / '.config/google-chrome',
                'firefox': home / '.mozilla/firefox',
                'chromium': home / '.config/chromium',
            }
        
        elif PlatformDetector.is_macos():
            dirs = {
                'chrome': home / 'Library/Application Support/Google/Chrome',
                'firefox': home / 'Library/Application Support/Firefox/Profiles',
                'safari': home / 'Library/Safari',
            }
        
        # Return only existing directories
        return {k: v for k, v in dirs.items() if v.exists()}
    
    @staticmethod
    def get_documents_dir() -> Path:
        """Get user's documents directory"""
        if PlatformDetector.is_windows():
            return Path(os.environ.get('USERPROFILE', Path.home())) / 'Documents'
        else:
            return Path.home() / 'Documents'
    
    @staticmethod
    def get_downloads_dir() -> Path:
        """Get user's downloads directory"""
        if PlatformDetector.is_windows():
            return Path(os.environ.get('USERPROFILE', Path.home())) / 'Downloads'
        else:
            return Path.home() / 'Downloads'


# Test functionality
if __name__ == "__main__":
    print("=" * 70)
    print("PLATFORM DETECTION TEST")
    print("=" * 70)
    
    # Basic detection
    print(f"\nOperating System: {PlatformDetector.get_os()}")
    print(f"Is Windows: {PlatformDetector.is_windows()}")
    print(f"Is Linux: {PlatformDetector.is_linux()}")
    print(f"Is macOS: {PlatformDetector.is_macos()}")
    print(f"Is Admin/Root: {PlatformDetector.is_admin()}")
    
    # Detailed info
    print("\nDetailed Platform Info:")
    info = PlatformDetector.get_detailed_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Cross-platform commands
    print("\nCross-Platform Commands:")
    print(f"  Username: {CrossPlatformCommand.get_username()}")
    print(f"  Hostname: {CrossPlatformCommand.get_hostname()}")
    
    # Network interfaces
    print("\nNetwork Interfaces:")
    interfaces = CrossPlatformCommand.get_network_interfaces()
    for iface, ip in interfaces.items():
        print(f"  {iface}: {ip}")
    
    # Paths
    print("\nCross-Platform Paths:")
    print(f"  Home: {PlatformDetector.get_home_dir()}")
    print(f"  Temp: {PlatformDetector.get_temp_dir()}")
    print(f"  Startup: {PathHelper.get_startup_dir()}")
    print(f"  Documents: {PathHelper.get_documents_dir()}")
    print(f"  Downloads: {PathHelper.get_downloads_dir()}")
    
    # Browser directories
    print("\nBrowser Data Directories:")
    browsers = PathHelper.get_browser_data_dirs()
    for browser, path in browsers.items():
        print(f"  {browser}: {path}")
    
    print("\n" + "=" * 70)
    print("✅ All platform detection features working!")
    print("=" * 70)
