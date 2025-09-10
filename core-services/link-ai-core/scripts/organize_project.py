#!/usr/bin/env python3
"""
Project Organization Script
จัดระเบียบโครงสร้างโปรเจ็ค FileSystemMCP
"""

import os
import shutil
from pathlib import Path

def organize_scripts():
    """จัดระเบียบ scripts ไปยังโฟลเดอร์ที่เหมาะสม"""
    
    # สร้างโฟลเดอร์ย่อยถ้ายังไม่มี
    folders = {
        'core': 'scripts/core',
        'utilities': 'scripts/utilities', 
        'startup': 'scripts/startup',
        'analysis': 'scripts/analysis'
    }
    
    for folder_path in folders.values():
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created/ensured folder: {folder_path}")
    
    # กำหนดการย้ายไฟล์
    file_moves = {
        # Core Scripts
        'scripts/guardian.py': 'scripts/core/',
        'scripts/setup.py': 'scripts/core/',
        
        # Utility Scripts
        'scripts/ultimate_trailing_spaces_fixer.py': 'scripts/utilities/',
        'scripts/ultimate_md_cleaner_real.py': 'scripts/utilities/',
        'scripts/simple_file_manager.py': 'scripts/utilities/',
        'scripts/move_existing_files.py': 'scripts/utilities/',
        
        # Startup Scripts  
        'scripts/start-docker.ps1': 'scripts/startup/',
        'scripts/start-universal.ps1': 'scripts/startup/',
        'scripts/start-unified.ps1': 'scripts/startup/',
        'scripts/run.ps1': 'scripts/startup/',
        'scripts/run.bat': 'scripts/startup/',
        
        # Analysis Scripts
        'scripts/analyze_vault_structure.py': 'scripts/analysis/',
        'scripts/create_vault_structure.py': 'scripts/analysis/',
        'scripts/generate_datasets.py': 'scripts/analysis/',
    }
    
    # ย้ายไฟล์
    moved_count = 0
    for source, destination in file_moves.items():
        if os.path.exists(source):
            try:
                shutil.move(source, destination)
                print(f"✅ Moved: {source} → {destination}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {source}: {e}")
        else:
            print(f"⚠️  File not found: {source}")
    
    print(f"\n📊 Summary: Moved {moved_count} files")

def organize_configs():
    """จัดระเบียบ configuration files"""
    
    # สร้างโฟลเดอร์ config หลัก
    os.makedirs('config/core', exist_ok=True)
    os.makedirs('config/database', exist_ok=True)
    os.makedirs('config/ai', exist_ok=True)
    
    config_moves = {
        'configs/alembic.ini': 'config/database/',
        'configs/env.example': 'config/core/',
        'configs/fine_tuning_config.py': 'config/ai/',
        'configs/ai_orchestrator_schema.sql': 'config/database/', 
        'configs/ai_orchestrator_queries.sql': 'config/database/',
    }
    
    moved_count = 0
    for source, destination in config_moves.items():
        if os.path.exists(source):
            try:
                shutil.move(source, destination)
                print(f"✅ Moved config: {source} → {destination}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {source}: {e}")
        else:
            print(f"⚠️  Config file not found: {source}")
    
    print(f"\n📊 Config Summary: Moved {moved_count} files")

def cleanup_empty_folders():
    """ลบโฟลเดอร์ที่ว่างเปล่า"""
    empty_folders = []
    
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    empty_folders.append(dir_path)
            except OSError:
                pass
    
    if empty_folders:
        print(f"\n🗑️  Removed empty folders: {len(empty_folders)}")
        for folder in empty_folders:
            print(f"   - {folder}")

def main():
    """Main function"""
    print("🧹 Starting Project Organization...")
    print("=" * 50)
    
    print("\n📁 Organizing Scripts...")
    organize_scripts()
    
    print("\n⚙️  Organizing Configurations...")
    organize_configs()
    
    print("\n🗑️  Cleaning up empty folders...")
    cleanup_empty_folders()
    
    print("\n🎉 Project organization completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
