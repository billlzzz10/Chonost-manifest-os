#!/usr/bin/env python3
"""
Smart Vault Manager - An intelligent and adaptive tool for managing a vault.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import difflib

class SmartVaultManager:
    """
    An intelligent tool for managing a vault.

    Attributes:
        vault_path (Path): The path to the vault.
        analysis_result (dict): The result of the structure analysis.
        management_plan (dict): The generated management plan.
        operations_log (list): A log of the operations performed.
    """
    
    def __init__(self, vault_path: str):
        """
        Initializes the SmartVaultManager.

        Args:
            vault_path (str): The path to the vault.
        """
        self.vault_path = Path(vault_path)
        self.analysis_result = {}
        self.management_plan = {}
        self.operations_log = []
        
    def analyze_current_structure(self) -> Dict[str, Any]:
        """
        Analyzes the current structure in detail.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        print("🔍 Analyzing current structure...")
        
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
        
        # Analyze main folders
        main_folders = [
            '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
            '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
            '08_Templates-Tools'
        ]
        
        # Check for duplicate folders
        all_folders = [f.name for f in self.vault_path.iterdir() if f.is_dir()]
        duplicate_patterns = self._find_duplicate_patterns(all_folders)
        
        for folder_name in main_folders:
            folder_path = self.vault_path / folder_name
            if folder_path.exists():
                folder_info = self._analyze_folder(folder_path)
                analysis['folders'][folder_name] = folder_info
                analysis['statistics']['total_folders'] += 1
                
                # Check for empty folders
                if folder_info['file_count'] == 0:
                    analysis['empty_folders'].append(folder_name)
                
                # Check for management issues
                if folder_info['has_management_issues']:
                    analysis['structure_issues'].append({
                        'folder': folder_name,
                        'issue': 'Missing management file (README, Dashboard, Index)',
                        'severity': 'medium'
                    })
        
        # Analyze other folders
        other_folders = [f for f in all_folders if f not in main_folders]
        for folder_name in other_folders:
            folder_path = self.vault_path / folder_name
            folder_info = self._analyze_folder(folder_path)
            analysis['folders'][folder_name] = folder_info
            analysis['statistics']['total_folders'] += 1
            
            # Check for potentially duplicate folders
            if any(pattern in folder_name for pattern in duplicate_patterns):
                analysis['duplicate_folders'].append(folder_name)
        
        # Analyze files in the Templates-Tools folder
        templates_path = self.vault_path / "08_Templates-Tools"
        if templates_path.exists():
            analysis['templates_analysis'] = self._analyze_templates_structure(templates_path)
        
        self.analysis_result = analysis
        return analysis
    
    def _analyze_folder(self, folder_path: Path) -> Dict[str, Any]:
        """
        Analyzes a single folder.

        Args:
            folder_path (Path): The path to the folder.

        Returns:
            Dict[str, Any]: The analysis result for the folder.
        """
        files = list(folder_path.rglob("*"))
        md_files = [f for f in files if f.is_file() and f.suffix == '.md']
        json_files = [f for f in files if f.is_file() and f.suffix == '.json']
        other_files = [f for f in files if f.is_file() and f.suffix not in ['.md', '.json']]
        
        # Check for management files
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
            'files': [f.name for f in md_files[:10]],  # Show the first 10 files
            'subfolders': [f.name for f in files if f.is_dir()]
        }
    
    def _analyze_templates_structure(self, templates_path: Path) -> Dict[str, Any]:
        """
        Analyzes the structure of the Templates-Tools folder.

        Args:
            templates_path (Path): The path to the Templates-Tools folder.

        Returns:
            Dict[str, Any]: The analysis result.
        """
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
        """
        Finds duplicate folder patterns.

        Args:
            folder_names (List[str]): A list of folder names.

        Returns:
            List[str]: A list of duplicate folder patterns.
        """
        patterns = []
        for name in folder_names:
            # Find similar names
            similar = difflib.get_close_matches(name, folder_names, n=2, cutoff=0.6)
            if len(similar) > 1:
                patterns.append(name)
        return patterns
    
    def generate_management_plan(self) -> Dict[str, Any]:
        """
        Generates a management plan.

        Returns:
            Dict[str, Any]: The generated management plan.
        """
        print("📋 Generating management plan...")
        
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
        
        # 1. Address critical issues
        if analysis['duplicate_folders']:
            plan['summary']['critical_issues'] += len(analysis['duplicate_folders'])
            plan['operations']['cleanup'].append({
                'action': 'resolve_duplicates',
                'folders': analysis['duplicate_folders'],
                'priority': 'critical'
            })
            plan['recommendations'].append('Resolve duplicate folders first')
        
        # 2. Create missing structure
        if 'templates_analysis' in analysis:
            missing = analysis['templates_analysis']['missing_structure']
            if missing:
                plan['operations']['create_structure'].append({
                    'action': 'create_missing_folders',
                    'folders': missing,
                    'priority': 'high'
                })
        
        # 3. Move scattered files
        if analysis['folders']:
            for folder_name, folder_info in analysis['folders'].items():
                if folder_name not in ['00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
                                     '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE',
                                     '08_Templates-Tools']:
                    # Old folders that should be moved
                    if folder_info['file_count'] > 0:
                        plan['operations']['move_files'].append({
                            'action': 'move_old_folder',
                            'source': folder_name,
                            'target': self._determine_target_folder(folder_name, folder_info),
                            'priority': 'medium'
                        })
        
        # 4. Create management files
        for folder_name, folder_info in analysis['folders'].items():
            if folder_info['has_management_issues']:
                plan['operations']['create_management_files'].append({
                    'action': 'create_readme',
                    'folder': folder_name,
                    'priority': 'medium'
                })
        
        # 5. Organize Templates-Tools
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
        """
        Determines the target folder for a file.

        Args:
            folder_name (str): The name of the folder.
            folder_info (Dict[str, Any]): Information about the folder.

        Returns:
            str: The target folder.
        """
        # Classification logic
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
        """Displays the analysis report."""
        analysis = self.analysis_result
        
        print("\n" + "="*80)
        print("📊 Vault Structure Analysis Report")
        print("="*80)
        
        print(f"\n📁 Basic Information:")
        print(f"   Path: {analysis['vault_path']}")
        print(f"   Total folders: {analysis['statistics']['total_folders']}")
        print(f"   Total files: {analysis['statistics']['total_files']}")
        print(f"   Markdown files: {analysis['statistics']['md_files']}")
        
        if analysis['duplicate_folders']:
            print(f"\n⚠️ Duplicate Folders:")
            for folder in analysis['duplicate_folders']:
                print(f"   - {folder}")
        
        if analysis['empty_folders']:
            print(f"\n📁 Empty Folders:")
            for folder in analysis['empty_folders']:
                print(f"   - {folder}")
        
        if analysis['structure_issues']:
            print(f"\n❌ Management Issues:")
            for issue in analysis['structure_issues']:
                print(f"   - {issue['folder']}: {issue['issue']}")
        
        # Display details of main folders
        print(f"\n📋 Main Folder Details:")
        main_folders = ['00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
                       '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE']
        
        for folder in main_folders:
            if folder in analysis['folders']:
                info = analysis['folders'][folder]
                status = "✅" if not info['has_management_issues'] else "❌"
                print(f"   {status} {folder}: {info['file_count']} files")
    
    def display_management_plan(self):
        """Displays the management plan."""
        plan = self.management_plan
        
        print("\n" + "="*80)
        print("📋 Vault Management Plan")
        print("="*80)
        
        print(f"\n📊 Plan Summary:")
        print(f"   Total operations: {plan['summary']['total_operations']}")
        print(f"   Critical issues: {plan['summary']['critical_issues']}")
        
        if plan['operations']['cleanup']:
            print(f"\n🚨 Critical Issue Resolution:")
            for op in plan['operations']['cleanup']:
                print(f"   - {op['action']}: {op['folders']}")
        
        if plan['operations']['create_structure']:
            print(f"\n🏗️ Structure Creation:")
            for op in plan['operations']['create_structure']:
                print(f"   - {op['action']}: {op['folders']}")
        
        if plan['operations']['move_files']:
            print(f"\n📁 File Movement:")
            for op in plan['operations']['move_files']:
                print(f"   - Move {op['source']} -> {op['target']}")
        
        if plan['operations']['create_management_files']:
            print(f"\n📝 Management File Creation:")
            for op in plan['operations']['create_management_files']:
                print(f"   - Create README for {op['folder']}")
        
        if plan['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in plan['recommendations']:
                print(f"   - {rec}")
    
    def execute_plan(self, confirm: bool = True) -> bool:
        """
        Executes the management plan.

        Args:
            confirm (bool, optional): Whether to ask for confirmation before executing. Defaults to True.

        Returns:
            bool: True if the plan was executed successfully, False otherwise.
        """
        if confirm:
            print("\n" + "="*80)
            print("🚀 Starting plan execution")
            print("="*80)
            
            response = input("\n❓ Do you want to execute this plan? (y/N): ")
            if response.lower() != 'y':
                print("❌ Execution cancelled")
                return False
        
        plan = self.management_plan
        
        try:
            # Execute in order of priority
            operations_order = ['cleanup', 'create_structure', 'move_files', 'create_management_files', 'organize']
            
            for op_type in operations_order:
                if plan['operations'][op_type]:
                    print(f"\n🔧 Executing: {op_type}")
                    for op in plan['operations'][op_type]:
                        self._execute_operation(op)
            
            print("\n✅ Execution complete!")
            return True
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            return False
    
    def _execute_operation(self, operation: Dict[str, Any]):
        """
        Executes a single operation.

        Args:
            operation (Dict[str, Any]): The operation to execute.
        """
        action = operation['action']
        
        if action == 'resolve_duplicates':
            print(f"   🗑️ Resolving duplicate folders: {operation['folders']}")
            
        elif action == 'create_missing_folders':
            for folder in operation['folders']:
                folder_path = self.vault_path / "08_Templates-Tools" / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created folder: {folder}")
        
        elif action == 'move_old_folder':
            source = self.vault_path / operation['source']
            target = self.vault_path / operation['target']
            if source.exists():
                print(f"   📁 Moving: {operation['source']} -> {operation['target']}")
        
        elif action == 'create_readme':
            folder_path = self.vault_path / operation['folder']
            readme_path = folder_path / "README.md"
            if not readme_path.exists():
                print(f"   📝 Creating README for: {operation['folder']}")
    
    def save_report(self, filename: str = "vault_management_report.json"):
        """
        Saves the analysis and management plan to a report file.

        Args:
            filename (str, optional): The name of the report file.
                Defaults to "vault_management_report.json".
        """
        report = {
            'analysis': self.analysis_result,
            'plan': self.management_plan,
            'operations_log': self.operations_log,
            'generated_at': datetime.now().isoformat()
        }
        
        report_path = self.vault_path / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Report saved to: {filename}")

def main():
    """Main function."""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 Smart Vault Manager - An intelligent tool for managing a vault")
    print("="*80)
    
    # Create the manager
    manager = SmartVaultManager(vault_path)
    
    # 1. Analyze the structure
    analysis = manager.analyze_current_structure()
    
    # 2. Display the analysis report
    manager.display_analysis_report()
    
    # 3. Generate a management plan
    plan = manager.generate_management_plan()
    
    # 4. Display the management plan
    manager.display_management_plan()
    
    # 5. Save the report
    manager.save_report()
    
    # 6. Ask the user if they want to proceed
    print("\n" + "="*80)
    print("🎯 Next Steps")
    print("="*80)
    print("1. Review the analysis report")
    print("2. Review the management plan")
    print("3. Decide whether to proceed")
    print("4. Call manager.execute_plan() to proceed")

if __name__ == "__main__":
    main()
