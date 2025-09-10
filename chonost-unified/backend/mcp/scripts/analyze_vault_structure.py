#!/usr/bin/env python3
"""
Analyze Vault Structure - วิเคราะห์โครงสร้าง Vault อย่างละเอียด
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any

def analyze_vault_structure():
    """วิเคราะห์โครงสร้าง Vault อย่างละเอียด"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🔍 วิเคราะห์โครงสร้าง Vault อย่างละเอียด")
    print("=" * 60)
    
    # 1. วิเคราะห์โฟลเดอร์หลัก
    main_folders = [
        '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
        '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE'
    ]
    
    analysis = {
        'main_folders': {},
        'missing_readme': [],
        'missing_dashboard': [],
        'file_count': 0,
        'total_folders': 0
    }
    
    for folder in main_folders:
        folder_path = os.path.join(vault_path, folder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            md_files = [f for f in files if f.endswith('.md')]
            
            analysis['main_folders'][folder] = {
                'total_files': len(files),
                'md_files': len(md_files),
                'files': files,
                'has_readme': any('readme' in f.lower() for f in files),
                'has_dashboard': any('dashboard' in f.lower() for f in files),
                'has_index': any('index' in f.lower() for f in files)
            }
            
            analysis['file_count'] += len(files)
            analysis['total_folders'] += 1
            
            if not analysis['main_folders'][folder]['has_readme']:
                analysis['missing_readme'].append(folder)
            
            if not analysis['main_folders'][folder]['has_dashboard']:
                analysis['missing_dashboard'].append(folder)
    
    # 2. แสดงผลการวิเคราะห์
    print("\n📊 ผลการวิเคราะห์โฟลเดอร์หลัก:")
    print("-" * 40)
    
    for folder, info in analysis['main_folders'].items():
        print(f"\n📁 {folder}:")
        print(f"   ไฟล์ทั้งหมด: {info['total_files']}")
        print(f"   ไฟล์ Markdown: {info['md_files']}")
        print(f"   มี README: {'✅' if info['has_readme'] else '❌'}")
        print(f"   มี Dashboard: {'✅' if info['has_dashboard'] else '❌'}")
        print(f"   มี Index: {'✅' if info['has_index'] else '❌'}")
        
        if info['files']:
            print(f"   ไฟล์: {', '.join(info['files'][:5])}{'...' if len(info['files']) > 5 else ''}")
    
    # 3. วิเคราะห์ไฟล์ใน 08_Templates-Tools
    print("\n\n🔧 วิเคราะห์ 08_Templates-Tools:")
    print("-" * 40)
    
    templates_path = os.path.join(vault_path, "08_Templates-Tools")
    if os.path.exists(templates_path):
        for subfolder in ['Prompts', 'Document_Templates', 'Tools_and_Utilities', 'Databases']:
            subfolder_path = os.path.join(templates_path, subfolder)
            if os.path.exists(subfolder_path):
                files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
                md_files = [f for f in files if f.endswith('.md')]
                
                print(f"\n📁 {subfolder}:")
                print(f"   ไฟล์ทั้งหมด: {len(files)}")
                print(f"   ไฟล์ Markdown: {len(md_files)}")
                
                if subfolder == 'Prompts':
                    # วิเคราะห์ subfolders ของ Prompts
                    for prompt_type in ['General', 'Default_Prompts', 'Smart_Connections']:
                        prompt_path = os.path.join(subfolder_path, prompt_type)
                        if os.path.exists(prompt_path):
                            prompt_files = [f for f in os.listdir(prompt_path) if os.path.isfile(os.path.join(prompt_path, f))]
                            print(f"     📂 {prompt_type}: {len(prompt_files)} ไฟล์")
    
    # 4. สรุปปัญหาที่พบ
    print("\n\n❌ ปัญหาที่พบ:")
    print("-" * 40)
    
    if analysis['missing_readme']:
        print(f"📝 โฟลเดอร์ที่ขาด README: {', '.join(analysis['missing_readme'])}")
    
    if analysis['missing_dashboard']:
        print(f"📊 โฟลเดอร์ที่ขาด Dashboard: {', '.join(analysis['missing_dashboard'])}")
    
    print(f"\n📈 สถิติรวม:")
    print(f"   โฟลเดอร์หลัก: {analysis['total_folders']}")
    print(f"   ไฟล์ทั้งหมด: {analysis['file_count']}")
    print(f"   โฟลเดอร์ที่ขาด README: {len(analysis['missing_readme'])}")
    print(f"   โฟลเดอร์ที่ขาด Dashboard: {len(analysis['missing_dashboard'])}")
    
    return analysis

if __name__ == "__main__":
    analyze_vault_structure()
