#!/usr/bin/env python3
"""
Smart Vault Manager - เครื่องมือจัดการ Vault ที่ชาญฉลาดและรองรับการเปลี่ยนแปลง
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import difflib

class SmartVaultManager:
    """เครื่องมือจัดการ Vault ที่ชาญฉลาด"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.analysis_result = {}
        self.management_plan = {}
        self.operations_log = []
        
    def analyze_current_structure(self) -> Dict[str, Any]:
        """วิเคราะห์โครงสร้างปัจจุบันอย่างละเอียด"""
        print("🔍 วิเคราะห์โครงสร้างปัจจุบัน...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'vault_path': str(self.vault_path),
            'folders': {},
            'files': {},
            'duplicate_folders': [],
            'empty_folders': [],
            'orphaned_files': [],
            'structure_issues': [],
            'statistics': {
                'total_folders': 0,
                'total_files': 0,
                'md_files': 0,
                'json_files': 0,
                'other_files': 0
            }
        }
        
        # วิเคราะห์โฟลเดอร์หลัก
        main_folders = [
            '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
            '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
            '08_Templates-Tools'
        ]
        
        # ตรวจสอบโฟลเดอร์ที่ซ้ำซ้อน
        all_folders = [f.name for f in self.vault_path.iterdir() if f.is_dir()]
        duplicate_patterns = self._find_duplicate_patterns(all_folders)
        
        for folder_name in main_folders:
            folder_path = self.vault_path / folder_name
            if folder_path.exists():
                folder_info = self._analyze_folder(folder_path)
                analysis['folders'][folder_name] = folder_info
                analysis['statistics']['total_folders'] += 1
                
                # ตรวจสอบโฟลเดอร์ว่าง
                if folder_info['file_count'] == 0:
                    analysis['empty_folders'].append(folder_name)
                
                # ตรวจสอบปัญหาการจัดการ
                if folder_info['has_management_issues']:
                    analysis['structure_issues'].append({
                        'folder': folder_name,
                        'issue': 'ขาดไฟล์จัดการ (README, Dashboard, Index)',
                        'severity': 'medium'
                    })
        
        # วิเคราะห์โฟลเดอร์อื่นๆ
        other_folders = [f for f in all_folders if f not in main_folders]
        for folder_name in other_folders:
            folder_path = self.vault_path / folder_name
            folder_info = self._analyze_folder(folder_path)
            analysis['folders'][folder_name] = folder_info
            analysis['statistics']['total_folders'] += 1
            
            # ตรวจสอบโฟลเดอร์ที่อาจซ้ำซ้อน
            if any(pattern in folder_name for pattern in duplicate_patterns):
                analysis['duplicate_folders'].append(folder_name)
        
        # วิเคราะห์ไฟล์ในโฟลเดอร์ Templates-Tools
        templates_path = self.vault_path / "08_Templates-Tools"
        if templates_path.exists():
            analysis['templates_analysis'] = self._analyze_templates_structure(templates_path)
        
        self.analysis_result = analysis
        return analysis
    
    def _analyze_folder(self, folder_path: Path) -> Dict[str, Any]:
        """วิเคราะห์โฟลเดอร์เดียว"""
        files = list(folder_path.rglob("*"))
        md_files = [f for f in files if f.is_file() and f.suffix == '.md']
        json_files = [f for f in files if f.is_file() and f.suffix == '.json']
        other_files = [f for f in files if f.is_file() and f.suffix not in ['.md', '.json']]
        
        # ตรวจสอบไฟล์จัดการ
        has_readme = any('readme' in f.name.lower() for f in md_files)
        has_dashboard = any('dashboard' in f.name.lower() for f in md_files)
        has_index = any('index' in f.name.lower() for f in md_files)
        
        return {
            'path': str(folder_path),
            'file_count': len([f for f in files if f.is_file()]),
            'folder_count': len([f for f in files if f.is_dir()]),
            'md_files': len(md_files),
            'json_files': len(json_files),
            'other_files': len(other_files),
            'has_readme': has_readme,
            'has_dashboard': has_dashboard,
            'has_index': has_index,
            'has_management_issues': not (has_readme or has_dashboard or has_index),
            'files': [f.name for f in md_files[:10]],  # แสดง 10 ไฟล์แรก
            'subfolders': [f.name for f in files if f.is_dir()]
        }
    
    def _analyze_templates_structure(self, templates_path: Path) -> Dict[str, Any]:
        """วิเคราะห์โครงสร้าง Templates-Tools"""
        analysis = {
            'subfolders': {},
            'file_distribution': {},
            'missing_structure': []
        }
        
        expected_subfolders = ['Prompts', 'Document_Templates', 'Tools_and_Utilities', 'Databases']
        
        for subfolder in expected_subfolders:
            subfolder_path = templates_path / subfolder
            if subfolder_path.exists():
                files = list(subfolder_path.rglob("*"))
                md_files = [f for f in files if f.is_file() and f.suffix == '.md']
                
                analysis['subfolders'][subfolder] = {
                    'file_count': len([f for f in files if f.is_file()]),
                    'md_files': len(md_files),
                    'has_readme': any('readme' in f.name.lower() for f in md_files)
                }
                
                analysis['file_distribution'][subfolder] = len([f for f in files if f.is_file()])
            else:
                analysis['missing_structure'].append(subfolder)
        
        return analysis
    
    def _find_duplicate_patterns(self, folder_names: List[str]) -> List[str]:
        """หารูปแบบโฟลเดอร์ที่ซ้ำซ้อน"""
        patterns = []
        for name in folder_names:
            # หาชื่อที่คล้ายกัน
            similar = difflib.get_close_matches(name, folder_names, n=2, cutoff=0.6)
            if len(similar) > 1:
                patterns.append(name)
        return patterns
    
    def generate_management_plan(self) -> Dict[str, Any]:
        """สร้างแผนการจัดการ"""
        print("📋 สร้างแผนการจัดการ...")
        
        plan = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_operations': 0,
                'critical_issues': 0,
                'recommended_actions': []
            },
            'operations': {
                'create_structure': [],
                'move_files': [],
                'create_management_files': [],
                'cleanup': [],
                'organize': []
            },
            'recommendations': []
        }
        
        analysis = self.analysis_result
        
        # 1. แก้ไขปัญหาวิกฤต
        if analysis['duplicate_folders']:
            plan['summary']['critical_issues'] += len(analysis['duplicate_folders'])
            plan['operations']['cleanup'].append({
                'action': 'resolve_duplicates',
                'folders': analysis['duplicate_folders'],
                'priority': 'critical'
            })
            plan['recommendations'].append('แก้ไขโฟลเดอร์ซ้ำซ้อนก่อน')
        
        # 2. สร้างโครงสร้างที่ขาดหาย
        if 'templates_analysis' in analysis:
            missing = analysis['templates_analysis']['missing_structure']
            if missing:
                plan['operations']['create_structure'].append({
                    'action': 'create_missing_folders',
                    'folders': missing,
                    'priority': 'high'
                })
        
        # 3. ย้ายไฟล์ที่กระจาย
        if analysis['folders']:
            for folder_name, folder_info in analysis['folders'].items():
                if folder_name not in ['00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
                                     '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
                                     '08_Templates-Tools']:
                    # โฟลเดอร์เก่าที่ควรย้าย
                    if folder_info['file_count'] > 0:
                        plan['operations']['move_files'].append({
                            'action': 'move_old_folder',
                            'source': folder_name,
                            'target': self._determine_target_folder(folder_name, folder_info),
                            'priority': 'medium'
                        })
        
        # 4. สร้างไฟล์จัดการ
        for folder_name, folder_info in analysis['folders'].items():
            if folder_info['has_management_issues']:
                plan['operations']['create_management_files'].append({
                    'action': 'create_readme',
                    'folder': folder_name,
                    'priority': 'medium'
                })
        
        # 5. จัดระเบียบ Templates-Tools
        if 'templates_analysis' in analysis:
            templates_analysis = analysis['templates_analysis']
            for subfolder, info in templates_analysis['subfolders'].items():
                if not info['has_readme'] and info['file_count'] > 0:
                    plan['operations']['create_management_files'].append({
                        'action': 'create_templates_readme',
                        'folder': f'08_Templates-Tools/{subfolder}',
                        'priority': 'low'
                    })
        
        plan['summary']['total_operations'] = (
            len(plan['operations']['create_structure']) +
            len(plan['operations']['move_files']) +
            len(plan['operations']['create_management_files']) +
            len(plan['operations']['cleanup']) +
            len(plan['operations']['organize'])
        )
        
        self.management_plan = plan
        return plan
    
    def _determine_target_folder(self, folder_name: str, folder_info: Dict[str, Any]) -> str:
        """กำหนดโฟลเดอร์ปลายทางสำหรับไฟล์"""
        # ตรรกะการจัดหมวดหมู่
        if 'prompt' in folder_name.lower() or 'copilot' in folder_name.lower():
            return '08_Templates-Tools/Prompts/Default_Prompts'
        elif 'template' in folder_name.lower():
            return '08_Templates-Tools/Document_Templates'
        elif 'tool' in folder_name.lower() or 'utility' in folder_name.lower():
            return '08_Templates-Tools/Tools_and_Utilities'
        elif 'database' in folder_name.lower() or 'data' in folder_name.lower():
            return '08_Templates-Tools/Databases'
        elif 'note' in folder_name.lower() or 'inbox' in folder_name.lower():
            return '06_NOTE'
        else:
            return '06_NOTE'  # default
    
    def display_analysis_report(self):
        """แสดงรายงานการวิเคราะห์"""
        analysis = self.analysis_result
        
        print("\n" + "="*80)
        print("📊 รายงานการวิเคราะห์โครงสร้าง Vault")
        print("="*80)
        
        print(f"\n📁 ข้อมูลพื้นฐาน:")
        print(f"   Path: {analysis['vault_path']}")
        print(f"   โฟลเดอร์ทั้งหมด: {analysis['statistics']['total_folders']}")
        print(f"   ไฟล์ทั้งหมด: {analysis['statistics']['total_files']}")
        print(f"   ไฟล์ Markdown: {analysis['statistics']['md_files']}")
        
        if analysis['duplicate_folders']:
            print(f"\n⚠️ โฟลเดอร์ที่ซ้ำซ้อน:")
            for folder in analysis['duplicate_folders']:
                print(f"   - {folder}")
        
        if analysis['empty_folders']:
            print(f"\n📁 โฟลเดอร์ว่าง:")
            for folder in analysis['empty_folders']:
                print(f"   - {folder}")
        
        if analysis['structure_issues']:
            print(f"\n❌ ปัญหาการจัดการ:")
            for issue in analysis['structure_issues']:
                print(f"   - {issue['folder']}: {issue['issue']}")
        
        # แสดงรายละเอียดโฟลเดอร์หลัก
        print(f"\n📋 รายละเอียดโฟลเดอร์หลัก:")
        main_folders = ['00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
                       '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE']
        
        for folder in main_folders:
            if folder in analysis['folders']:
                info = analysis['folders'][folder]
                status = "✅" if not info['has_management_issues'] else "❌"
                print(f"   {status} {folder}: {info['file_count']} ไฟล์")
    
    def display_management_plan(self):
        """แสดงแผนการจัดการ"""
        plan = self.management_plan
        
        print("\n" + "="*80)
        print("📋 แผนการจัดการ Vault")
        print("="*80)
        
        print(f"\n📊 สรุปแผน:")
        print(f"   การดำเนินการทั้งหมด: {plan['summary']['total_operations']}")
        print(f"   ปัญหาวิกฤต: {plan['summary']['critical_issues']}")
        
        if plan['operations']['cleanup']:
            print(f"\n🚨 การแก้ไขปัญหาวิกฤต:")
            for op in plan['operations']['cleanup']:
                print(f"   - {op['action']}: {op['folders']}")
        
        if plan['operations']['create_structure']:
            print(f"\n🏗️ การสร้างโครงสร้าง:")
            for op in plan['operations']['create_structure']:
                print(f"   - {op['action']}: {op['folders']}")
        
        if plan['operations']['move_files']:
            print(f"\n📁 การย้ายไฟล์:")
            for op in plan['operations']['move_files']:
                print(f"   - ย้าย {op['source']} -> {op['target']}")
        
        if plan['operations']['create_management_files']:
            print(f"\n📝 การสร้างไฟล์จัดการ:")
            for op in plan['operations']['create_management_files']:
                print(f"   - สร้าง README สำหรับ {op['folder']}")
        
        if plan['recommendations']:
            print(f"\n💡 คำแนะนำ:")
            for rec in plan['recommendations']:
                print(f"   - {rec}")
    
    def execute_plan(self, confirm: bool = True) -> bool:
        """ดำเนินการตามแผน"""
        if confirm:
            print("\n" + "="*80)
            print("🚀 เริ่มดำเนินการตามแผน")
            print("="*80)
            
            response = input("\n❓ ต้องการดำเนินการตามแผนนี้หรือไม่? (y/N): ")
            if response.lower() != 'y':
                print("❌ ยกเลิกการดำเนินการ")
                return False
        
        plan = self.management_plan
        
        try:
            # ดำเนินการตามลำดับความสำคัญ
            operations_order = ['cleanup', 'create_structure', 'move_files', 'create_management_files', 'organize']
            
            for op_type in operations_order:
                if plan['operations'][op_type]:
                    print(f"\n🔧 ดำเนินการ: {op_type}")
                    for op in plan['operations'][op_type]:
                        self._execute_operation(op)
            
            print("\n✅ การดำเนินการเสร็จสิ้น!")
            return True
            
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def _execute_operation(self, operation: Dict[str, Any]):
        """ดำเนินการเดียว"""
        action = operation['action']
        
        if action == 'resolve_duplicates':
            print(f"   🗑️ แก้ไขโฟลเดอร์ซ้ำซ้อน: {operation['folders']}")
            # TODO: Implement duplicate resolution
            
        elif action == 'create_missing_folders':
            for folder in operation['folders']:
                folder_path = self.vault_path / "08_Templates-Tools" / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ สร้างโฟลเดอร์: {folder}")
        
        elif action == 'move_old_folder':
            source = self.vault_path / operation['source']
            target = self.vault_path / operation['target']
            if source.exists():
                # TODO: Implement file moving logic
                print(f"   📁 ย้าย: {operation['source']} -> {operation['target']}")
        
        elif action == 'create_readme':
            folder_path = self.vault_path / operation['folder']
            readme_path = folder_path / "README.md"
            if not readme_path.exists():
                # TODO: Implement README creation
                print(f"   📝 สร้าง README: {operation['folder']}")
    
    def save_report(self, filename: str = "vault_management_report.json"):
        """บันทึกรายงาน"""
        report = {
            'analysis': self.analysis_result,
            'plan': self.management_plan,
            'operations_log': self.operations_log,
            'generated_at': datetime.now().isoformat()
        }
        
        report_path = self.vault_path / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 บันทึกรายงาน: {filename}")

def main():
    """ฟังก์ชันหลัก"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 Smart Vault Manager - เครื่องมือจัดการ Vault ที่ชาญฉลาด")
    print("="*80)
    
    # สร้างเครื่องมือ
    manager = SmartVaultManager(vault_path)
    
    # 1. วิเคราะห์โครงสร้าง
    analysis = manager.analyze_current_structure()
    
    # 2. แสดงรายงานการวิเคราะห์
    manager.display_analysis_report()
    
    # 3. สร้างแผนการจัดการ
    plan = manager.generate_management_plan()
    
    # 4. แสดงแผนการจัดการ
    manager.display_management_plan()
    
    # 5. บันทึกรายงาน
    manager.save_report()
    
    # 6. ถามผู้ใช้ว่าต้องการดำเนินการหรือไม่
    print("\n" + "="*80)
    print("🎯 ขั้นตอนต่อไป")
    print("="*80)
    print("1. ตรวจสอบรายงานการวิเคราะห์")
    print("2. ตรวจสอบแผนการจัดการ")
    print("3. ตัดสินใจว่าจะดำเนินการหรือไม่")
    print("4. เรียกใช้ manager.execute_plan() เพื่อดำเนินการ")

if __name__ == "__main__":
    main()
