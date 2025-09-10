#!/usr/bin/env python3
"""
Ultimate Trailing Spaces Fixer
แก้ไข trailing spaces ทั้งหมดในไฟล์ .md
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple

def find_markdown_files() -> List[str]:
    """ค้นหาไฟล์ .md ทั้งหมด"""
    md_files = []
    for pattern in ["**/*.md", "**/*.mdc"]:
        md_files.extend(glob.glob(pattern, recursive=True))
    return md_files

def fix_trailing_spaces(content: str) -> str:
    """แก้ไข trailing spaces ทั้งหมด"""
    # แก้ไข trailing spaces และ tabs ในทุกบรรทัด
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # ลบ trailing spaces และ tabs
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
    
    # รวมบรรทัดกลับและเพิ่ม newline ตัวเดียวที่ท้ายไฟล์
    return '\n'.join(fixed_lines) + '\n'

def fix_file(filepath: str) -> bool:
    """แก้ไขไฟล์ Markdown เดียว"""
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
    """Main function"""
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
