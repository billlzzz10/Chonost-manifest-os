#!/usr/bin/env python3
"""
Complete Vault Management.
This script provides a complete and intelligent solution for managing an
Obsidian vault. It analyzes the old structure, moves files to their correct
locations, and cleans up old folders.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def analyze_old_structure() -> Dict[str, List[str]]:
    """
    Analyzes the old vault structure to find files that need to be moved.

    Returns:
        Dict[str, List[str]]: A dictionary containing the old folders and the
                              files within them.
    """
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
    """
    Creates a complete and intelligent vault structure.

    This function analyzes the old structure, moves files from the old folders
    to the new ones, and then cleans up the old, empty folders. It also
    creates README files for any new, empty folders.
    """
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 Starting complete and intelligent vault management")
    print("=" * 70)
    
    # 1. Analyze the old structure
    print("\n🔍 Analyzing old structure...")
    old_structure = analyze_old_structure()
    
    for folder, files in old_structure.items():
        if files:
            print(f"📁 {folder}: {len(files)} files")
    
    # 2. Move files from 08_TEMP to 08_Templates-Tools
    print("\n📁 Moving files from 08_TEMP...")
    source_path = os.path.join(vault_path, "08_TEMP")
    target_base = os.path.join(vault_path, "08_Templates-Tools")
    
    if os.path.exists(source_path):
        # Move files based on their type
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
            
            # Prompts (moved to General if not already there)
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
                
                # Create the destination folder if it doesn't exist
                os.makedirs(target_folder, exist_ok=True)
                
                # Move the file
                if not os.path.exists(target_file):
                    shutil.move(source_file, target_file)
                    print(f"✅ Moved: {file} -> {file_mapping[file]}")
                    moved_count += 1
                else:
                    print(f"⚠️ File already exists: {file}")
        
        print(f"📊 Moved files from 08_TEMP: {moved_count} files")
    
    # 3. Move files from copilot-conversations to Default_Prompts
    print("\n📁 Moving files from copilot-conversations...")
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
                    print(f"✅ Moved: {file}")
                    moved_count += 1
                else:
                    print(f"⚠️ File already exists: {file}")
        
        print(f"📊 Moved files from copilot-conversations: {moved_count} files")
    
    # 4. Move files from 99_INBOX to 06_NOTE
    print("\n📁 Moving files from 99_INBOX...")
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
                    print(f"✅ Moved: {file}")
                    moved_count += 1
                else:
                    print(f"⚠️ File already exists: {file}")
        
        print(f"📊 Moved files from 99_INBOX: {moved_count} files")
    
    # 5. Delete old, empty folders
    print("\n🗑️ Deleting old, empty folders...")
    old_folders = ["08_TEMP", "copilot-conversations", "99_INBOX"]
    
    for folder in old_folders:
        folder_path = os.path.join(vault_path, folder)
        if os.path.exists(folder_path):
            try:
                # Check if the folder is empty
                remaining_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                if not remaining_files:
                    shutil.rmtree(folder_path)
                    print(f"✅ Deleted empty folder: {folder}")
                else:
                    print(f"⚠️ Folder still contains files: {folder} ({len(remaining_files)} files)")
            except Exception as e:
                print(f"❌ Could not delete folder: {folder} - {e}")
    
    # 6. Create READMEs for empty folders
    print("\n📝 Creating READMEs for empty folders...")
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

## 🎯 Purpose
{folder.replace('_', ' ').lower()}

## 📋 Status
- [ ] Add first file

---
*Last updated: {date}*
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created README: {folder}")
    
    print("\n🎉 Complete vault management finished!")

if __name__ == "__main__":
    create_complete_structure()
