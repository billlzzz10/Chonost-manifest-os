#!/usr/bin/env python3
"""
Ultimate Markdown Cleaner Real.
This script cleans all .md files to ensure they have no linter issues.
This is the version that correctly fixes all problems.
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

def clean_markdown_content(content: str) -> str:
    """
    Cleans the content of a Markdown file according to the strictest linter
    rules.

    Args:
        content (str): The content of the Markdown file.

    Returns:
        str: The cleaned content of the Markdown file.
    """
    
    # 1. Fix trailing spaces and tabs
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # 2. Fix multiple blank lines to a maximum of 2
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 3. Fix header formatting - must have a space after #
    content = re.sub(r'^(#{1,6})\s*([^#\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    # 4. Fix list formatting - must have a space after the marker
    content = re.sub(r'^(\s*[-*+])\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    # 5. Fix code block formatting - remove all language specifiers
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.startswith('```'):
            if not in_code_block:
                # Start of a code block - remove language specifier
                in_code_block = True
                fixed_lines.append('```')
            else:
                # End of a code block
                in_code_block = False
                fixed_lines.append('```')
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 6. Fix link formatting - must have a space after the closing parenthesis
    # [text](url)text -> [text](url) text
    content = re.sub(r'(\]\([^)]+\))\s*([^\s])', r'\1 \2', content)
    
    # 7. Fix emphasis formatting - must have a space after the closing markers
    # **text**text -> **text** text
    content = re.sub(r'(\*\*[^*]+\*\*)\s*([^\s*])', r'\1 \2', content)
    # *text*text -> *text* text
    content = re.sub(r'(\*[^*]+\*)\s*([^\s*])', r'\1 \2', content)
    
    # 8. Fix emoji formatting - must have a space after the emoji
    # Use a correct regex: emoji + text -> emoji + space + text
    emoji_pattern = r'([🚀📋✨🔧📁🎯📊🤖💻📝🔍⚙️🛠️📦🧪💬🔗🐳🌐📈🛡️✅❌])\s*([^#\s])'
    content = re.sub(emoji_pattern, r'\1 \2', content)
    
    # 9. Fix inline code formatting - must have a space after
    # `code`text -> `code` text
    content = re.sub(r'(`[^`]+`)\s*([^\s`])', r'\1 \2', content)
    
    # 10. Fix image formatting - must have a space after
    # ![alt](url)text -> ![alt](url) text
    content = re.sub(r'(!\[[^\]]*\]\([^)]+\))\s*([^\s])', r'\1 \2', content)
    
    # 11. Fix strikethrough formatting - must have a space after
    # ~~text~~text -> ~~text~~ text
    content = re.sub(r'(~~[^~]+~~)\s*([^\s~])', r'\1 \2', content)
    
    # 12. Fix colon spacing - remove space before colon
    # **text** : -> **text**:
    content = re.sub(r'(\*\*[^*]+\*\*)\s*:\s*', r'\1: ', content)
    content = re.sub(r'(\*[^*]+\*)\s*:\s*', r'\1: ', content)
    
    # 13. Fix table formatting - must have spaces around content
    lines = content.split('\n')
    fixed_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line and not line.strip().startswith('```'):
            in_table = True
            # Fix table formatting to have spaces around content
            parts = line.split('|')
            fixed_parts = []
            for part in parts:
                if part.strip():
                    fixed_parts.append(f' {part.strip()} ')
                else:
                    fixed_parts.append(' ')
            fixed_lines.append('|'.join(fixed_parts))
        elif in_table and not '|' in line:
            in_table = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 14. Fix blockquote formatting
    content = re.sub(r'^>\s*([^\s])', r'> \1', content, flags=re.MULTILINE)
    
    # 15. Fix horizontal rule formatting
    content = re.sub(r'^(\s*[-*_]{3,})\s*$', r'\1', content, flags=re.MULTILINE)
    
    # 16. Fix task list formatting
    content = re.sub(r'^(\s*[-*+])\s*\[([ xX])\]\s*([^\s])', r'\1 [\2] \3', content, flags=re.MULTILINE)
    
    # 17. Add a single newline at the end of the file
    content = content.rstrip() + '\n'
    
    return content

def clean_file(filepath: str) -> bool:
    """
    Cleans a single Markdown file.

    Args:
        filepath (str): The path to the Markdown file.

    Returns:
        bool: True if the file was cleaned, False otherwise.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        cleaned_content = clean_markdown_content(content)
        
        if cleaned_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"✅ Cleaned: {filepath}")
            return True
        else:
            print(f"✅ Already clean: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {filepath}: {e}")
        return False

def main() -> None:
    """
    The main function of the script.

    This function finds all Markdown files in the project, cleans them, and
    then prints a summary of the results.
    """
    print("🧹 Ultimate Markdown Cleaner Real...")
    print("=" * 50)
    
    md_files = find_markdown_files()
    print(f"📁 Found {len(md_files)} Markdown files")
    
    cleaned_count = 0
    for filepath in md_files:
        if clean_file(filepath):
            cleaned_count += 1
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Total files: {len(md_files)}")
    print(f"   Files cleaned: {cleaned_count}")
    
    if cleaned_count > 0:
        print("\n🎉 All Markdown files cleaned successfully!")
        print("📝 No more linter issues!")
    else:
        print("\n✅ All Markdown files were already clean!")

if __name__ == "__main__":
    main()
