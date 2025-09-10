#!/usr/bin/env python3
"""
Auto Vault Watcher - เครื่องมือเฝ้ามองและจัดระเบียบไฟล์อัตโนมัติ
"""

import os
import time
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileMovedEvent
import threading
import queue

class VaultFileHandler(FileSystemEventHandler):
    """จัดการเหตุการณ์การเปลี่ยนแปลงไฟล์"""
    
    def __init__(self, vault_manager: 'AutoVaultWatcher'):
        self.vault_manager = vault_manager
        self.pending_files: Set[str] = set()
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.start_processing_thread()
    
    def start_processing_thread(self):
        """เริ่ม thread สำหรับประมวลผลไฟล์"""
        self.processing_thread = threading.Thread(target=self._process_files_worker, daemon=True)
        self.processing_thread.start()
    
    def _process_files_worker(self):
        """Worker thread สำหรับประมวลผลไฟล์"""
        while True:
            try:
                file_path = self.processing_queue.get(timeout=1)
                if file_path is None:  # Signal to stop
                    break
                
                self.vault_manager.process_file(file_path)
                self.processing_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {e}")
    
    def on_created(self, event):
        """เมื่อสร้างไฟล์ใหม่"""
        if not event.is_directory and self._is_target_file(event.src_path):
            self._handle_file_event(event.src_path, "created")
    
    def on_modified(self, event):
        """เมื่อแก้ไขไฟล์"""
        if not event.is_directory and self._is_target_file(event.src_path):
            self._handle_file_event(event.src_path, "modified")
    
    def on_moved(self, event):
        """เมื่อย้ายไฟล์"""
        if not event.is_directory and self._is_target_file(event.dest_path):
            self._handle_file_event(event.dest_path, "moved")
    
    def _is_target_file(self, file_path: str) -> bool:
        """ตรวจสอบว่าเป็นไฟล์ที่ต้องการติดตามหรือไม่"""
        path = Path(file_path)
        return path.suffix.lower() in ['.txt', '.md', '.json']
    
    def _handle_file_event(self, file_path: str, event_type: str):
        """จัดการเหตุการณ์ไฟล์"""
        try:
            # รอสักครู่ให้ไฟล์เสร็จการเขียน
            time.sleep(0.5)
            
            if os.path.exists(file_path):
                # เพิ่มลงคิวสำหรับประมวลผล
                self.processing_queue.put(file_path)
                logging.info(f"Queued file for processing: {file_path} ({event_type})")
                
        except Exception as e:
            logging.error(f"Error handling file event {file_path}: {e}")

