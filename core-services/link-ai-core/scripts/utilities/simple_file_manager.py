#!/usr/bin/env python3
"""
Simple File Manager.
This script uses existing tools to manage the file structure of a project.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFileManager:
    """
    A simple file manager tool.

    This class provides methods for analyzing, creating, and modifying the
    file structure of a project.
    """
    
    def __init__(self, base_path: str):
        """
        Initializes the SimpleFileManager.

        Args:
            base_path (str): The base path of the project.
        """
        self.base_path = Path(base_path)
        self.operations_log = []
        
    def analyze_current_structure(self) -> Dict[str, Any]:
        """
        Analyzes the current file structure.

        Returns:
            Dict[str, Any]: A dictionary containing the analysis of the
                            current file structure.
        """
        logger.info(f"🔍 Analyzing structure: {self.base_path}")
        
        structure = {
            "base_path": str(self.base_path),
            "folders": {},
            "files": {},
            "total_items": 0
        }
        
        try:
            for item in self.base_path.rglob("*"):
                if item.is_file():
                    relative_path = str(item.relative_to(self.base_path))
                    structure["files"][relative_path] = {
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime
                    }
                    structure["total_items"] += 1
                elif item.is_dir():
                    relative_path = str(item.relative_to(self.base_path))
                    structure["folders"][relative_path] = {
                        "created": item.stat().st_ctime
                    }
                    structure["total_items"] += 1
                    
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
            
        return structure
    
    def create_new_structure(self, structure_plan: Dict[str, Any]) -> bool:
        """
        Creates a new file structure based on a plan.

        Args:
            structure_plan (Dict[str, Any]): A dictionary containing the plan
                                             for the new file structure.

        Returns:
            bool: True if the new structure was created successfully, False
                  otherwise.
        """
        logger.info("🏗️ Starting to create new structure")
        
        try:
            # Create main folders
            for folder_name in structure_plan.get("main_folders", []):
                folder_path = self.base_path / folder_name
                if not folder_path.exists():
                    folder_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✅ Created folder: {folder_name}")
                    self.operations_log.append(f"Created folder: {folder_name}")
            
            # Create subfolders
            for folder_path, subfolders in structure_plan.get("subfolders", {}).items():
                parent_path = self.base_path / folder_path
                if parent_path.exists():
                    for subfolder in subfolders:
                        subfolder_path = parent_path / subfolder
                        if not subfolder_path.exists():
                            subfolder_path.mkdir(parents=True, exist_ok=True)
                            logger.info(f"✅ Created subfolder: {folder_path}/{subfolder}")
                            self.operations_log.append(f"Created subfolder: {folder_path}/{subfolder}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating new structure: {e}")
            return False
    
    def move_files_to_new_structure(self, file_mapping: Dict[str, str]) -> bool:
        """
        Moves files to a new structure based on a mapping.

        Args:
            file_mapping (Dict[str, str]): A dictionary containing the mapping
                                           of source paths to target paths.

        Returns:
            bool: True if the files were moved successfully, False otherwise.
        """
        logger.info("📁 Starting to move files")
        
        try:
            for source_path, target_path in file_mapping.items():
                source = self.base_path / source_path
                target = self.base_path / target_path
                
                if source.exists():
                    # Create the target folder if it doesn't exist
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    shutil.move(str(source), str(target))
                    logger.info(f"✅ Moved file: {source_path} -> {target_path}")
                    self.operations_log.append(f"Moved file: {source_path} -> {target_path}")
                else:
                    logger.warning(f"⚠️ File not found: {source_path}")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error moving files: {e}")
            return False
    
    def remove_duplicate_files(self, duplicate_list: List[str]) -> bool:
        """
        Removes duplicate files.

        Args:
            duplicate_list (List[str]): A list of paths to the duplicate
                                        files to be removed.

        Returns:
            bool: True if the duplicate files were removed successfully, False
                  otherwise.
        """
        logger.info("🗑️ Starting to remove duplicate files")
        
        try:
            for file_path in duplicate_list:
                full_path = self.base_path / file_path
                if full_path.exists():
                    full_path.unlink()
                    logger.info(f"✅ Removed duplicate file: {file_path}")
                    self.operations_log.append(f"Removed duplicate file: {file_path}")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing files: {e}")
            return False
    
    def generate_structure_report(self) -> Dict[str, Any]:
        """
        Generates a report of the current file structure.

        Returns:
            Dict[str, Any]: A dictionary containing the structure report.
        """
        current_structure = self.analyze_current_structure()
        
        report = {
            "timestamp": str(Path().cwd()),
            "base_path": str(self.base_path),
            "total_items": current_structure["total_items"],
            "folders_count": len(current_structure["folders"]),
            "files_count": len(current_structure["files"]),
            "operations_performed": self.operations_log,
            "structure": current_structure
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "structure_report.json"):
        """
        Saves a report to a file.

        Args:
            report (Dict[str, Any]): The report to save.
            filename (str, optional): The name of the file to save the report
                                     to. Defaults to "structure_report.json".
        """
        report_path = self.base_path / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"📄 Saved report: {filename}")

def main():
    """
    The main function of the script.

    This function defines the new file structure, the file mapping, and the
    list of duplicate files, and then uses the `SimpleFileManager` to
    restructure the project.
    """
    # Define the new structure as desired
    new_structure = {
        "main_folders": [
            "00_DASHBOARD",
            "01_MANUSCRIPT", 
            "02_CHARACTERS",
            "03_WORLDBUILDING",
            "04_PLOT-TIMELINE",
            "05_SYSTEMS-LORE",
            "06_NOTE",
            "08_Templates-Tools"
        ],
        "subfolders": {
            "08_Templates-Tools": [
                "Prompts",
                "Document_Templates", 
                "Tools_and_Utilities",
                "Databases"
            ],
            "08_Templates-Tools/Prompts": [
                "General",
                "Default_Prompts",
                "Smart_Connections"
            ]
        }
    }
    
    # แผนการย้ายไฟล์
    file_mapping = {
        # ย้ายไฟล์จาก 06_Templates_and_Tools ไปยัง 08_Templates-Tools
        "06_Templates_and_Tools/AshvalPrompt.md": "08_Templates-Tools/Prompts/General/AshvalPrompt.md",
        "06_Templates_and_Tools/master_prompt.json": "08_Templates-Tools/Prompts/General/master_prompt.json",
        "06_Templates_and_Tools/scene_prompt.json": "08_Templates-Tools/Prompts/General/scene_prompt.json",
        "06_Templates_and_Tools/scoring_prompt.json": "08_Templates-Tools/Prompts/General/scoring_prompt.json",
        "06_Templates_and_Tools/Summerize_Geminiv3.md": "08_Templates-Tools/Prompts/General/Summerize_Geminiv3.md",
        "06_Templates_and_Tools/GeminiTagger.md": "08_Templates-Tools/Prompts/General/GeminiTagger.md",
        "06_Templates_and_Tools/askGPT4.md": "08_Templates-Tools/Prompts/General/askGPT4.md",
        "06_Templates_and_Tools/describe_Images.md": "08_Templates-Tools/Prompts/General/describe_Images.md",
        "06_Templates_and_Tools/stability.md": "08_Templates-Tools/Prompts/General/stability.md",
        
        # ย้าย Default Prompts
        "06_Templates_and_Tools/default/getOutline.md": "08_Templates-Tools/Prompts/Default_Prompts/getOutline.md",
        "06_Templates_and_Tools/default/getTitles.md": "08_Templates-Tools/Prompts/Default_Prompts/getTitles.md",
        "06_Templates_and_Tools/default/getParagraph.md": "08_Templates-Tools/Prompts/Default_Prompts/getParagraph.md",
        "06_Templates_and_Tools/default/getTags.md": "08_Templates-Tools/Prompts/Default_Prompts/getTags.md",
        "06_Templates_and_Tools/default/getIdeas.md": "08_Templates-Tools/Prompts/Default_Prompts/getIdeas.md",
        "06_Templates_and_Tools/default/summarize.md": "08_Templates-Tools/Prompts/Default_Prompts/summarize.md",
        "06_Templates_and_Tools/default/simplify.md": "08_Templates-Tools/Prompts/Default_Prompts/simplify.md",
        "06_Templates_and_Tools/default/rewrite.md": "08_Templates-Tools/Prompts/Default_Prompts/rewrite.md",
        "06_Templates_and_Tools/default/getEmailNeg.md": "08_Templates-Tools/Prompts/Default_Prompts/getEmailNeg.md",
        "06_Templates_and_Tools/default/getEmailPos.md": "08_Templates-Tools/Prompts/Default_Prompts/getEmailPos.md",
        "06_Templates_and_Tools/default/summarizeLarge.md": "08_Templates-Tools/Prompts/Default_Prompts/summarizeLarge.md",
        
        # ย้าย Smart Connections
        "06_Templates_and_Tools/smart_connections/summarize.md": "08_Templates-Tools/Prompts/Smart_Connections/summarize.md",
        
        # ย้าย Document Templates
        "06_Templates_and_Tools/Character_Template.md": "08_Templates-Tools/Document_Templates/Character_Template.md",
        "06_Templates_and_Tools/PlotOutline.md": "08_Templates-Tools/Document_Templates/PlotOutline.md",
        "06_Templates_and_Tools/SceneTemplate.md": "08_Templates-Tools/Document_Templates/SceneTemplate.md",
        "06_Templates_and_Tools/Template_YAML.md": "08_Templates-Tools/Document_Templates/Template_YAML.md",
        "06_Templates_and_Tools/chapter_template.json": "08_Templates-Tools/Document_Templates/chapter_template.json",
        "06_Templates_and_Tools/INDEX_Template.md": "08_Templates-Tools/Document_Templates/INDEX_Template.md",
        "06_Templates_and_Tools/Locations.md": "08_Templates-Tools/Document_Templates/Locations.md",
        "06_Templates_and_Tools/Note.md": "08_Templates-Tools/Document_Templates/Note.md",
        "06_Templates_and_Tools/DailyReport.md": "08_Templates-Tools/Document_Templates/DailyReport.md",
        "06_Templates_and_Tools/Draft-All-V3.md": "08_Templates-Tools/Document_Templates/Draft-All-V3.md",
        "06_Templates_and_Tools/TableOfContents-VbX.md": "08_Templates-Tools/Document_Templates/TableOfContents-VbX.md",
        "06_Templates_and_Tools/location_template.md": "08_Templates-Tools/Document_Templates/location_template.md",
        
        # ย้าย Tools and Utilities
        "06_Templates_and_Tools/APIHealthCheck.md": "08_Templates-Tools/Tools_and_Utilities/APIHealthCheck.md",
        "06_Templates_and_Tools/AshvalWriter.md": "08_Templates-Tools/Tools_and_Utilities/AshvalWriter.md",
        "06_Templates_and_Tools/Automated Document Processing Template.md": "08_Templates-Tools/Tools_and_Utilities/Automated Document Processing Template.md",
        "06_Templates_and_Tools/Automated Scene Merger-V5.md.md": "08_Templates-Tools/Tools_and_Utilities/Automated Scene Merger-V5.md.md",
        "06_Templates_and_Tools/DuplicateFinder.md": "08_Templates-Tools/Tools_and_Utilities/DuplicateFinder.md",
        "06_Templates_and_Tools/FileRename.md": "08_Templates-Tools/Tools_and_Utilities/FileRename.md",
        "06_Templates_and_Tools/Find_Vault.md": "08_Templates-Tools/Tools_and_Utilities/Find_Vault.md",
        "06_Templates_and_Tools/Generat_Index_V2.md": "08_Templates-Tools/Tools_and_Utilities/Generat_Index_V2.md",
        "06_Templates_and_Tools/Validator.md": "08_Templates-Tools/Tools_and_Utilities/Validator.md",
        "06_Templates_and_Tools/renamev2.md": "08_Templates-Tools/Tools_and_Utilities/renamev2.md",
        "06_Templates_and_Tools/fix_bad_scene_model.md": "08_Templates-Tools/Tools_and_Utilities/fix_bad_scene_model.md",
        "06_Templates_and_Tools/textgenerator.md": "08_Templates-Tools/Tools_and_Utilities/textgenerator.md",
        "06_Templates_and_Tools/สร้างภาพv11.md": "08_Templates-Tools/Tools_and_Utilities/สร้างภาพv11.md",
        "06_Templates_and_Tools/แก้ไขไฟล์มาสเตอร์.md": "08_Templates-Tools/Tools_and_Utilities/แก้ไขไฟล์มาสเตอร์.md",
        "06_Templates_and_Tools/ค้นหาแบบยาว.md": "08_Templates-Tools/Tools_and_Utilities/ค้นหาแบบยาว.md",
        "06_Templates_and_Tools/ตรวจไฟล์ซ้ำซ้อน.md": "08_Templates-Tools/Tools_and_Utilities/ตรวจไฟล์ซ้ำซ้อน.md",
        "06_Templates_and_Tools/แก้ไขไฟล์มาสเตอร์ 2.md": "08_Templates-Tools/Tools_and_Utilities/แก้ไขไฟล์มาสเตอร์ 2.md",
        
        # ย้าย Databases
        "06_Templates_and_Tools/ArcanaDatabase.md": "08_Templates-Tools/Databases/ArcanaDatabase.md"
    }
    
    # ไฟล์ซ้ำซ้อนที่จะลบ
    duplicate_files = [
        "06_Templates_and_Tools/textgenerator/fix_bad_scene_model.md",
        "06_Templates_and_Tools/textgenerator/local/แก้ไขไฟล์มาสเตอร์.md",
        "06_Templates_and_Tools/textgenerator/generations/TableOfContents-VbX.md"
    ]
    
    # เริ่มการจัดการไฟล์
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    manager = SimpleFileManager(vault_path)
    
    print("🎯 เริ่มจัดการโครงสร้างไฟล์ Obsidian Vault")
    print("=" * 50)
    
    # 1. วิเคราะห์โครงสร้างปัจจุบัน
    print("📊 วิเคราะห์โครงสร้างปัจจุบัน...")
    current_report = manager.analyze_current_structure()
    print(f"พบไฟล์และโฟลเดอร์ทั้งหมด: {current_report['total_items']} รายการ")
    
    # 2. สร้างโครงสร้างใหม่
    print("\n🏗️ สร้างโครงสร้างใหม่...")
    if manager.create_new_structure(new_structure):
        print("✅ สร้างโครงสร้างใหม่สำเร็จ")
    else:
        print("❌ เกิดข้อผิดพลาดในการสร้างโครงสร้าง")
        return
    
    # 3. ย้ายไฟล์
    print("\n📁 ย้ายไฟล์ไปยังโครงสร้างใหม่...")
    if manager.move_files_to_new_structure(file_mapping):
        print("✅ ย้ายไฟล์สำเร็จ")
    else:
        print("❌ เกิดข้อผิดพลาดในการย้ายไฟล์")
    
    # 4. ลบไฟล์ซ้ำซ้อน
    print("\n🗑️ ลบไฟล์ซ้ำซ้อน...")
    if manager.remove_duplicate_files(duplicate_files):
        print("✅ ลบไฟล์ซ้ำซ้อนสำเร็จ")
    else:
        print("❌ เกิดข้อผิดพลาดในการลบไฟล์")
    
    # 5. สร้างรายงาน
    print("\n📄 สร้างรายงาน...")
    final_report = manager.generate_structure_report()
    manager.save_report(final_report, "vault_restructure_report.json")
    
    print("\n🎉 การจัดการโครงสร้างไฟล์เสร็จสิ้น!")
    print("=" * 50)
    print(f"📊 สรุปการทำงาน:")
    print(f"   - ไฟล์และโฟลเดอร์ทั้งหมด: {final_report['files_count'] + final_report['folders_count']}")
    print(f"   - การดำเนินการที่ทำ: {len(final_report['operations_performed'])} รายการ")
    print(f"   - รายงานถูกบันทึกใน: vault_restructure_report.json")

if __name__ == "__main__":
    main()
