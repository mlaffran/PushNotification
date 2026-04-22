#!/usr/bin/env python3
"""
Script to update version headers in PushNotification workbench files.
Updates the header from 2026.04.07-V01 to 2026.04.09-V01.
"""

import os
import re
from pathlib import Path

# Files to update in PushNotification workbench
PUSH_NOTIFICATION_FILES = [
    "Init.py",
    "InitGui.py",
    "push_notification/__init__.py",
    "push_notification/commands.py",
    "push_notification/core.py",
    "push_notification/objects.py",
    "resources/generate_icons.py",
]

OLD_VERSION = "2026.04.07-V01"
NEW_VERSION = "2026.04.09-V01"

def update_file(filepath):
    """Update version in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update version - handle different spacing patterns
        updated_content = content
        
        # Pattern 1: Standard pattern with exact match
        standard_pattern = f'# * ## PushNotification FreeCAD WorkBench {OLD_VERSION} ##'
        if standard_pattern in content:
            updated_content = updated_content.replace(
                f'# * ## PushNotification FreeCAD WorkBench {OLD_VERSION} ##',
                f'# * ## PushNotification FreeCAD WorkBench {NEW_VERSION} ##'
            )
        
        # Pattern 2: With extra spaces after
        pattern_with_spaces = f'# \\* ## PushNotification FreeCAD WorkBench {OLD_VERSION} ##\\s*\\*'
        if re.search(pattern_with_spaces, content):
            updated_content = re.sub(
                pattern_with_spaces,
                f'# * ## PushNotification FreeCAD WorkBench {NEW_VERSION} ##                    *',
                updated_content
            )
        
        # Pattern 3: Using regex replacement for any version
        updated_content = re.sub(
            f'# \\* ## PushNotification FreeCAD WorkBench {re.escape(OLD_VERSION)} ##',
            f'# * ## PushNotification FreeCAD WorkBench {NEW_VERSION} ##',
            updated_content
        )
        
        # Also check for "2026.04.07-V01" anywhere else in the file
        if OLD_VERSION in updated_content:
            updated_content = updated_content.replace(OLD_VERSION, NEW_VERSION)
        
        if updated_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True, "Updated"
        else:
            # Check if already has new version
            if NEW_VERSION in content:
                return False, f"Already has {NEW_VERSION}"
            else:
                return False, "No changes needed"
                
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    cwd = Path(".")
    print(f"Working directory: {cwd.absolute()}")
    print(f"Updating headers from {OLD_VERSION} to {NEW_VERSION}")
    print("=" * 60)
    
    updated_count = 0
    for filename in PUSH_NOTIFICATION_FILES:
        filepath = cwd / filename
        if not filepath.exists():
            print(f"  ⚠️  {filename}: File not found")
            continue
        
        updated, message = update_file(filepath)
        status = "✅" if updated else "ℹ️ "
        if updated:
            updated_count += 1
        print(f"  {status} {filename}: {message}")
    
    print("=" * 60)
    print(f"Updated {updated_count} out of {len(PUSH_NOTIFICATION_FILES)} files")

if __name__ == "__main__":
    main()