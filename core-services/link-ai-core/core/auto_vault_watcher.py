#!/usr/bin/env python3
"""
Auto Vault Watcher - A tool for automatically monitoring and organizing files.
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
    """
    Handles file system events.

    Attributes:
        vault_manager (AutoVaultWatcher): The vault manager instance.
        pending_files (Set[str]): A set of pending files to be processed.
        processing_queue (queue.Queue): A queue for processing files.
        processing_thread (threading.Thread): The thread for processing files.
    """
    
    def __init__(self, vault_manager: 'AutoVaultWatcher'):
        """
        Initializes the VaultFileHandler.

        Args:
            vault_manager (AutoVaultWatcher): The vault manager instance.
        """
        self.vault_manager = vault_manager
        self.pending_files: Set[str] = set()
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.start_processing_thread()
    
    def start_processing_thread(self):
        """Starts the file processing thread."""
        self.processing_thread = threading.Thread(target=self._process_files_worker, daemon=True)
        self.processing_thread.start()
    
    def _process_files_worker(self):
        """Worker thread for processing files."""
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
        """
        Handles file creation events.

        Args:
            event: The file system event.
        """
        if not event.is_directory and self._is_target_file(event.src_path):
            self._handle_file_event(event.src_path, "created")
    
    def on_modified(self, event):
        """
        Handles file modification events.

        Args:
            event: The file system event.
        """
        if not event.is_directory and self._is_target_file(event.src_path):
            self._handle_file_event(event.src_path, "modified")
    
    def on_moved(self, event):
        """
        Handles file move events.

        Args:
            event: The file system event.
        """
        if not event.is_directory and self._is_target_file(event.dest_path):
            self._handle_file_event(event.dest_path, "moved")
    
    def _is_target_file(self, file_path: str) -> bool:
        """
        Checks if a file is a target file.

        Args:
            file_path (str): The path to the file.

        Returns:
            bool: True if the file is a target file, False otherwise.
        """
        path = Path(file_path)
        return path.suffix.lower() in ['.txt', '.md', '.json']
    
    def _handle_file_event(self, file_path: str, event_type: str):
        """
        Handles a file event.

        Args:
            file_path (str): The path to the file.
            event_type (str): The type of the event.
        """
        try:
            # Wait a moment for the file to be fully written
            time.sleep(0.5)
            
            if os.path.exists(file_path):
                # Add to the queue for processing
                self.processing_queue.put(file_path)
                logging.info(f"Queued file for processing: {file_path} ({event_type})")
                
        except Exception as e:
            logging.error(f"Error handling file event {file_path}: {e}")

class AutoVaultWatcher:
    """
    A tool for automatically monitoring and organizing a vault.

    Attributes:
        vault_path (Path): The path to the vault.
        observer (Observer): The file system observer.
        file_handler (VaultFileHandler): The file system event handler.
        running (bool): A flag indicating if the watcher is running.
        config (Dict[str, Any]): The configuration for the watcher.
        stats (Dict[str, Any]): The statistics of the watcher's operation.
    """
    
    def __init__(self, vault_path: str):
        """
        Initializes the AutoVaultWatcher.

        Args:
            vault_path (str): The path to the vault.
        """
        self.vault_path = Path(vault_path)
        self.observer = Observer()
        self.file_handler = VaultFileHandler(self)
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Operation statistics
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'files_organized': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def _setup_logging(self):
        """Sets up logging."""
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
        """
        Loads the configuration.

        Returns:
            Dict[str, Any]: The configuration.
        """
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
        """Starts watching the vault."""
        try:
            logging.info("🚀 Starting Auto Vault Watcher...")
            logging.info(f"📁 Watching: {self.vault_path}")
            logging.info(f"📋 Configuration: {json.dumps(self.config, ensure_ascii=False, indent=2)}")
            
            # Start observer
            self.observer.schedule(self.file_handler, str(self.vault_path), recursive=True)
            self.observer.start()
            
            self.running = True
            logging.info("✅ Watcher started successfully")
            
            # Show status
            self._show_status()
            
        except Exception as e:
            logging.error(f"❌ Could not start watcher: {e}")
            raise
    
    def stop_watching(self):
        """Stops watching the vault."""
        try:
            logging.info("🛑 Stopping watcher...")
            
            self.running = False
            
            # Stop observer
            self.observer.stop()
            self.observer.join()
            
            # Signal the worker thread to stop
            self.file_handler.processing_queue.put(None)
            if self.file_handler.processing_thread:
                self.file_handler.processing_thread.join(timeout=5)
            
            # Save statistics
            self._save_stats()
            
            logging.info("✅ Watcher stopped successfully")
            
        except Exception as e:
            logging.error(f"❌ Could not stop watcher: {e}")
    
    def process_file(self, file_path: str):
        """
        Processes a file.

        Args:
            file_path (str): The path to the file.
        """
        try:
            path = Path(file_path)
            
            # Check if the file should be processed
            if not self._should_process_file(path):
                return
            
            logging.info(f"🔍 Processing file: {path.name}")
            
            # Check file size
            if path.stat().st_size < self.config['min_file_size']:
                logging.info(f"⏭️ Skipping small file: {path.name}")
                return
            
            # Check if the file is in the correct location
            if self._is_in_correct_location(path):
                logging.info(f"✅ File is in the correct location: {path.name}")
                return
            
            # Organize the file
            if self.config['auto_organize']:
                self._organize_file(path)
            
            self.stats['files_processed'] += 1
            
        except Exception as e:
            logging.error(f"❌ Error processing {file_path}: {e}")
            self.stats['errors'] += 1
    
    def _should_process_file(self, file_path: Path) -> bool:
        """
        Checks if a file should be processed.

        Args:
            file_path (Path): The path to the file.

        Returns:
            bool: True if the file should be processed, False otherwise.
        """
        # Check file extension
        if file_path.suffix.lower() not in self.config['watch_extensions']:
            return False
        
        # Check for excluded patterns
        for pattern in self.config['exclude_patterns']:
            if pattern.lower() in file_path.name.lower():
                return False
        
        # Check for system files
        if file_path.name.startswith('.'):
            return False
        
        return True
    
    def _is_in_correct_location(self, file_path: Path) -> bool:
        """
        Checks if a file is in the correct location.

        Args:
            file_path (Path): The path to the file.

        Returns:
            bool: True if the file is in the correct location, False otherwise.
        """
        try:
            # Check if the file is in a main folder
            main_folders = [
                '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS',
                '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
                '08_Templates-Tools'
            ]
            
            # Check if the file is in a subfolder of Templates-Tools
            templates_subfolders = [
                'Prompts/General', 'Prompts/Default_Prompts', 'Prompts/Smart_Connections',
                'Document_Templates', 'Tools_and_Utilities', 'Databases'
            ]
            
            # Check main folders
            for folder in main_folders:
                if folder in str(file_path):
                    return True
            
            # Check subfolders of Templates-Tools
            for subfolder in templates_subfolders:
                if f'08_Templates-Tools/{subfolder}' in str(file_path):
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking file location: {e}")
            return False
    
    def _organize_file(self, file_path: Path):
        """
        Organizes a file.

        Args:
            file_path (Path): The path to the file.
        """
        try:
            # Determine the target folder
            target_folder = self._determine_target_folder(file_path)
            
            if not target_folder:
                logging.info(f"⏭️ Could not determine target folder for: {file_path.name}")
                return
            
            # Create the target folder
            target_path = self.vault_path / target_folder
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Check for duplicates
            target_file = target_path / file_path.name
            if target_file.exists():
                if self.config['move_duplicates']:
                    # Rename the file
                    new_name = self._generate_unique_name(target_file)
                    target_file = target_path / new_name
                    logging.info(f"🔄 Renaming duplicate file: {file_path.name} -> {new_name}")
                else:
                    logging.info(f"⏭️ Skipping duplicate file: {file_path.name}")
                    return
            
            # Move the file
            shutil.move(str(file_path), str(target_file))
            
            logging.info(f"✅ Moved file: {file_path.name} -> {target_folder}")
            
            self.stats['files_moved'] += 1
            self.stats['files_organized'] += 1
            
            # Create README if necessary
            if self.config['create_readme']:
                self._ensure_readme_exists(target_path)
            
        except Exception as e:
            logging.error(f"❌ Error organizing {file_path}: {e}")
            self.stats['errors'] += 1
    
    def _determine_target_folder(self, file_path: Path) -> Optional[str]:
        """
        Determines the target folder for a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            Optional[str]: The target folder, or None if it cannot be determined.
        """
        try:
            file_name = file_path.name.lower()
            file_content = ""
            
            # Read file content for analysis
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read(1000).lower()  # Read the first 1000 characters
            except:
                pass
            
            # Check against organization rules
            for category, keywords in self.config['organize_rules'].items():
                for keyword in keywords:
                    if keyword in file_name or keyword in file_content:
                        return self.config['target_folders'][category]
            
            # If no rule matches, move to Notes
            return self.config['target_folders']['notes']
            
        except Exception as e:
            logging.error(f"Error determining target folder: {e}")
            return None
    
    def _generate_unique_name(self, file_path: Path) -> str:
        """
        Generates a unique name for a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            str: A unique file name.
        """
        counter = 1
        name = file_path.stem
        suffix = file_path.suffix
        
        while file_path.exists():
            new_name = f"{name}_{counter}{suffix}"
            file_path = file_path.parent / new_name
            counter += 1
        
        return file_path.name
    
    def _ensure_readme_exists(self, folder_path: Path):
        """
        Ensures that a README file exists in a folder.

        Args:
            folder_path (Path): The path to the folder.
        """
        readme_path = folder_path / "README.md"
        
        if not readme_path.exists():
            try:
                folder_name = folder_path.name
                date = datetime.now().strftime("%Y-%m-%d")
                
                content = f"""# 📁 {folder_name.replace('_', ' ')}

