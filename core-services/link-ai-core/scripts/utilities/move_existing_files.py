#!/usr/bin/env python3
"""
Move Existing Files.
This script moves existing files to the new vault structure.
"""

import os
import shutil
from pathlib import Path

def move_existing_files():
    """
    Moves existing files to their new locations in the vault.

    This function moves files from the old `09_PROMPTS` and
    `copilot-custom-prompts` directories to the new `08_Templates-Tools`
    directory, and then removes the old, empty directories.
    """
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 Starting to move existing files")
    print("=" * 50)
    
    # 1. ย้ายไฟล์จาก 09_PROMPTS ไปยัง 08_Templates-Tools/Prompts/General
    print("📁 ย้ายไฟล์จาก 09_PROMPTS...")
    source_path = os.path.join(vault_path, "09_PROMPTS")
    target_path = os.path.join(vault_path, "08_Templates-Tools", "Prompts", "General")
    
    if os.path.exists(source_path):
        for file in os.listdir(source_path):
            if file.endswith('.md'):
                source_file = os.path.join(source_path, file)
                target_file = os.path.join(target_path, file)
                
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ ย้าย: {file}")
                else:
                    print(f"⚠️ ไฟล์มีอยู่แล้ว: {file}")
    
    # 2. ย้ายไฟล์จาก copilot-custom-prompts ไปยัง 08_Templates-Tools/Prompts/Default_Prompts
    print("\n📁 ย้ายไฟล์จาก copilot-custom-prompts...")
    source_path = os.path.join(vault_path, "copilot-custom-prompts")
    target_path = os.path.join(vault_path, "08_Templates-Tools", "Prompts", "Default_Prompts")
    
    if os.path.exists(source_path):
        for file in os.listdir(source_path):
            if file.endswith('.md'):
                source_file = os.path.join(source_path, file)
                target_file = os.path.join(target_path, file)
                
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ ย้าย: {file}")
                else:
                    print(f"⚠️ ไฟล์มีอยู่แล้ว: {file}")
    
    # 3. ลบโฟลเดอร์เก่าที่ว่างแล้ว
    print("\n🗑️ ลบโฟลเดอร์เก่าที่ว่างแล้ว...")
    old_folders = ["09_PROMPTS", "copilot-custom-prompts"]
    
    for folder in old_folders:
        folder_path = os.path.join(vault_path, folder)
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)
            print(f"✅ ลบโฟลเดอร์ว่าง: {folder}")
    
    print("\n🎉 การย้ายไฟล์เสร็จสิ้น!")

if __name__ == "__main__":
    move_existing_files()
