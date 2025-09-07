#!/usr/bin/env python3
"""
Dataset Generator for File System MCP Tool Training
เครื่องกำเนิดชุดข้อมูลสำหรับฝึก AI Agent ให้เข้าใจวิธีการใช้เครื่องมือจัดการไฟล์
"""

import json
import random
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path
import os

class FileSystemDatasetGenerator:
    """เครื่องกำเนิดชุดข้อมูลสำหรับฝึก AI Agent"""
    
    def __init__(self, db_path: str = "file_system_analysis.db"):
        self.db_path = db_path
        self.dataset = []
        
    def generate_training_dataset(self, output_file: str = "file_system_training_dataset.json"):
        """สร้างชุดข้อมูลสำหรับฝึก AI Agent"""
        print("🚀 เริ่มสร้างชุดข้อมูลสำหรับฝึก AI Agent...")
        
        # 1. สร้างชุดข้อมูลพื้นฐาน
        self._generate_basic_queries()
        
        # 2. สร้างชุดข้อมูลการค้นหาไฟล์
        self._generate_file_search_queries()
        
        # 3. สร้างชุดข้อมูลการวิเคราะห์
        self._generate_analysis_queries()
        
        # 4. สร้างชุดข้อมูล SQL queries
        self._generate_sql_queries()
        
        # 5. สร้างชุดข้อมูลการจัดการไฟล์
        self._generate_file_management_queries()
        
        # 6. สร้างชุดข้อมูลการรายงาน
        self._generate_reporting_queries()
        
        # 7. บันทึกชุดข้อมูล
        self._save_dataset(output_file)
        
        print(f"✅ สร้างชุดข้อมูลสำเร็จ: {len(self.dataset)} รายการ")
        print(f"📁 บันทึกไปยัง: {output_file}")
        
    def _generate_basic_queries(self):
        """สร้างชุดข้อมูลพื้นฐาน"""
        basic_queries = [
            {
                "instruction": "สรุปข้อมูลโฟลเดอร์นี้ให้ที",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": "scan_xxx",
                    "args": []
                },
                "category": "basic",
                "description": "ขอสรุปข้อมูลพื้นฐานของโฟลเดอร์"
            },
            {
                "instruction": "มีไฟล์ทั้งหมดกี่ไฟล์ในโฟลเดอร์นี้",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as total_files FROM files WHERE session_id = ?",
                    "params": ["scan_xxx"]
                },
                "category": "basic",
                "description": "นับจำนวนไฟล์ทั้งหมด"
            },
            {
                "instruction": "ขนาดรวมของโฟลเดอร์เท่าไหร่",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT SUM(file_size) as total_size FROM files WHERE session_id = ?",
                    "params": ["scan_xxx"]
                },
                "category": "basic",
                "description": "คำนวณขนาดรวมของโฟลเดอร์"
            },
            {
                "instruction": "แสดงไฟล์ที่ใหญ่ที่สุด 10 ไฟล์",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_largest_files",
                    "session_id": "scan_xxx",
                    "args": [10]
                },
                "category": "basic",
                "description": "แสดงไฟล์ขนาดใหญ่ที่สุด"
            },
            {
                "instruction": "มีไฟล์ซ้ำกันไหม",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": []
                },
                "category": "basic",
                "description": "ตรวจสอบไฟล์ซ้ำ"
            }
        ]
        
        self.dataset.extend(basic_queries)
        
    def _generate_file_search_queries(self):
        """สร้างชุดข้อมูลการค้นหาไฟล์"""
        file_search_queries = [
            {
                "instruction": "หาไฟล์เอกสาร Word ที่ใหญ่ที่สุด 5 ไฟล์ให้หน่อย",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_extension = '.docx' ORDER BY file_size DESC LIMIT 5",
                    "params": ["scan_xxx"]
                },
                "category": "file_search",
                "description": "ค้นหาไฟล์ Word ขนาดใหญ่"
            },
            {
                "instruction": "แสดงไฟล์รูปภาพทั้งหมด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND mime_type LIKE 'image/%'",
                    "params": ["scan_xxx"]
                },
                "category": "file_search",
                "description": "ค้นหาไฟล์รูปภาพ"
            },
            {
                "instruction": "มีไฟล์ PDF กี่ไฟล์ในระบบ",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as pdf_count FROM files WHERE session_id = ? AND file_extension = '.pdf'",
                    "params": ["scan_xxx"]
                },
                "category": "file_search",
                "description": "นับไฟล์ PDF"
            },
            {
                "instruction": "แสดงไฟล์ทั้งหมดที่ชื่อมีคำว่า 'report' และเป็นไฟล์ PDF",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_path FROM files WHERE session_id = ? AND file_name LIKE '%report%' AND file_extension = '.pdf'",
                    "params": ["scan_xxx"]
                },
                "category": "file_search",
                "description": "ค้นหาไฟล์ PDF ที่มีคำว่า report"
            },
            {
                "instruction": "หาไฟล์โค้ด Python ที่ใหญ่ที่สุด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_extension = '.py' ORDER BY file_size DESC LIMIT 1",
                    "params": ["scan_xxx"]
                },
                "category": "file_search",
                "description": "ค้นหาไฟล์ Python ขนาดใหญ่ที่สุด"
            },
            {
                "instruction": "แสดงไฟล์ JavaScript ทั้งหมด",
                "correct_action": {
                    "action": "query_function",
                    "function": "find_files_by_extension",
                    "session_id": "scan_xxx",
                    "args": [".js"]
                },
                "category": "file_search",
                "description": "ค้นหาไฟล์ JavaScript"
            },
            {
                "instruction": "ไฟล์ไหนที่ซ้ำกันแล้วเปลืองเนื้อที่มากที่สุด",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": []
                },
                "category": "file_search",
                "description": "ตรวจสอบไฟล์ซ้ำที่เปลืองพื้นที่"
            }
        ]
        
        self.dataset.extend(file_search_queries)
        
    def _generate_analysis_queries(self):
        """สร้างชุดข้อมูลการวิเคราะห์"""
        analysis_queries = [
            {
                "instruction": "วิเคราะห์ประเภทไฟล์ที่พบในโฟลเดอร์",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, COUNT(*) as count, SUM(file_size) as total_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC",
                    "params": ["scan_xxx"]
                },
                "category": "analysis",
                "description": "วิเคราะห์ประเภทไฟล์"
            },
            {
                "instruction": "ไฟล์ประเภทไหนที่ใช้พื้นที่มากที่สุด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, SUM(file_size) as total_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY total_size DESC LIMIT 5",
                    "params": ["scan_xxx"]
                },
                "category": "analysis",
                "description": "วิเคราะห์ไฟล์ที่ใช้พื้นที่มาก"
            },
            {
                "instruction": "มีไฟล์ที่ซ่อนอยู่กี่ไฟล์",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT COUNT(*) as hidden_count FROM files WHERE session_id = ? AND is_hidden = 1",
                    "params": ["scan_xxx"]
                },
                "category": "analysis",
                "description": "นับไฟล์ซ่อน"
            },
            {
                "instruction": "ไฟล์ไหนที่เก่าที่สุด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, created_date FROM files WHERE session_id = ? ORDER BY created_date ASC LIMIT 10",
                    "params": ["scan_xxx"]
                },
                "category": "analysis",
                "description": "หาไฟล์เก่าที่สุด"
            },
            {
                "instruction": "ไฟล์ไหนที่แก้ไขล่าสุด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, modified_date FROM files WHERE session_id = ? ORDER BY modified_date DESC LIMIT 10",
                    "params": ["scan_xxx"]
                },
                "category": "analysis",
                "description": "หาไฟล์ที่แก้ไขล่าสุด"
            }
        ]
        
        self.dataset.extend(analysis_queries)
        
    def _generate_sql_queries(self):
        """สร้างชุดข้อมูล SQL queries"""
        sql_queries = [
            {
                "instruction": "แสดงไฟล์ที่มีขนาดมากกว่า 100MB",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_size > 104857600 ORDER BY file_size DESC",
                    "params": ["scan_xxx"]
                },
                "category": "sql",
                "description": "ค้นหาไฟล์ขนาดใหญ่"
            },
            {
                "instruction": "ไฟล์รูปภาพที่มีขนาดมากกว่า 10MB มีอะไรบ้าง",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND mime_type LIKE 'image/%' AND file_size > 10485760",
                    "params": ["scan_xxx"]
                },
                "category": "sql",
                "description": "ค้นหารูปภาพขนาดใหญ่"
            },
            {
                "instruction": "แสดงไฟล์ที่สร้างในเดือนนี้",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, created_date FROM files WHERE session_id = ? AND created_date >= date('now', 'start of month')",
                    "params": ["scan_xxx"]
                },
                "category": "sql",
                "description": "หาไฟล์ที่สร้างในเดือนปัจจุบัน"
            },
            {
                "instruction": "ไฟล์ที่แก้ไขในสัปดาห์นี้มีอะไรบ้าง",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, modified_date FROM files WHERE session_id = ? AND modified_date >= date('now', '-7 days')",
                    "params": ["scan_xxx"]
                },
                "category": "sql",
                "description": "หาไฟล์ที่แก้ไขในสัปดาห์นี้"
            },
            {
                "instruction": "แสดงไฟล์ที่ไม่มีนามสกุล",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND (file_extension = '' OR file_extension IS NULL)",
                    "params": ["scan_xxx"]
                },
                "category": "sql",
                "description": "หาไฟล์ที่ไม่มีนามสกุล"
            }
        ]
        
        self.dataset.extend(sql_queries)
        
    def _generate_file_management_queries(self):
        """สร้างชุดข้อมูลการจัดการไฟล์"""
        management_queries = [
            {
                "instruction": "ไฟล์ไหนที่ควรลบเพื่อประหยัดพื้นที่",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, file_size FROM files WHERE session_id = ? AND file_size > 52428800 ORDER BY file_size DESC LIMIT 20",
                    "params": ["scan_xxx"]
                },
                "category": "management",
                "description": "หาไฟล์ที่ควรลบ"
            },
            {
                "instruction": "มีไฟล์ชั่วคราวอะไรบ้าง",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND (file_name LIKE '%.tmp' OR file_name LIKE 'temp%' OR file_name LIKE '%cache%')",
                    "params": ["scan_xxx"]
                },
                "category": "management",
                "description": "หาไฟล์ชั่วคราว"
            },
            {
                "instruction": "ไฟล์ไหนที่เข้าถึงล่าสุด",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path, accessed_date FROM files WHERE session_id = ? ORDER BY accessed_date DESC LIMIT 10",
                    "params": ["scan_xxx"]
                },
                "category": "management",
                "description": "หาไฟล์ที่เข้าถึงล่าสุด"
            },
            {
                "instruction": "แสดงไฟล์ที่อาจเป็นไวรัส",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_name, file_path FROM files WHERE session_id = ? AND file_extension IN ('.exe', '.bat', '.cmd', '.scr', '.pif')",
                    "params": ["scan_xxx"]
                },
                "category": "management",
                "description": "หาไฟล์ที่อาจเป็นไวรัส"
            }
        ]
        
        self.dataset.extend(management_queries)
        
    def _generate_reporting_queries(self):
        """สร้างชุดข้อมูลการรายงาน"""
        reporting_queries = [
            {
                "instruction": "สร้างรายงานสรุปโฟลเดอร์",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_directory_summary",
                    "session_id": "scan_xxx",
                    "args": []
                },
                "category": "reporting",
                "description": "สร้างรายงานสรุป"
            },
            {
                "instruction": "รายงานไฟล์ที่ใหญ่ที่สุด 20 ไฟล์",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_largest_files",
                    "session_id": "scan_xxx",
                    "args": [20]
                },
                "category": "reporting",
                "description": "รายงานไฟล์ขนาดใหญ่"
            },
            {
                "instruction": "รายงานไฟล์ซ้ำทั้งหมด",
                "correct_action": {
                    "action": "query_function",
                    "function": "get_duplicate_files",
                    "session_id": "scan_xxx",
                    "args": []
                },
                "category": "reporting",
                "description": "รายงานไฟล์ซ้ำ"
            },
            {
                "instruction": "สถิติประเภทไฟล์",
                "correct_action": {
                    "action": "query_sql",
                    "sql": "SELECT file_extension, COUNT(*) as count, AVG(file_size) as avg_size FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC",
                    "params": ["scan_xxx"]
                },
                "category": "reporting",
                "description": "สถิติประเภทไฟล์"
            }
        ]
        
        self.dataset.extend(reporting_queries)
        
    def _save_dataset(self, output_file: str):
        """บันทึกชุดข้อมูล"""
        dataset_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(self.dataset),
                "categories": list(set(item["category"] for item in self.dataset)),
                "description": "Dataset สำหรับฝึก AI Agent ให้เข้าใจการใช้ File System MCP Tool"
            },
            "dataset": self.dataset
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
            
    def generate_variations(self, base_dataset_file: str, output_file: str = "expanded_dataset.json"):
        """สร้างชุดข้อมูลที่มีความหลากหลายมากขึ้น"""
        print("🔄 สร้างชุดข้อมูลที่มีความหลากหลาย...")
        
        with open(base_dataset_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
            
        expanded_dataset = base_data["dataset"].copy()
        
        # สร้างความหลากหลายของคำสั่ง
        variations = [
            ("แสดงไฟล์ขนาดใหญ่", ["แสดงไฟล์ที่ใหญ่ที่สุด", "ไฟล์ไหนใหญ่ที่สุด", "ไฟล์ขนาดใหญ่มีอะไรบ้าง"]),
            ("หาไฟล์ซ้ำ", ["มีไฟล์ซ้ำไหม", "ไฟล์ไหนซ้ำกัน", "ตรวจสอบไฟล์ซ้ำ"]),
            ("สรุปข้อมูล", ["สรุปโฟลเดอร์", "ข้อมูลสรุป", "รายงานสรุป"]),
            ("ไฟล์รูปภาพ", ["รูปภาพทั้งหมด", "ไฟล์รูป", "รูปมีอะไรบ้าง"]),
            ("ไฟล์เอกสาร", ["ไฟล์ Word", "เอกสารทั้งหมด", "ไฟล์ .docx"])
        ]
        
        for original, variations_list in variations:
            for variation in variations_list:
                # หา entry ที่ตรงกับ original
                for entry in base_data["dataset"]:
                    if original in entry["instruction"]:
                        new_entry = entry.copy()
                        new_entry["instruction"] = entry["instruction"].replace(original, variation)
                        new_entry["category"] = "variation"
                        expanded_dataset.append(new_entry)
                        
        # บันทึกชุดข้อมูลที่ขยายแล้ว
        expanded_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(expanded_dataset),
                "base_samples": len(base_data["dataset"]),
                "variations_added": len(expanded_dataset) - len(base_data["dataset"]),
                "description": "Expanded dataset with variations"
            },
            "dataset": expanded_dataset
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(expanded_info, f, ensure_ascii=False, indent=2)
            
        print(f"✅ สร้างชุดข้อมูลขยายสำเร็จ: {len(expanded_dataset)} รายการ")
        
    def generate_test_dataset(self, training_dataset_file: str, output_file: str = "test_dataset.json"):
        """สร้างชุดข้อมูลสำหรับทดสอบ"""
        print("🧪 สร้างชุดข้อมูลสำหรับทดสอบ...")
        
        with open(training_dataset_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
            
        # สุ่มเลือก 20% สำหรับทดสอบ
        test_samples = random.sample(training_data["dataset"], 
                                   min(len(training_data["dataset"]) // 5, 50))
        
        test_info = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_samples": len(test_samples),
                "source": training_dataset_file,
                "description": "Test dataset for File System MCP Tool"
            },
            "dataset": test_samples
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_info, f, ensure_ascii=False, indent=2)
            
        print(f"✅ สร้างชุดข้อมูลทดสอบสำเร็จ: {len(test_samples)} รายการ")
        
    def analyze_dataset(self, dataset_file: str):
        """วิเคราะห์ชุดข้อมูล"""
        print(f"📊 วิเคราะห์ชุดข้อมูล: {dataset_file}")
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        dataset = data["dataset"]
        
        # วิเคราะห์ตามหมวดหมู่
        categories = {}
        for item in dataset:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
            
        print("\n📈 สถิติชุดข้อมูล:")
        print(f"• จำนวนตัวอย่างทั้งหมด: {len(dataset)}")
        print(f"• จำนวนหมวดหมู่: {len(categories)}")
        
        print("\n📋 หมวดหมู่:")
        for cat, count in sorted(categories.items()):
            percentage = (count / len(dataset)) * 100
            print(f"  • {cat}: {count} ({percentage:.1f}%)")
            
        # วิเคราะห์ actions
        actions = {}
        for item in dataset:
            action = item["correct_action"]["action"]
            if action not in actions:
                actions[action] = 0
            actions[action] += 1
            
        print("\n🔧 Actions ที่ใช้:")
        for action, count in sorted(actions.items()):
            percentage = (count / len(dataset)) * 100
            print(f"  • {action}: {count} ({percentage:.1f}%)")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 File System MCP Dataset Generator")
    print("=" * 50)
    
    generator = FileSystemDatasetGenerator()
    
    # สร้างชุดข้อมูลพื้นฐาน
    generator.generate_training_dataset("file_system_training_dataset.json")
    
    # สร้างชุดข้อมูลขยาย
    generator.generate_variations("file_system_training_dataset.json", "expanded_dataset.json")
    
    # สร้างชุดข้อมูลทดสอบ
    generator.generate_test_dataset("file_system_training_dataset.json", "test_dataset.json")
    
    # วิเคราะห์ชุดข้อมูล
    print("\n" + "=" * 50)
    generator.analyze_dataset("file_system_training_dataset.json")
    
    print("\n" + "=" * 50)
    generator.analyze_dataset("expanded_dataset.json")
    
    print("\n" + "=" * 50)
    generator.analyze_dataset("test_dataset.json")
    
    print("\n🎉 สร้างชุดข้อมูลเสร็จสิ้น!")
    print("\n📁 ไฟล์ที่สร้าง:")
    print("  • file_system_training_dataset.json - ชุดข้อมูลพื้นฐาน")
    print("  • expanded_dataset.json - ชุดข้อมูลขยาย")
    print("  • test_dataset.json - ชุดข้อมูลทดสอบ")

if __name__ == "__main__":
    main()