class AutoVaultWatcher:
    """เครื่องมือเฝ้ามองและจัดระเบียบ Vault อัตโนมัติ"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.observer = Observer()
        self.file_handler = VaultFileHandler(self)
        self.running = False
        
        # ตั้งค่า logging
        self._setup_logging()
        
        # โหลดการตั้งค่า
        self.config = self._load_config()
        
        # สถิติการทำงาน
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'files_organized': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def _setup_logging(self):
        """ตั้งค่า logging"""
        log_dir = self.vault_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"vault_watcher_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        config_file = self.vault_path / "vault_watcher_config.json"
        
        default_config = {
            'watch_extensions': ['.txt', '.md', '.json'],
            'auto_organize': True,
            'move_duplicates': True,
            'create_readme': True,
            'organize_rules': {
                'prompts': ['prompt', 'copilot', 'template'],
                'templates': ['template', 'form', 'format'],
                'tools': ['tool', 'utility', 'script'],
                'notes': ['note', 'memo', 'idea'],
                'data': ['data', 'database', 'config']
            },
            'target_folders': {
                'prompts': '08_Templates-Tools/Prompts/General',
                'templates': '08_Templates-Tools/Document_Templates',
                'tools': '08_Templates-Tools/Tools_and_Utilities',
                'notes': '06_NOTE',
                'data': '08_Templates-Tools/Databases'
            },
            'exclude_patterns': ['temp', 'tmp', 'backup', 'old'],
            'min_file_size': 10  # bytes
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        
        return default_config
    
    def start_watching(self):
        """เริ่มการเฝ้ามอง"""
        try:
            logging.info("🚀 เริ่ม Auto Vault Watcher...")
            logging.info(f"📁 เฝ้ามอง: {self.vault_path}")
            logging.info(f"📋 การตั้งค่า: {json.dumps(self.config, ensure_ascii=False, indent=2)}")
            
            # เริ่ม observer
            self.observer.schedule(self.file_handler, str(self.vault_path), recursive=True)
            self.observer.start()
            
            self.running = True
            logging.info("✅ เริ่มการเฝ้ามองเรียบร้อย")
            
            # แสดงสถิติ
            self._show_status()
            
        except Exception as e:
            logging.error(f"❌ ไม่สามารถเริ่มการเฝ้ามอง: {e}")
            raise
    
    def stop_watching(self):
        """หยุดการเฝ้ามอง"""
        try:
            logging.info("🛑 หยุดการเฝ้ามอง...")
            
            self.running = False
            
            # หยุด observer
            self.observer.stop()
            self.observer.join()
            
            # ส่งสัญญาณหยุด worker thread
            self.file_handler.processing_queue.put(None)
            if self.file_handler.processing_thread:
                self.file_handler.processing_thread.join(timeout=5)
            
            # บันทึกสถิติ
            self._save_stats()
            
            logging.info("✅ หยุดการเฝ้ามองเรียบร้อย")
            
        except Exception as e:
            logging.error(f"❌ ไม่สามารถหยุดการเฝ้ามอง: {e}")
    
    def process_file(self, file_path: str):
        """ประมวลผลไฟล์"""
        try:
            path = Path(file_path)
            
            # ตรวจสอบว่าเป็นไฟล์ที่ต้องการหรือไม่
            if not self._should_process_file(path):
                return
            
            logging.info(f"🔍 ประมวลผลไฟล์: {path.name}")
            
            # ตรวจสอบขนาดไฟล์
            if path.stat().st_size < self.config['min_file_size']:
                logging.info(f"⏭️ ข้ามไฟล์เล็กเกินไป: {path.name}")
                return
            
            # ตรวจสอบว่าไฟล์อยู่ในตำแหน่งที่ถูกต้องหรือไม่
            if self._is_in_correct_location(path):
                logging.info(f"✅ ไฟล์อยู่ในตำแหน่งที่ถูกต้อง: {path.name}")
                return
            
            # จัดระเบียบไฟล์
            if self.config['auto_organize']:
                self._organize_file(path)
            
            self.stats['files_processed'] += 1
            
        except Exception as e:
            logging.error(f"❌ เกิดข้อผิดพลาดในการประมวลผล {file_path}: {e}")
            self.stats['errors'] += 1
    
    def _should_process_file(self, file_path: Path) -> bool:
        """ตรวจสอบว่าควรประมวลผลไฟล์หรือไม่"""
        # ตรวจสอบนามสกุลไฟล์
        if file_path.suffix.lower() not in self.config['watch_extensions']:
            return False
        
        # ตรวจสอบรูปแบบที่ต้องยกเว้น
        for pattern in self.config['exclude_patterns']:
            if pattern.lower() in file_path.name.lower():
                return False
        
        # ตรวจสอบว่าไม่ใช่ไฟล์ระบบ
        if file_path.name.startswith('.'):
            return False
        
        return True
    
    def _is_in_correct_location(self, file_path: Path) -> bool:
        """ตรวจสอบว่าไฟล์อยู่ในตำแหน่งที่ถูกต้องหรือไม่"""
        try:
            # ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์หลักหรือไม่
            main_folders = [
                '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS',
                '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
                '08_Templates-Tools'
            ]
            
            # ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ย่อยของ Templates-Tools หรือไม่
            templates_subfolders = [
                'Prompts/General', 'Prompts/Default_Prompts', 'Prompts/Smart_Connections',
                'Document_Templates', 'Tools_and_Utilities', 'Databases'
            ]
            
            # ตรวจสอบโฟลเดอร์หลัก
            for folder in main_folders:
                if folder in str(file_path):
                    return True
            
            # ตรวจสอบโฟลเดอร์ย่อยของ Templates-Tools
            for subfolder in templates_subfolders:
                if f'08_Templates-Tools/{subfolder}' in str(file_path):
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking file location: {e}")
            return False
    
    def _organize_file(self, file_path: Path):
        """จัดระเบียบไฟล์"""
        try:
            # กำหนดโฟลเดอร์ปลายทาง
            target_folder = self._determine_target_folder(file_path)
            
            if not target_folder:
                logging.info(f"⏭️ ไม่สามารถกำหนดโฟลเดอร์ปลายทาง: {file_path.name}")
                return
            
            # สร้างโฟลเดอร์ปลายทาง
            target_path = self.vault_path / target_folder
            target_path.mkdir(parents=True, exist_ok=True)
            
            # ตรวจสอบไฟล์ซ้ำ
            target_file = target_path / file_path.name
            if target_file.exists():
                if self.config['move_duplicates']:
                    # เปลี่ยนชื่อไฟล์
                    new_name = self._generate_unique_name(target_file)
                    target_file = target_path / new_name
                    logging.info(f"🔄 เปลี่ยนชื่อไฟล์ซ้ำ: {file_path.name} -> {new_name}")
                else:
                    logging.info(f"⏭️ ข้ามไฟล์ซ้ำ: {file_path.name}")
                    return
            
            # ย้ายไฟล์
            shutil.move(str(file_path), str(target_file))
            
            logging.info(f"✅ ย้ายไฟล์: {file_path.name} -> {target_folder}")
            
            self.stats['files_moved'] += 1
            self.stats['files_organized'] += 1
            
            # สร้าง README ถ้าจำเป็น
            if self.config['create_readme']:
                self._ensure_readme_exists(target_path)
            
        except Exception as e:
            logging.error(f"❌ เกิดข้อผิดพลาดในการจัดระเบียบ {file_path}: {e}")
            self.stats['errors'] += 1
    
    def _determine_target_folder(self, file_path: Path) -> Optional[str]:
        """กำหนดโฟลเดอร์ปลายทาง"""
        try:
            file_name = file_path.name.lower()
            file_content = ""
            
            # อ่านเนื้อหาไฟล์เพื่อวิเคราะห์
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read(1000).lower()  # อ่าน 1000 ตัวอักษรแรก
            except:
                pass
            
            # ตรวจสอบตามกฎการจัดระเบียบ
            for category, keywords in self.config['organize_rules'].items():
                for keyword in keywords:
                    if keyword in file_name or keyword in file_content:
                        return self.config['target_folders'][category]
            
            # ถ้าไม่ตรงกับกฎใดๆ ให้ย้ายไป Notes
            return self.config['target_folders']['notes']
            
        except Exception as e:
            logging.error(f"Error determining target folder: {e}")
            return None
    
    def _generate_unique_name(self, file_path: Path) -> str:
        """สร้างชื่อไฟล์ที่ไม่ซ้ำ"""
        counter = 1
        name = file_path.stem
        suffix = file_path.suffix
        
        while file_path.exists():
            new_name = f"{name}_{counter}{suffix}"
            file_path = file_path.parent / new_name
            counter += 1
        
        return file_path.name
    
    def _ensure_readme_exists(self, folder_path: Path):
        """ตรวจสอบและสร้าง README ถ้าจำเป็น"""
        readme_path = folder_path / "README.md"
        
        if not readme_path.exists():
            try:
                folder_name = folder_path.name
                date = datetime.now().strftime("%Y-%m-%d")
                
                content = f"""# 📁 {folder_name.replace('_', ' ')}

