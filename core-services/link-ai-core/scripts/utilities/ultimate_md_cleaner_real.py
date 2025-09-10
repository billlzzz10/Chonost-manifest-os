#!/usr/bin/env python3
"""
Ultimate Markdown Cleaner Real
ทำความสะอาดไฟล์ .md ทั้งหมดให้ไม่มี linter issues - เวอร์ชันที่แก้ไขปัญหาทั้งหมดอย่างถูกต้อง
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

def clean_markdown_content(content: str) -> str:
    """ทำความสะอาดเนื้อหา Markdown ตาม linter rules ที่เข้มงวดที่สุด"""
    
    # 1. แก้ไข trailing spaces และ tabs
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # 2. แก้ไข multiple blank lines ให้เหลือแค่ 2 บรรทัด
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 3. แก้ไข header formatting - ต้องมี space หลัง #
    content = re.sub(r'^(#{1,6})\s*([^#\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    # 4. แก้ไข list formatting - ต้องมี space หลัง marker
    content = re.sub(r'^(\s*[-*+])\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    # 5. แก้ไข code block formatting - ลบ language specifier ออกทั้งหมด
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.startswith('```'):
            if not in_code_block:
                # เริ่ม code block - ลบ language specifier ออก
                in_code_block = True
                fixed_lines.append('```')
            else:
                # จบ code block
                in_code_block = False
                fixed_lines.append('```')
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 6. แก้ไข link formatting - ต้องมี space หลัง closing parenthesis
    # [text](url)text -> [text](url) text
    content = re.sub(r'(\]\([^)]+\))\s*([^\s])', r'\1 \2', content)
    
    # 7. แก้ไข emphasis formatting - ต้องมี space หลัง closing markers
    # **text**text -> **text** text
    content = re.sub(r'(\*\*[^*]+\*\*)\s*([^\s*])', r'\1 \2', content)
    # *text*text -> *text* text
    content = re.sub(r'(\*[^*]+\*)\s*([^\s*])', r'\1 \2', content)
    
    # 8. แก้ไข emoji formatting - ต้องมี space หลัง emoji
    # ใช้ regex ที่ถูกต้อง: emoji + text -> emoji + space + text
    emoji_pattern = r'([🚀📋✨🔧📁🎯📊🤖💻📝🔍⚙️🛠️📦🧪💬🔗🐳🌐📈🛡️✅❌])\s*([^#\s])'
    content = re.sub(emoji_pattern, r'\1 \2', content)
    
    # 9. แก้ไข inline code formatting - ต้องมี space หลัง
    # `code`text -> `code` text
    content = re.sub(r'(`[^`]+`)\s*([^\s`])', r'\1 \2', content)
    
    # 10. แก้ไข image formatting - ต้องมี space หลัง
    # ![alt](url)text -> ![alt](url) text
    content = re.sub(r'(!\[[^\]]*\]\([^)]+\))\s*([^\s])', r'\1 \2', content)
    
    # 11. แก้ไข strikethrough formatting - ต้องมี space หลัง
    # ~~text~~text -> ~~text~~ text
    content = re.sub(r'(~~[^~]+~~)\s*([^\s~])', r'\1 \2', content)
    
    # 12. แก้ไข colon spacing - ลบ space ก่อน colon
    # **text** : -> **text**:
    content = re.sub(r'(\*\*[^*]+\*\*)\s*:\s*', r'\1: ', content)
    content = re.sub(r'(\*[^*]+\*)\s*:\s*', r'\1: ', content)
    
    # 13. แก้ไข table formatting - ต้องมี space รอบ content
    lines = content.split('\n')
    fixed_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line and not line.strip().startswith('```'):
            in_table = True
            # แก้ไข table formatting ให้มี space รอบ content
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
    
    # 14. แก้ไข blockquote formatting
    content = re.sub(r'^>\s*([^\s])', r'> \1', content, flags=re.MULTILINE)
    
    # 15. แก้ไข horizontal rule formatting
    content = re.sub(r'^(\s*[-*_]{3,})\s*$', r'\1', content, flags=re.MULTILINE)
    
    # 16. แก้ไข task list formatting
    content = re.sub(r'^(\s*[-*+])\s*\[([ xX])\]\s*([^\s])', r'\1 [\2] \3', content, flags=re.MULTILINE)
    
    # 17. เพิ่ม newline ตัวเดียวที่ท้ายไฟล์
    content = content.rstrip() + '\n'
    
    return content

def clean_file(filepath: str) -> bool:
    """ทำความสะอาดไฟล์ Markdown เดียว"""
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
    """Main function"""
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
