#!/usr/bin/env python3
"""
Project Manager - An intelligent tool for managing projects.
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
    """
    An intelligent tool for managing projects.

    Attributes:
        project_path (Path): The path to the project.
        config (Dict[str, Any]): The configuration for the project.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initializes the ProjectManager.

        Args:
            project_path (str, optional): The path to the project. Defaults to ".".
        """
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config()
        self.setup_logging()
        
    def setup_logging(self):
        """Sets up logging for the project manager."""
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
        """
        Loads the configuration for the project.

        Returns:
            Dict[str, Any]: The project configuration.
        """
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
        """
        Analyzes the project structure.

        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.
        """
        logging.info("🔍 Analyzing project structure...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'structure': {},
            'files': {},
            'issues': [],
            'recommendations': []
        }
        
        # Analyze folder structure
        for folder_name in self.config['structure']:
            folder_path = self.project_path / folder_name
            if folder_path.exists():
                folder_info = await self._analyze_folder(folder_path)
                analysis['structure'][folder_name] = folder_info
            else:
                analysis['issues'].append(f"Missing folder: {folder_name}")
                analysis['recommendations'].append(f"Create folder: {folder_name}")
        
        # Analyze scattered files
        scattered_files = await self._find_scattered_files()
        analysis['scattered_files'] = scattered_files
        
        if scattered_files:
            analysis['issues'].append(f"Found {len(scattered_files)} scattered files")
            analysis['recommendations'].append("Organize scattered files")
        
        # Check management files
        management_files = await self._check_management_files()
        analysis['management_files'] = management_files
        
        missing_management = [f for f, exists in management_files.items() if not exists]
        if missing_management:
            analysis['issues'].extend([f"Missing {f}" for f in missing_management])
            analysis['recommendations'].extend([f"Create {f}" for f in missing_management])
        
        return analysis
    
    async def _analyze_folder(self, folder_path: Path) -> Dict[str, Any]:
        """
        Analyzes a single folder.

        Args:
            folder_path (Path): The path to the folder to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing the folder analysis.
        """
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
        """
        Finds scattered files in the main project folder.

        Returns:
            List[Dict[str, Any]]: A list of scattered files.
        """
        scattered = []
        
        # Check files in the main folder
        for item in self.project_path.iterdir():
            if item.is_file() and item.name not in ['README.md', 'requirements.txt', 'setup.py', 'pyproject.toml']:
                scattered.append({
                    'path': str(item),
                    'name': item.name,
                    'suggested_location': self._suggest_location(item)
                })
        
        return scattered
    
    async def _check_management_files(self) -> Dict[str, bool]:
        """
        Checks for the existence of management files.

        Returns:
            Dict[str, bool]: A dictionary indicating the existence of each management file.
        """
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
        """
        Suggests a suitable location for a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            str: The suggested location for the file.
        """
        file_name = file_path.name.lower()
        
        for category, keywords in self.config['organize_rules'].items():
            for keyword in keywords:
                if keyword in file_name:
                    return f"src/{category}"
        
        # Check file extension
        if file_path.suffix == '.py':
            return 'src/core'
        elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml']:
            return 'config'
        elif file_path.suffix in ['.md', '.txt', '.rst']:
            return 'docs'
        
        return 'src/utils'
    
    async def organize_project(self) -> Dict[str, Any]:
        """
        Organizes the project by creating folders, moving files, and creating management files.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the organization.
        """
        logging.info("🏗️ Organizing project...")
        
        results = {
            'folders_created': [],
            'files_moved': [],
            'files_created': [],
            'errors': []
        }
        
        try:
            # 1. Create folder structure
            await self._create_folder_structure(results)
            
            # 2. Move scattered files
            await self._move_scattered_files(results)
            
            # 3. Create management files
            await self._create_management_files(results)
            
            # 4. Create READMEs for folders
            await self._create_folder_readmes(results)
            
        except Exception as e:
            results['errors'].append(str(e))
            logging.error(f"Error organizing project: {e}")
        
        return results
    
    async def _create_folder_structure(self, results: Dict[str, Any]):
        """
        Creates the folder structure for the project.

        Args:
            results (Dict[str, Any]): A dictionary to store the results.
        """
        for folder_name, subfolders in self.config['structure'].items():
            folder_path = self.project_path / folder_name
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                results['folders_created'].append(folder_name)
                logging.info(f"✅ Created folder: {folder_name}")
            
            # Create subfolders
            for subfolder in subfolders:
                subfolder_path = folder_path / subfolder
                if not subfolder_path.exists():
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                    results['folders_created'].append(f"{folder_name}/{subfolder}")
                    logging.info(f"✅ Created folder: {folder_name}/{subfolder}")
    
    async def _move_scattered_files(self, results: Dict[str, Any]):
        """
        Moves scattered files to their suggested locations.

        Args:
            results (Dict[str, Any]): A dictionary to store the results.
        """
        scattered_files = await self._find_scattered_files()
        
        for file_info in scattered_files:
            try:
                source_path = Path(file_info['path'])
                target_folder = file_info['suggested_location']
                target_path = self.project_path / target_folder / source_path.name
                
                # Create target folder
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                if not target_path.exists():
                    shutil.move(str(source_path), str(target_path))
                    results['files_moved'].append({
                        'from': str(source_path),
                        'to': str(target_path)
                    })
                    logging.info(f"📁 Moved file: {source_path.name} -> {target_folder}")
                else:
                    # Rename file if it already exists
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
                    logging.info(f"📁 Moved file: {source_path.name} -> {target_path.name}")
                    
            except Exception as e:
                results['errors'].append(f"Error moving {file_info['path']}: {e}")
    
    async def _create_management_files(self, results: Dict[str, Any]):
        """
        Creates management files if they don't exist.

        Args:
            results (Dict[str, Any]): A dictionary to store the results.
        """
        management_files = await self._check_management_files()
        
        # Create README.md
        if not management_files['README.md']:
            readme_content = self._generate_readme()
            readme_path = self.project_path / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            results['files_created'].append('README.md')
            logging.info("📝 Created README.md")
        
        # Create .gitignore
        if not management_files['.gitignore']:
            gitignore_content = self._generate_gitignore()
            gitignore_path = self.project_path / '.gitignore'
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            results['files_created'].append('.gitignore')
            logging.info("📝 Created .gitignore")
        
        # Create project_config.json
        if not management_files['project_config.json']:
            config_path = self.project_path / 'project_config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            results['files_created'].append('project_config.json')
            logging.info("📝 Created project_config.json")
    
    async def _create_folder_readmes(self, results: Dict[str, Any]):
        """
        Creates README files for folders.

        Args:
            results (Dict[str, Any]): A dictionary to store the results.
        """
        for folder_name in self.config['structure']:
            folder_path = self.project_path / folder_name
            if folder_path.exists():
                readme_path = folder_path / 'README.md'
                if not readme_path.exists():
                    readme_content = self._generate_folder_readme(folder_name)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    results['files_created'].append(f'{folder_name}/README.md')
                    logging.info(f"📝 Created README for: {folder_name}")
    
    def _generate_readme(self) -> str:
        """
        Generates the content for the main README.md file.

        Returns:
            str: The content of the README.md file.
        """
        return f"""# {self.config['project_name']}

