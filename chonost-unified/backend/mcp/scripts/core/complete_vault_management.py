#!/usr/bin/env python3
"""
Complete Vault Management - จัดการ Vault อย่างสมบูรณ์และชาญฉลาด
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def analyze_old_structure() -> Dict[str, List[str]]:
    """วิเคราะห์โครงสร้างเก่าเพื่อหาไฟล์ที่ต้องย้าย"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    old_folders = {
        "08_TEMP": [],
        "copilot-conversations": [],
        "99_INBOX": []
    }
    
    for folder in old_folders.keys():
        folder_path = os.path.join(vault_path, folder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            old_folders[folder] = files
    
    return old_folders

def create_complete_structure():
    """สร้างโครงสร้าง Vault อย่างสมบูรณ์และชาญฉลาด"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 เริ่มจัดการ Vault อย่างสมบูรณ์และชาญฉลาด")
    print("=" * 70)
    
    # 1. วิเคราะห์โครงสร้างเก่า
    print("\n🔍 วิเคราะห์โครงสร้างเก่า...")
    old_structure = analyze_old_structure()
    
    for folder, files in old_structure.items():
        if files:
            print(f"📁 {folder}: {len(files)} ไฟล์")
    
    # 2. ย้ายไฟล์จาก 08_TEMP ไปยัง 08_Templates-Tools
    print("\n📁 ย้ายไฟล์จาก 08_TEMP...")
    source_path = os.path.join(vault_path, "08_TEMP")
    target_base = os.path.join(vault_path, "08_Templates-Tools")
    
    if os.path.exists(source_path):
        # ย้ายไฟล์ตามประเภท
        file_mapping = {
            # Document Templates
            "Character_Template.md": "Document_Templates/",
            "Character_Template_New.md": "Document_Templates/",
            "Scene_Template_New.md": "Document_Templates/",
            "Location_Template.md": "Document_Templates/",
            "template_location.md": "Document_Templates/",
            "PlotOutline.md": "Document_Templates/",
            "chapter_template.json": "Document_Templates/",
            "INDEX_Template.md": "Document_Templates/",
            "Template_YAML.md": "Document_Templates/",
            "SceneTemplate.md": "Document_Templates/",
            "AshvalTemplate.md": "Document_Templates/",
            "Draft-All-V3.md": "Document_Templates/",
            "DailyReport.md": "Document_Templates/",
            "Note.md": "Document_Templates/",
            "Locations.md": "Document_Templates/",
            
            # Tools and Utilities
            "APIHealthCheck.md": "Tools_and_Utilities/",
            "AshvalWriter.md": "Tools_and_Utilities/",
            "Automated Document Processing Template.md": "Tools_and_Utilities/",
            "Automated Scene Merger-V5.md.md": "Tools_and_Utilities/",
            "DuplicateFinder.md": "Tools_and_Utilities/",
            "FileRename.md": "Tools_and_Utilities/",
            "Find_Vault.md": "Tools_and_Utilities/",
            "Generat_Index_V2.md": "Tools_and_Utilities/",
            "Validator.md": "Tools_and_Utilities/",
            "renamev2.md": "Tools_and_Utilities/",
            "fix_bad_scene_model.md": "Tools_and_Utilities/",
            "Vault_Organization_Tool.md": "Tools_and_Utilities/",
            "File_Naming_Standards.md": "Tools_and_Utilities/",
            "extract_file_content.md": "Tools_and_Utilities/",
            "Conflict.md": "Tools_and_Utilities/",
            "ค้นหาแบบยาว.md": "Tools_and_Utilities/",
            "ตรวจไฟล์ซ้ำซ้อน.md": "Tools_and_Utilities/",
            "สร้างภาพ.md": "Tools_and_Utilities/",
            "สร้างภาพv11.md": "Tools_and_Utilities/",
            
            # Databases
            "ArcanaDatabase.md": "Databases/",
            
            # Prompts (ย้ายไป General ถ้ายังไม่มี)
            "AshvalPrompt.md": "Prompts/General/",
            "Ashval Prompt Master.md": "Prompts/General/",
            "GeminiTagger.md": "Prompts/General/",
            "Summerize_Geminiv3.md": "Prompts/General/",
            "master_prompt.json": "Prompts/General/",
            "scene_prompt.json": "Prompts/General/",
            "scoring_prompt.json": "Prompts/General/",
        }
        
        moved_count = 0
        for file in os.listdir(source_path):
            if file in file_mapping:
                source_file = os.path.join(source_path, file)
                target_folder = os.path.join(target_base, file_mapping[file])
                target_file = os.path.join(target_folder, file)
                
                # สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
                os.makedirs(target_folder, exist_ok=True)
                
                # ย้ายไฟล์
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ ย้าย: {file} -> {file_mapping[file]}")
                    moved_count += 1
                else:
                    print(f"⚠️ ไฟล์มีอยู่แล้ว: {file}")
        
        print(f"📊 ย้ายไฟล์จาก 08_TEMP: {moved_count} ไฟล์")
    
    # 3. ย้ายไฟล์จาก copilot-conversations ไปยัง Default_Prompts
    print("\n📁 ย้ายไฟล์จาก copilot-conversations...")
    source_path = os.path.join(vault_path, "copilot-conversations")
    target_path = os.path.join(vault_path, "08_Templates-Tools", "Prompts", "Default_Prompts")
    
    if os.path.exists(source_path):
        moved_count = 0
        for file in os.listdir(source_path):
            if file.endswith('.md') and file not in ['README.md']:
                source_file = os.path.join(source_path, file)
                target_file = os.path.join(target_path, file)
                
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ ย้าย: {file}")
                    moved_count += 1
                else:
                    print(f"⚠️ ไฟล์มีอยู่แล้ว: {file}")
        
        print(f"📊 ย้ายไฟล์จาก copilot-conversations: {moved_count} ไฟล์")
    
    # 4. ย้ายไฟล์จาก 99_INBOX ไปยัง 06_NOTE
    print("\n📁 ย้ายไฟล์จาก 99_INBOX...")
    source_path = os.path.join(vault_path, "99_INBOX")
    target_path = os.path.join(vault_path, "06_NOTE")
    
    if os.path.exists(source_path):
        moved_count = 0
        for file in os.listdir(source_path):
            if file.endswith('.md') and file not in ['README.md', 'Dashboard.md']:
                source_file = os.path.join(source_path, file)
                target_file = os.path.join(target_path, file)
                
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ ย้าย: {file}")
                    moved_count += 1
                else:
                    print(f"⚠️ ไฟล์มีอยู่แล้ว: {file}")
        
        print(f"📊 ย้ายไฟล์จาก 99_INBOX: {moved_count} ไฟล์")
    
    # 5. ลบโฟลเดอร์เก่าที่ว่างแล้ว
    print("\n🗑️ ลบโฟลเดอร์เก่าที่ว่างแล้ว...")
    old_folders = ["08_TEMP", "copilot-conversations", "99_INBOX"]
    
    for folder in old_folders:
        folder_path = os.path.join(vault_path, folder)
        if os.path.exists(folder_path):
            try:
                # ตรวจสอบว่าโฟลเดอร์ว่างหรือไม่
                remaining_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                if not remaining_files:
                    shutil.rmtree(folder_path)
                    print(f"✅ ลบโฟลเดอร์ว่าง: {folder}")
                else:
                    print(f"⚠️ โฟลเดอร์ยังมีไฟล์: {folder} ({len(remaining_files)} ไฟล์)")
            except Exception as e:
                print(f"❌ ไม่สามารถลบโฟลเดอร์: {folder} - {e}")
    
    # 6. สร้าง README สำหรับโฟลเดอร์ที่ว่าง
    print("\n📝 สร้าง README สำหรับโฟลเดอร์ที่ว่าง...")
    empty_folders = [
        "Document_Templates",
        "Tools_and_Utilities", 
        "Databases"
    ]
    
    for folder in empty_folders:
        folder_path = os.path.join(target_base, folder)
        readme_path = os.path.join(folder_path, "README.md")
        
        if not os.path.exists(readme_path):
            date = datetime.now().strftime("%Y-%m-%d")
            content = f"""# 📁 {folder.replace('_', ' ')}

## 🎯 วัตถุประสงค์
{folder.replace('_', ' ').lower()}

## 📋 สถานะ
- [ ] เพิ่มไฟล์แรก

---
*อัปเดตล่าสุด: {date}*
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ สร้าง README: {folder}")
    
    print("\n🎉 การจัดการ Vault อย่างสมบูรณ์เสร็จสิ้น!")

if __name__ == "__main__":
    create_complete_structure()
