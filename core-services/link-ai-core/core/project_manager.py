#!/usr/bin/env python3
"""
Project Manager - เครื่องมือจัดการโปรเจ็คที่ชาญฉลาด
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

class ProjectManager:
    """เครื่องมือจัดการโปรเจ็คที่ชาญฉลาด"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config()
        self.setup_logging()
        
    def setup_logging(self):
        """ตั้งค่า logging"""
        log_dir = self.project_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"project_manager_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        config_file = self.project_path / "project_config.json"
        
        default_config = {
            'project_name': 'FileSystemMCP',
            'project_description': 'MCP Server with File Management Tools',
            'structure': {
                'src': ['core', 'services', 'tools', 'utils'],
                'docs': ['api', 'guides', 'examples'],
                'tests': ['unit', 'integration', 'e2e'],
                'scripts': ['setup', 'deploy', 'maintenance'],
                'config': ['dev', 'prod', 'test']
            },
            'file_patterns': {
                'python': ['*.py', '*.pyc', '__pycache__'],
                'config': ['*.json', '*.yaml', '*.yml', '*.toml'],
                'docs': ['*.md', '*.txt', '*.rst'],
                'logs': ['*.log', 'logs/'],
                'temp': ['*.tmp', '*.temp', '.cache/']
            },
            'organize_rules': {
                'core': ['core', 'main', 'app', 'server'],
                'services': ['service', 'api', 'endpoint'],
                'tools': ['tool', 'utility', 'helper'],
                'utils': ['util', 'helper', 'common'],
                'config': ['config', 'settings', 'env'],
                'docs': ['readme', 'documentation', 'guide']
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        
        return default_config
    
    async def analyze_project(self) -> Dict[str, Any]:
        """วิเคราะห์โครงสร้างโปรเจ็ค"""
        logging.info("🔍 วิเคราะห์โครงสร้างโปรเจ็ค...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'structure': {},
            'files': {},
            'issues': [],
            'recommendations': []
        }
        
        # วิเคราะห์โครงสร้างโฟลเดอร์
        for folder_name in self.config['structure']:
            folder_path = self.project_path / folder_name
            if folder_path.exists():
                folder_info = await self._analyze_folder(folder_path)
                analysis['structure'][folder_name] = folder_info
            else:
                analysis['issues'].append(f"Missing folder: {folder_name}")
                analysis['recommendations'].append(f"Create folder: {folder_name}")
        
        # วิเคราะห์ไฟล์ที่กระจาย
        scattered_files = await self._find_scattered_files()
        analysis['scattered_files'] = scattered_files
        
        if scattered_files:
            analysis['issues'].append(f"Found {len(scattered_files)} scattered files")
            analysis['recommendations'].append("Organize scattered files")
        
        # ตรวจสอบไฟล์จัดการ
        management_files = await self._check_management_files()
        analysis['management_files'] = management_files
        
        missing_management = [f for f, exists in management_files.items() if not exists]
        if missing_management:
            analysis['issues'].extend([f"Missing {f}" for f in missing_management])
            analysis['recommendations'].extend([f"Create {f}" for f in missing_management])
        
        return analysis
    
    async def _analyze_folder(self, folder_path: Path) -> Dict[str, Any]:
        """วิเคราะห์โฟลเดอร์เดียว"""
        files = list(folder_path.rglob("*"))
        python_files = [f for f in files if f.is_file() and f.suffix == '.py']
        config_files = [f for f in files if f.is_file() and f.suffix in ['.json', '.yaml', '.yml', '.toml']]
        doc_files = [f for f in files if f.is_file() and f.suffix in ['.md', '.txt', '.rst']]
        
        return {
            'path': str(folder_path),
            'file_count': len([f for f in files if f.is_file()]),
            'folder_count': len([f for f in files if f.is_dir()]),
            'python_files': len(python_files),
            'config_files': len(config_files),
            'doc_files': len(doc_files),
            'has_init': (folder_path / '__init__.py').exists(),
            'has_readme': any('readme' in f.name.lower() for f in doc_files)
        }
    
    async def _find_scattered_files(self) -> List[Dict[str, Any]]:
        """หาไฟล์ที่กระจายในโฟลเดอร์หลัก"""
        scattered = []
        
        # ตรวจสอบไฟล์ในโฟลเดอร์หลัก
        for item in self.project_path.iterdir():
            if item.is_file() and item.name not in ['README.md', 'requirements.txt', 'setup.py', 'pyproject.toml']:
                scattered.append({
                    'path': str(item),
                    'name': item.name,
                    'suggested_location': self._suggest_location(item)
                })
        
        return scattered
    
    async def _check_management_files(self) -> Dict[str, bool]:
        """ตรวจสอบไฟล์จัดการ"""
        management_files = {
            'README.md': (self.project_path / 'README.md').exists(),
            'requirements.txt': (self.project_path / 'requirements.txt').exists(),
            'setup.py': (self.project_path / 'setup.py').exists(),
            'pyproject.toml': (self.project_path / 'pyproject.toml').exists(),
            '.gitignore': (self.project_path / '.gitignore').exists(),
            'project_config.json': (self.project_path / 'project_config.json').exists()
        }
        
        return management_files
    
    def _suggest_location(self, file_path: Path) -> str:
        """แนะนำตำแหน่งที่เหมาะสมสำหรับไฟล์"""
        file_name = file_path.name.lower()
        
        for category, keywords in self.config['organize_rules'].items():
            for keyword in keywords:
                if keyword in file_name:
                    return f"src/{category}"
        
        # ตรวจสอบนามสกุลไฟล์
        if file_path.suffix == '.py':
            return 'src/core'
        elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml']:
            return 'config'
        elif file_path.suffix in ['.md', '.txt', '.rst']:
            return 'docs'
        
        return 'src/utils'
    
    async def organize_project(self) -> Dict[str, Any]:
        """จัดระเบียบโปรเจ็ค"""
        logging.info("🏗️ เริ่มจัดระเบียบโปรเจ็ค...")
        
        results = {
            'folders_created': [],
            'files_moved': [],
            'files_created': [],
            'errors': []
        }
        
        try:
            # 1. สร้างโครงสร้างโฟลเดอร์
            await self._create_folder_structure(results)
            
            # 2. ย้ายไฟล์ที่กระจาย
            await self._move_scattered_files(results)
            
            # 3. สร้างไฟล์จัดการ
            await self._create_management_files(results)
            
            # 4. สร้าง README สำหรับโฟลเดอร์
            await self._create_folder_readmes(results)
            
        except Exception as e:
            results['errors'].append(str(e))
            logging.error(f"Error organizing project: {e}")
        
        return results
    
    async def _create_folder_structure(self, results: Dict[str, Any]):
        """สร้างโครงสร้างโฟลเดอร์"""
        for folder_name, subfolders in self.config['structure'].items():
            folder_path = self.project_path / folder_name
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                results['folders_created'].append(folder_name)
                logging.info(f"✅ สร้างโฟลเดอร์: {folder_name}")
            
            # สร้างโฟลเดอร์ย่อย
            for subfolder in subfolders:
                subfolder_path = folder_path / subfolder
                if not subfolder_path.exists():
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                    results['folders_created'].append(f"{folder_name}/{subfolder}")
                    logging.info(f"✅ สร้างโฟลเดอร์: {folder_name}/{subfolder}")
    
    async def _move_scattered_files(self, results: Dict[str, Any]):
        """ย้ายไฟล์ที่กระจาย"""
        scattered_files = await self._find_scattered_files()
        
        for file_info in scattered_files:
            try:
                source_path = Path(file_info['path'])
                target_folder = file_info['suggested_location']
                target_path = self.project_path / target_folder / source_path.name
                
                # สร้างโฟลเดอร์ปลายทาง
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # ย้ายไฟล์
                if not target_path.exists():
                    shutil.move(str(source_path), str(target_path))
                    results['files_moved'].append({
                        'from': str(source_path),
                        'to': str(target_path)
                    })
                    logging.info(f"📁 ย้ายไฟล์: {source_path.name} -> {target_folder}")
                else:
                    # เปลี่ยนชื่อไฟล์ถ้าซ้ำ
                    counter = 1
                    while target_path.exists():
                        new_name = f"{source_path.stem}_{counter}{source_path.suffix}"
                        target_path = target_path.parent / new_name
                        counter += 1
                    
                    shutil.move(str(source_path), str(target_path))
                    results['files_moved'].append({
                        'from': str(source_path),
                        'to': str(target_path)
                    })
                    logging.info(f"📁 ย้ายไฟล์: {source_path.name} -> {target_path.name}")
                    
            except Exception as e:
                results['errors'].append(f"Error moving {file_info['path']}: {e}")
    
    async def _create_management_files(self, results: Dict[str, Any]):
        """สร้างไฟล์จัดการ"""
        management_files = await self._check_management_files()
        
        # สร้าง README.md
        if not management_files['README.md']:
            readme_content = self._generate_readme()
            readme_path = self.project_path / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            results['files_created'].append('README.md')
            logging.info("📝 สร้าง README.md")
        
        # สร้าง .gitignore
        if not management_files['.gitignore']:
            gitignore_content = self._generate_gitignore()
            gitignore_path = self.project_path / '.gitignore'
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            results['files_created'].append('.gitignore')
            logging.info("📝 สร้าง .gitignore")
        
        # สร้าง project_config.json
        if not management_files['project_config.json']:
            config_path = self.project_path / 'project_config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            results['files_created'].append('project_config.json')
            logging.info("📝 สร้าง project_config.json")
    
    async def _create_folder_readmes(self, results: Dict[str, Any]):
        """สร้าง README สำหรับโฟลเดอร์"""
        for folder_name in self.config['structure']:
            folder_path = self.project_path / folder_name
            if folder_path.exists():
                readme_path = folder_path / 'README.md'
                if not readme_path.exists():
                    readme_content = self._generate_folder_readme(folder_name)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    results['files_created'].append(f'{folder_name}/README.md')
                    logging.info(f"📝 สร้าง README: {folder_name}")
    
    def _generate_readme(self) -> str:
        """สร้าง README.md"""
        return f"""# {self.config['project_name']}

{self.config['project_description']}

## 📁 โครงสร้างโปรเจ็ค

```
{self.project_path.name}/
├── src/                    # โค้ดหลัก
│   ├── core/              # ฟังก์ชันหลัก
│   ├── services/          # บริการต่างๆ
│   ├── tools/             # เครื่องมือ
│   └── utils/             # ฟังก์ชันช่วยเหลือ
├── docs/                  # เอกสาร
│   ├── api/               # API Documentation
│   ├── guides/            # คู่มือการใช้งาน
│   └── examples/          # ตัวอย่างการใช้งาน
├── tests/                 # การทดสอบ
│   ├── unit/              # Unit Tests
│   ├── integration/       # Integration Tests
│   └── e2e/               # End-to-End Tests
├── scripts/               # สคริปต์
│   ├── setup/             # สคริปต์ติดตั้ง
│   ├── deploy/            # สคริปต์ deploy
│   └── maintenance/       # สคริปต์บำรุงรักษา
└── config/                # ไฟล์การตั้งค่า
    ├── dev/               # การตั้งค่าสำหรับ Development
    ├── prod/              # การตั้งค่าสำหรับ Production
    └── test/              # การตั้งค่าสำหรับ Testing
```

## 🚀 การติดตั้ง

```bash
pip install -r requirements.txt
```

## 📖 การใช้งาน

ดูเอกสารในโฟลเดอร์ `docs/`

## 🧪 การทดสอบ

```bash
python -m pytest tests/
```

## 📝 การพัฒนา

1. สร้าง feature branch
2. เขียนโค้ดและทดสอบ
3. สร้าง Pull Request
4. รีวิวและ merge

---
*อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    def _generate_gitignore(self) -> str:
        """สร้าง .gitignore"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.cache/

# OS
.DS_Store
Thumbs.db

# Project specific
project_config.json
"""
    
    def _generate_folder_readme(self, folder_name: str) -> str:
        """สร้าง README สำหรับโฟลเดอร์"""
        folder_descriptions = {
            'src': 'โค้ดหลักของโปรเจ็ค',
            'docs': 'เอกสารและคู่มือการใช้งาน',
            'tests': 'การทดสอบต่างๆ',
            'scripts': 'สคริปต์สำหรับการจัดการโปรเจ็ค',
            'config': 'ไฟล์การตั้งค่า'
        }
        
        description = folder_descriptions.get(folder_name, f'โฟลเดอร์สำหรับ {folder_name}')
        
        return f"""# 📁 {folder_name}

{description}

## 📋 สถานะ
- [x] โฟลเดอร์พร้อมใช้งาน

## 📁 ไฟล์ในโฟลเดอร์
{self._generate_file_list(self.project_path / folder_name)}

---
*อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    def _generate_file_list(self, folder_path: Path) -> str:
        """สร้างรายการไฟล์"""
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
    
    async def display_analysis(self, analysis: Dict[str, Any]):
        """แสดงผลการวิเคราะห์"""
        print("\n" + "="*80)
        print("📊 ผลการวิเคราะห์โปรเจ็ค")
        print("="*80)
        
        print(f"\n📁 ข้อมูลพื้นฐาน:")
        print(f"   Path: {analysis['project_path']}")
        print(f"   Timestamp: {analysis['timestamp']}")
        
        if analysis['issues']:
            print(f"\n❌ ปัญหาที่พบ:")
            for issue in analysis['issues']:
                print(f"   - {issue}")
        
        if analysis['recommendations']:
            print(f"\n💡 คำแนะนำ:")
            for rec in analysis['recommendations']:
                print(f"   - {rec}")
        
        if analysis['scattered_files']:
            print(f"\n📁 ไฟล์ที่กระจาย:")
            for file_info in analysis['scattered_files']:
                print(f"   - {file_info['name']} -> {file_info['suggested_location']}")
        
        print(f"\n📋 ไฟล์จัดการ:")
        for file_name, exists in analysis['management_files'].items():
            status = "✅" if exists else "❌"
            print(f"   {status} {file_name}")
    
    async def display_organization_results(self, results: Dict[str, Any]):
        """แสดงผลการจัดระเบียบ"""
        print("\n" + "="*80)
        print("🎉 ผลการจัดระเบียบโปรเจ็ค")
        print("="*80)
        
        if results['folders_created']:
            print(f"\n📁 โฟลเดอร์ที่สร้าง:")
            for folder in results['folders_created']:
                print(f"   ✅ {folder}")
        
        if results['files_moved']:
            print(f"\n📁 ไฟล์ที่ย้าย:")
            for move in results['files_moved']:
                print(f"   📁 {Path(move['from']).name} -> {Path(move['to']).parent.name}")
        
        if results['files_created']:
            print(f"\n📝 ไฟล์ที่สร้าง:")
            for file in results['files_created']:
                print(f"   ✅ {file}")
        
        if results['errors']:
            print(f"\n❌ ข้อผิดพลาด:")
            for error in results['errors']:
                print(f"   - {error}")

async def main():
    """ฟังก์ชันหลัก"""
    try:
        # สร้าง project manager
        manager = ProjectManager()
        
        # วิเคราะห์โปรเจ็ค
        analysis = await manager.analyze_project()
        await manager.display_analysis(analysis)
        
        # ถามผู้ใช้ว่าต้องการจัดระเบียบหรือไม่
        print("\n" + "="*80)
        response = input("❓ ต้องการจัดระเบียบโปรเจ็คหรือไม่? (y/N): ")
        
        if response.lower() == 'y':
            # จัดระเบียบโปรเจ็ค
            results = await manager.organize_project()
            await manager.display_organization_results(results)
            
            print("\n🎉 การจัดระเบียบโปรเจ็คเสร็จสิ้น!")
        else:
            print("\n❌ ยกเลิกการจัดระเบียบ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
