#!/usr/bin/env python3
"""
Script to fix escaped newlines in workplan-execution.v3.json
This script replaces \\n with actual newlines in ALL cat heredocs
"""

import json
import re

def fix_escaped_newlines():
    """Fix escaped newlines in ALL cat heredocs"""
    
    # Read the workplan file
    with open('workplan-execution.v3.json', 'r') as f:
        content = f.read()
    
    print("Original file size:", len(content))
    
    # Count original escaped newlines
    original_count = content.count("\\n")
    print(f"Found {original_count} escaped newlines (\\n)")
    
    # Find all lines that contain cat commands with heredocs
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'cat >' in line and '<<' in line and '\\n' in line:
            # This is a cat command with escaped newlines
            print(f"Fixing line {i+1}: {line[:100]}...")
            # Replace \\n with actual newlines
            fixed_line = line.replace("\\n", "\n")
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    # Rejoin the lines
    fixed_content = '\n'.join(fixed_lines)
    
    # Count remaining escaped newlines
    remaining_count = fixed_content.count("\\n")
    print(f"Remaining escaped newlines: {remaining_count}")
    print(f"Fixed {original_count - remaining_count} escaped newlines")
    
    # Write the fixed content
    with open('workplan-execution.v3.json', 'w') as f:
        f.write(fixed_content)
    
    print("File updated successfully")
    
    # Validate JSON
    try:
        with open('workplan-execution.v3.json', 'r') as f:
            json.load(f)
        print("JSON validation passed")
    except json.JSONDecodeError as e:
        print(f"JSON validation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_escaped_newlines()