## 🎯 Purpose
A folder for {folder_name.replace('_', ' ').lower()}

## 📋 Status
- [x] Folder is ready for use

## 📁 Files in Folder
{self._generate_file_list(folder_path)}

---
*Last updated: {date}*
"""
                
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logging.info(f"📝 Created README: {folder_path.name}")
                
            except Exception as e:
                logging.error(f"Error creating README: {e}")
    
    def _generate_file_list(self, folder_path: Path) -> str:
        """
        Generates a list of files for the README.

        Args:
            folder_path (Path): The path to the folder.

        Returns:
            str: A string containing the list of files.
        """
        try:
            files = [f for f in folder_path.iterdir() if f.is_file() and f.name != 'README.md']
            if not files:
                return "- No files"
            
            file_list = []
            for file in sorted(files):
                file_list.append(f"- {file.name}")
            
            return '\n'.join(file_list)
            
        except Exception as e:
            logging.error(f"Error generating file list: {e}")
            return "- Could not list files"
    
    def _show_status(self):
        """Displays the status of the watcher."""
        print("\n" + "="*80)
        print("🎯 Auto Vault Watcher - Status")
        print("="*80)
        print(f"📁 Vault Path: {self.vault_path}")
        print(f"🔍 Watching files: {', '.join(self.config['watch_extensions'])}")
        print(f"🤖 Auto-organize: {'✅' if self.config['auto_organize'] else '❌'}")
        print(f"📝 Create README: {'✅' if self.config['create_readme'] else '❌'}")
        print(f"🔄 Move duplicates: {'✅' if self.config['move_duplicates'] else '❌'}")
        print("\n💡 Tips:")
        print("   - Runs silently in the background")
        print("   - Automatically organizes files on save")
        print("   - Press Ctrl+C to stop")
        print("="*80)
    
    def _save_stats(self):
        """Saves the watcher's statistics."""
        try:
            stats_file = self.vault_path / "vault_watcher_stats.json"
            
            stats_data = {
                'stats': self.stats,
                'config': self.config,
                'last_run': datetime.now().isoformat()
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"📊 Saved statistics: {stats_file}")
            
        except Exception as e:
            logging.error(f"Error saving stats: {e}")

def main():
    """Main function."""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    try:
        # Create watcher
        watcher = AutoVaultWatcher(vault_path)
        
        # Start watching
        watcher.start_watching()
        
        # Run until Ctrl+C is pressed
        try:
            while watcher.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stop signal received...")
        
        # Stop watching
        watcher.stop_watching()
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
