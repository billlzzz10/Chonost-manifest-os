#!/usr/bin/env python3
"""
Ultimate Trailing Spaces Fixer.
This script fixes all trailing spaces in .md files.
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple

def find_markdown_files() -> List[str]:
    """
    Finds all Markdown files in the current directory and its subdirectories.

    Returns:
        List[str]: A list of paths to the Markdown files.
    """
    md_files = []
    for pattern in ["**/*.md", "**/*.mdc"]:
        md_files.extend(glob.glob(pattern, recursive=True))
    return md_files

def fix_trailing_spaces(content: str) -> str:
    """
    Fixes all trailing spaces in the given content.

    Args:
        content (str): The content to fix.

    Returns:
        str: The content with all trailing spaces removed.
    """
    # Fix trailing spaces and tabs on all lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing spaces and tabs
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
    
    # Join the lines back together and add a single newline at the end
    return '\n'.join(fixed_lines) + '\n'

def fix_file(filepath: str) -> bool:
    """
    Fixes a single Markdown file.

    Args:
        filepath (str): The path to the Markdown file.

    Returns:
        bool: True if the file was fixed, False otherwise.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed_content = fix_trailing_spaces(content)
        
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed trailing spaces: {filepath}")
            return True
        else:
            print(f"✅ No trailing spaces: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main() -> None:
    """
    The main function of the script.

    This function finds all Markdown files in the project, fixes the
    trailing spaces in them, and then prints a summary of the results.
    """
    print("🧹 Ultimate Trailing Spaces Fixer...")
    print("=" * 50)
    
    md_files = find_markdown_files()
    print(f"📁 Found {len(md_files)} Markdown files")
    
    fixed_count = 0
    for filepath in md_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Total files: {len(md_files)}")
    print(f"   Files fixed: {fixed_count}")
    
    if fixed_count > 0:
        print("\n🎉 All trailing spaces fixed successfully!")
        print("📝 No more trailing spaces!")
    else:
        print("\n✅ All files were already clean!")

if __name__ == "__main__":
    main()