{self.config['project_description']}

## 📁 Project Structure

```
{self.project_path.name}/
├── src/                    # Main source code
│   ├── core/              # Core functions
│   ├── services/          # Various services
│   ├── tools/             # Tools
│   └── utils/             # Helper functions
├── docs/                  # Documentation
│   ├── api/               # API Documentation
│   ├── guides/            # User guides
│   └── examples/          # Usage examples
├── tests/                 # Tests
│   ├── unit/              # Unit Tests
│   ├── integration/       # Integration Tests
│   └── e2e/               # End-to-End Tests
├── scripts/               # Scripts
│   ├── setup/             # Setup scripts
│   ├── deploy/            # Deployment scripts
│   └── maintenance/       # Maintenance scripts
└── config/                # Configuration files
    ├── dev/               # Development configuration
    ├── prod/              # Production configuration
    └── test/              # Testing configuration
```

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 📖 Usage

See the documentation in the `docs/` folder.

## 🧪 Testing

```bash
python -m pytest tests/
```

## 📝 Development

1. Create a feature branch
2. Write code and tests
3. Create a Pull Request
4. Review and merge

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    def _generate_gitignore(self) -> str:
        """
        Generates the content for the .gitignore file.

        Returns:
            str: The content of the .gitignore file.
        """
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
        """
        Generates the content for a folder's README.md file.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            str: The content of the README.md file.
        """
        folder_descriptions = {
            'src': 'Main source code of the project',
            'docs': 'Documentation and user guides',
            'tests': 'Various tests',
            'scripts': 'Scripts for project management',
            'config': 'Configuration files'
        }
        
        description = folder_descriptions.get(folder_name, f'Folder for {folder_name}')
        
        return f"""# 📁 {folder_name}

{description}

## 📋 Status
- [x] Folder is ready for use

## 📁 Files in Folder
{self._generate_file_list(self.project_path / folder_name)}

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    def _generate_file_list(self, folder_path: Path) -> str:
        """
        Generates a list of files in a folder.

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
    
    async def display_analysis(self, analysis: Dict[str, Any]):
        """
        Displays the project analysis results.

        Args:
            analysis (Dict[str, Any]): The analysis results.
        """
        print("\n" + "="*80)
        print("📊 Project Analysis Results")
        print("="*80)
        
        print(f"\n📁 Basic Information:")
        print(f"   Path: {analysis['project_path']}")
        print(f"   Timestamp: {analysis['timestamp']}")
        
        if analysis['issues']:
            print(f"\n❌ Issues Found:")
            for issue in analysis['issues']:
                print(f"   - {issue}")
        
        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   - {rec}")
        
        if analysis['scattered_files']:
            print(f"\n📁 Scattered Files:")
            for file_info in analysis['scattered_files']:
                print(f"   - {file_info['name']} -> {file_info['suggested_location']}")
        
        print(f"\n📋 Management Files:")
        for file_name, exists in analysis['management_files'].items():
            status = "✅" if exists else "❌"
            print(f"   {status} {file_name}")
    
    async def display_organization_results(self, results: Dict[str, Any]):
        """
        Displays the project organization results.

        Args:
            results (Dict[str, Any]): The organization results.
        """
        print("\n" + "="*80)
        print("🎉 Project Organization Results")
        print("="*80)
        
        if results['folders_created']:
            print(f"\n📁 Folders Created:")
            for folder in results['folders_created']:
                print(f"   ✅ {folder}")
        
        if results['files_moved']:
            print(f"\n📁 Files Moved:")
            for move in results['files_moved']:
                print(f"   📁 {Path(move['from']).name} -> {Path(move['to']).parent.name}")
        
        if results['files_created']:
            print(f"\n📝 Files Created:")
            for file in results['files_created']:
                print(f"   ✅ {file}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   - {error}")

async def main():
    """Main function."""
    try:
        # Create project manager
        manager = ProjectManager()
        
        # Analyze project
        analysis = await manager.analyze_project()
        await manager.display_analysis(analysis)
        
        # Ask the user if they want to organize the project
        print("\n" + "="*80)
        response = input("❓ Do you want to organize the project? (y/N): ")
        
        if response.lower() == 'y':
            # Organize project
            results = await manager.organize_project()
            await manager.display_organization_results(results)
            
            print("\n🎉 Project organization complete!")
        else:
            print("\n❌ Organization cancelled")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