## 🎯 วัตถุประสงค์
โฟลเดอร์สำหรับ {folder_name.replace('_', ' ').lower()}

## 📋 สถานะ
- [x] โฟลเดอร์พร้อมใช้งาน

## 📁 ไฟล์ในโฟลเดอร์
{self._generate_file_list(folder_path)}

---
*อัปเดตล่าสุด: {date}*
"""
                
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logging.info(f"📝 สร้าง README: {folder_path.name}")
                
            except Exception as e:
                logging.error(f"Error creating README: {e}")
    
    def _generate_file_list(self, folder_path: Path) -> str:
        """สร้างรายการไฟล์สำหรับ README"""
        try:
            files = [f for f in folder_path.iterdir() if f.is_file() and f.name != 'README.md']
            if not files:
                return "- ไม่มีไฟล์"
            
            file_list = []
            for file in sorted(files):
                file_list.append(f"- {file.name}")
            
            return '\n'.join(file_list)
            
        except Exception as e:
            logging.error(f"Error generating file list: {e}")
            return "- ไม่สามารถแสดงรายการไฟล์"
    
    def _show_status(self):
        """แสดงสถานะการทำงาน"""
        print("\n" + "="*80)
        print("🎯 Auto Vault Watcher - สถานะการทำงาน")
        print("="*80)
        print(f"📁 Vault Path: {self.vault_path}")
        print(f"🔍 เฝ้ามองไฟล์: {', '.join(self.config['watch_extensions'])}")
        print(f"🤖 จัดระเบียบอัตโนมัติ: {'✅' if self.config['auto_organize'] else '❌'}")
        print(f"📝 สร้าง README: {'✅' if self.config['create_readme'] else '❌'}")
        print(f"🔄 ย้ายไฟล์ซ้ำ: {'✅' if self.config['move_duplicates'] else '❌'}")
        print("\n💡 คำแนะนำ:")
        print("   - ทำงานเงียบๆ ในพื้นหลัง")
        print("   - จัดไฟล์อัตโนมัติเมื่อเซฟ")
        print("   - กด Ctrl+C เพื่อหยุด")
        print("="*80)
    
    def _save_stats(self):
        """บันทึกสถิติการทำงาน"""
        try:
            stats_file = self.vault_path / "vault_watcher_stats.json"
            
            stats_data = {
                'stats': self.stats,
                'config': self.config,
                'last_run': datetime.now().isoformat()
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"📊 บันทึกสถิติ: {stats_file}")
            
        except Exception as e:
            logging.error(f"Error saving stats: {e}")

def main():
    """ฟังก์ชันหลัก"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    try:
        # สร้าง watcher
        watcher = AutoVaultWatcher(vault_path)
        
        # เริ่มการเฝ้ามอง
        watcher.start_watching()
        
        # รันไปเรื่อยๆ จนกว่าจะกด Ctrl+C
        try:
            while watcher.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 ได้รับสัญญาณหยุด...")
        
        # หยุดการเฝ้ามอง
        watcher.stop_watching()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
