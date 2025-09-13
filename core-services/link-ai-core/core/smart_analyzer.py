#!/usr/bin/env python3
"""
Smart File System Analyzer - An intelligent analyzer for AI.
Understands folder structures deeply and provides smart recommendations.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from file_system_analyzer import FileSystemMCPTool

class SmartAnalyzer:
    """
    An intelligent file system analyzer that provides smart recommendations.

    Attributes:
        tool (FileSystemMCPTool): The file system tool for database interaction.
        session_id (str): The session ID for the analysis.
        analysis_results (dict): A dictionary to store the analysis results.
    """
    def __init__(self, session_id):
        """
        Initializes the SmartAnalyzer.

        Args:
            session_id (str): The session ID for the analysis.
        """
        self.tool = FileSystemMCPTool()
        self.session_id = session_id
        self.analysis_results = {}
        
    def analyze_project_structure(self):
        """Analyzes the project structure in depth."""
        print("🧠 Smart File System Analysis")
        print("=" * 60)
        
        # 1. Analyze project type
        self._detect_project_type()
        
        # 2. Analyze folder structure
        self._analyze_folder_structure()
        
        # 3. Analyze files by type
        self._analyze_file_patterns()
        
        # 4. Analyze file relationships
        self._analyze_file_relationships()
        
        # 5. Analyze file usage and age
        self._analyze_file_usage_patterns()
        
        # 6. Analyze security and risks
        self._analyze_security_risks()
        
        # 7. Summarize and provide recommendations
        self._generate_smart_recommendations()
        
    def _detect_project_type(self):
        """Detects the project type."""
        print("\n🔍 1. Detecting project type")
        print("-" * 40)
        
        # Check for key files
        key_files = self._get_key_files()
        
        project_type = "Unknown"
        confidence = 0
        
        # Detect Obsidian Vault
        if any('.obsidian' in path for _, path, _ in key_files):
            project_type = "Obsidian Vault"
            confidence = 95
            
        # Detect Web Project
        elif any(ext in ['.html', '.css', '.js'] for _, _, ext in key_files):
            project_type = "Web Project"
            confidence = 85
            
        # Detect Data Project
        elif any(ext in ['.csv', '.json', '.xlsx'] for _, _, ext in key_files):
            project_type = "Data Project"
            confidence = 80
            
        print(f"📋 Project Type: {project_type}")
        print(f"🎯 Confidence: {confidence}%")
        
        self.analysis_results['project_type'] = {
            'type': project_type,
            'confidence': confidence,
            'key_files': key_files
        }
        
    def _analyze_folder_structure(self):
        """Analyzes the folder structure."""
        print("\n📁 2. Analyzing folder structure")
        print("-" * 40)
        
        # Look at the folder structure
        sql = """
        SELECT parent_directory, COUNT(*) as file_count, 
               SUM(file_size) as total_size,
               GROUP_CONCAT(DISTINCT file_extension) as extensions
        FROM files 
        WHERE session_id = ? 
        GROUP BY parent_directory 
        ORDER BY file_count DESC
        LIMIT 15
        """
        
        result = self._execute_sql(sql, [self.session_id])
        
        print("📊 Main folder structure:")
        for i, (folder, count, size, exts) in enumerate(result, 1):
            size_mb = size / 1024 / 1024 if size else 0
            print(f"{i:2d}. {folder}")
            print(f"    📄 {count} files, {size_mb:.1f} MB")
            print(f"    📝 Extensions: {exts[:50]}...")
            print()
            
        self.analysis_results['folder_structure'] = result
        
    def _analyze_file_patterns(self):
        """Analyzes file patterns."""
        print("\n📈 3. Analyzing file patterns")
        print("-" * 40)
        
        # Analyze files by type
        patterns = {
            'documentation': ['.md', '.txt', '.pdf', '.doc', '.docx'],
            'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css'],
            'data': ['.csv', '.json', '.xml', '.sql', '.db'],
            'media': ['.jpg', '.png', '.gif', '.mp4', '.mp3', '.wav'],
            'archive': ['.zip', '.rar', '.tar', '.gz', '.7z'],
            'config': ['.config', '.ini', '.yaml', '.yml', '.toml', '.env']
        }
        
        for category, extensions in patterns.items():
            files = self._get_files_by_extensions(extensions)
            if files:
                total_size = sum(size for _, _, size in files)
                print(f"📂 {category.title()}: {len(files)} files, {total_size/1024/1024:.1f} MB")
                
        self.analysis_results['file_patterns'] = patterns
        
    def _analyze_file_relationships(self):
        """Analyzes relationships between files."""
        print("\n🔗 4. Analyzing file relationships")
        print("-" * 40)
        
        # Check for related files
        relationships = []
        
        # Check for related config files
        config_files = self._get_files_by_extensions(['.json', '.yaml', '.yml', '.config'])
        if config_files:
            print(f"⚙️ Config files: {len(config_files)} files")
            relationships.append(('config_files', config_files))
            
        # Check for potential backup files
        backup_patterns = ['backup', 'bak', 'old', 'temp', 'tmp']
        backup_files = self._find_files_by_patterns(backup_patterns)
        if backup_files:
            print(f"💾 Backup files: {len(backup_files)} files")
            relationships.append(('backup_files', backup_files))
            
        # Check for potential cache files
        cache_patterns = ['cache', 'tmp', 'temp', '.cache']
        cache_files = self._find_files_by_patterns(cache_patterns)
        if cache_files:
            print(f"🗂️ Cache files: {len(cache_files)} files")
            relationships.append(('cache_files', cache_files))
            
        self.analysis_results['file_relationships'] = relationships
        
    def _analyze_file_usage_patterns(self):
        """Analyzes file usage patterns."""
        print("\n⏰ 5. Analyzing file usage patterns")
        print("-" * 40)
        
        # Look at recently modified files
        recent_files = self._get_recent_files(days=7)
        old_files = self._get_old_files(days=90)
        
        print(f"🆕 Recently modified files (7 days): {len(recent_files)} files")
        print(f"📅 Old files (90 days): {len(old_files)} files")
        
        # Analyze unused files
        unused_files = self._identify_unused_files()
        if unused_files:
            print(f"🚫 Potentially unused files: {len(unused_files)} files")
            
        self.analysis_results['usage_patterns'] = {
            'recent_files': recent_files,
            'old_files': old_files,
            'unused_files': unused_files
        }
        
    def _analyze_security_risks(self):
        """Analyzes security risks."""
        print("\n🔒 6. Analyzing security risks")
        print("-" * 40)
        
        risks = []
        
        # Check for files that may contain sensitive information
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        sensitive_files = self._find_files_by_patterns(sensitive_patterns)
        if sensitive_files:
            print(f"⚠️ Files that may contain sensitive information: {len(sensitive_files)} files")
            risks.append(('sensitive_files', sensitive_files))
            
        # Check for executable files
        exe_files = self._get_files_by_extensions(['.exe', '.bat', '.cmd', '.ps1'])
        if exe_files:
            print(f"⚡ Executable files: {len(exe_files)} files")
            risks.append(('executable_files', exe_files))
            
        # Check for files that may be malware
        suspicious_patterns = ['virus', 'malware', 'trojan', 'spyware']
        suspicious_files = self._find_files_by_patterns(suspicious_patterns)
        if suspicious_files:
            print(f"🚨 Suspicious files: {len(suspicious_files)} files")
            risks.append(('suspicious_files', suspicious_files))
            
        self.analysis_results['security_risks'] = risks
        
    def _generate_smart_recommendations(self):
        """Generates smart recommendations."""
        print("\n🎯 7. Smart recommendations")
        print("-" * 40)
        
        recommendations = []
        
        # Analyze based on the analysis results
        project_type = self.analysis_results.get('project_type', {}).get('type', 'Unknown')
        
        if project_type == "Obsidian Vault":
            recommendations.extend(self._get_obsidian_recommendations())
        elif project_type == "Web Project":
            recommendations.extend(self._get_web_recommendations())
        else:
            recommendations.extend(self._get_general_recommendations())
            
        # Display recommendations
        for i, (category, recs) in enumerate(recommendations, 1):
            print(f"\n📋 {category}:")
            for j, rec in enumerate(recs, 1):
                print(f"  {i}.{j} {rec}")
                
        self.analysis_results['recommendations'] = recommendations
        
    def _get_obsidian_recommendations(self):
        """Gets recommendations for an Obsidian Vault."""
        recommendations = []
        
        # Check for unused plugins
        plugins = self._get_obsidian_plugins()
        if len(plugins) > 20:
            recommendations.append(("Optimization", "Consider deleting unused plugins (more than 20 plugins found)"))
            
        # Check for RAR files
        rar_files = self._get_files_by_extensions(['.rar'])
        if rar_files:
            recommendations.append(("Archive Management", "Check if RAR files need to be kept"))
            
        # Check for unnamed files
        unnamed_files = self._find_files_by_patterns(['untitled', 'untitled', 'new'])
        if unnamed_files:
            recommendations.append(("File Organization", "Give appropriate names to unnamed files"))
            
        return recommendations
        
    def _get_web_recommendations(self):
        """Gets recommendations for a Web Project."""
        recommendations = []
        
        # Check for duplicate JavaScript files
        js_files = self._get_files_by_extensions(['.js'])
        if len(js_files) > 50:
            recommendations.append(("Code Organization", "Consider using a bundler to combine JavaScript files"))
            
        return recommendations
        
    def _get_general_recommendations(self):
        """Gets general recommendations."""
        recommendations = []
        
        # Check for duplicate files
        duplicates = self._get_duplicate_files()
        if duplicates:
            recommendations.append(("Storage Optimization", f"Delete duplicate files to save space ({len(duplicates)} groups)"))
            
        # Check for old files
        old_files = self.analysis_results.get('usage_patterns', {}).get('old_files', [])
        if len(old_files) > 100:
            recommendations.append(("Archive Management", "Consider archiving old files"))
            
        return recommendations
        
    # Helper methods
    def _execute_sql(self, sql, params):
        """Executes an SQL query."""
        params_dict = {
            'action': 'query_sql',
            'sql': sql,
            'params': params,
            'session_id': self.session_id
        }
        result = self.tool._run(json.dumps(params_dict))
        return json.loads(result)
        
    def _get_key_files(self):
        """Gets key files for project type detection."""
        sql = """
        SELECT file_name, file_path, file_extension 
        FROM files 
        WHERE session_id = ? 
        ORDER BY file_size DESC 
        LIMIT 20
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_files_by_extensions(self, extensions):
        """Gets files by their extensions."""
        ext_list = "', '".join(extensions)
        sql = f"""
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? AND file_extension IN ('{ext_list}')
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _find_files_by_patterns(self, patterns):
        """Finds files by their name patterns."""
        pattern_conditions = " OR ".join([f"file_name LIKE '%{pattern}%'" for pattern in patterns])
        sql = f"""
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? AND ({pattern_conditions})
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_recent_files(self, days=7):
        """Gets recently modified files."""
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date > datetime('now', '-{} days')
        """.format(days)
        return self._execute_sql(sql, [self.session_id])
        
    def _get_old_files(self, days=90):
        """Gets old files."""
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date < datetime('now', '-{} days')
        """.format(days)
        return self._execute_sql(sql, [self.session_id])
        
    def _get_duplicate_files(self):
        """Gets duplicate files."""
        sql = """
        SELECT hash_md5, COUNT(*) as count 
        FROM files 
        WHERE session_id = ? AND hash_md5 IS NOT NULL 
        GROUP BY hash_md5 
        HAVING COUNT(*) > 1
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_obsidian_plugins(self):
        """Gets Obsidian plugins."""
        sql = """
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? 
        AND file_path LIKE '%.obsidian\\plugins%'
        AND file_name = 'main.js'
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _identify_unused_files(self):
        """Identifies potentially unused files."""
        # Files that have not been modified for a long time and are small
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date < datetime('now', '-30 days')
        AND file_size < 1024
        """
        return self._execute_sql(sql, [self.session_id])

def main():
    """Main function to run the analyzer."""
    session_id = 'scan_1755714528'  # Vault session
    analyzer = SmartAnalyzer(session_id)
    analyzer.analyze_project_structure()
    
    # Save the analysis results
    with open('smart_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(analyzer.analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 Analysis results saved to: smart_analysis_report.json")

if __name__ == "__main__":
    main()
