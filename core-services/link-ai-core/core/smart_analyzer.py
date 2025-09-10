#!/usr/bin/env python3
"""
Smart File System Analyzer - วิเคราะห์อัจฉริยะสำหรับ AI
เข้าใจโครงสร้างโฟลเดอร์ได้ลึกซึ้งและให้คำแนะนำที่ฉลาด
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from file_system_analyzer import FileSystemMCPTool

class SmartAnalyzer:
    def __init__(self, session_id):
        self.tool = FileSystemMCPTool()
        self.session_id = session_id
        self.analysis_results = {}
        
    def analyze_project_structure(self):
        """วิเคราะห์โครงสร้างโปรเจ็คอย่างลึกซึ้ง"""
        print("🧠 Smart File System Analysis")
        print("=" * 60)
        
        # 1. วิเคราะห์ประเภทโปรเจ็ค
        self._detect_project_type()
        
        # 2. วิเคราะห์โครงสร้างโฟลเดอร์
        self._analyze_folder_structure()
        
        # 3. วิเคราะห์ไฟล์ตามประเภท
        self._analyze_file_patterns()
        
        # 4. วิเคราะห์ความสัมพันธ์ระหว่างไฟล์
        self._analyze_file_relationships()
        
        # 5. วิเคราะห์การใช้งานและอายุไฟล์
        self._analyze_file_usage_patterns()
        
        # 6. วิเคราะห์ความปลอดภัยและความเสี่ยง
        self._analyze_security_risks()
        
        # 7. สรุปและให้คำแนะนำ
        self._generate_smart_recommendations()
        
    def _detect_project_type(self):
        """ตรวจจับประเภทโปรเจ็ค"""
        print("\n🔍 1. ตรวจจับประเภทโปรเจ็ค")
        print("-" * 40)
        
        # ตรวจสอบไฟล์สำคัญ
        key_files = self._get_key_files()
        
        project_type = "Unknown"
        confidence = 0
        
        # ตรวจจับ Obsidian Vault
        if any('.obsidian' in path for _, path, _ in key_files):
            project_type = "Obsidian Vault"
            confidence = 95
            
        # ตรวจจับ Web Project
        elif any(ext in ['.html', '.css', '.js'] for _, _, ext in key_files):
            project_type = "Web Project"
            confidence = 85
            
        # ตรวจจับ Data Project
        elif any(ext in ['.csv', '.json', '.xlsx'] for _, _, ext in key_files):
            project_type = "Data Project"
            confidence = 80
            
        print(f"📋 ประเภทโปรเจ็ค: {project_type}")
        print(f"🎯 ความเชื่อมั่น: {confidence}%")
        
        self.analysis_results['project_type'] = {
            'type': project_type,
            'confidence': confidence,
            'key_files': key_files
        }
        
    def _analyze_folder_structure(self):
        """วิเคราะห์โครงสร้างโฟลเดอร์"""
        print("\n📁 2. วิเคราะห์โครงสร้างโฟลเดอร์")
        print("-" * 40)
        
        # ดูโครงสร้างโฟลเดอร์
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
        
        print("📊 โครงสร้างโฟลเดอร์หลัก:")
        for i, (folder, count, size, exts) in enumerate(result, 1):
            size_mb = size / 1024 / 1024 if size else 0
            print(f"{i:2d}. {folder}")
            print(f"    📄 {count} files, {size_mb:.1f} MB")
            print(f"    📝 Extensions: {exts[:50]}...")
            print()
            
        self.analysis_results['folder_structure'] = result
        
    def _analyze_file_patterns(self):
        """วิเคราะห์รูปแบบไฟล์"""
        print("\n📈 3. วิเคราะห์รูปแบบไฟล์")
        print("-" * 40)
        
        # วิเคราะห์ไฟล์ตามประเภท
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
        """วิเคราะห์ความสัมพันธ์ระหว่างไฟล์"""
        print("\n🔗 4. วิเคราะห์ความสัมพันธ์ระหว่างไฟล์")
        print("-" * 40)
        
        # ตรวจสอบไฟล์ที่เกี่ยวข้อง
        relationships = []
        
        # ตรวจสอบไฟล์ config ที่เกี่ยวข้อง
        config_files = self._get_files_by_extensions(['.json', '.yaml', '.yml', '.config'])
        if config_files:
            print(f"⚙️ ไฟล์ Config: {len(config_files)} files")
            relationships.append(('config_files', config_files))
            
        # ตรวจสอบไฟล์ที่อาจเป็น backup
        backup_patterns = ['backup', 'bak', 'old', 'temp', 'tmp']
        backup_files = self._find_files_by_patterns(backup_patterns)
        if backup_files:
            print(f"💾 ไฟล์ Backup: {len(backup_files)} files")
            relationships.append(('backup_files', backup_files))
            
        # ตรวจสอบไฟล์ที่อาจเป็น cache
        cache_patterns = ['cache', 'tmp', 'temp', '.cache']
        cache_files = self._find_files_by_patterns(cache_patterns)
        if cache_files:
            print(f"🗂️ ไฟล์ Cache: {len(cache_files)} files")
            relationships.append(('cache_files', cache_files))
            
        self.analysis_results['file_relationships'] = relationships
        
    def _analyze_file_usage_patterns(self):
        """วิเคราะห์รูปแบบการใช้งานไฟล์"""
        print("\n⏰ 5. วิเคราะห์รูปแบบการใช้งานไฟล์")
        print("-" * 40)
        
        # ดูไฟล์ที่แก้ไขล่าสุด
        recent_files = self._get_recent_files(days=7)
        old_files = self._get_old_files(days=90)
        
        print(f"🆕 ไฟล์ที่แก้ไขล่าสุด (7 วัน): {len(recent_files)} files")
        print(f"📅 ไฟล์เก่า (90 วัน): {len(old_files)} files")
        
        # วิเคราะห์ไฟล์ที่ไม่ได้ใช้
        unused_files = self._identify_unused_files()
        if unused_files:
            print(f"🚫 ไฟล์ที่อาจไม่ได้ใช้: {len(unused_files)} files")
            
        self.analysis_results['usage_patterns'] = {
            'recent_files': recent_files,
            'old_files': old_files,
            'unused_files': unused_files
        }
        
    def _analyze_security_risks(self):
        """วิเคราะห์ความเสี่ยงด้านความปลอดภัย"""
        print("\n🔒 6. วิเคราะห์ความเสี่ยงด้านความปลอดภัย")
        print("-" * 40)
        
        risks = []
        
        # ตรวจสอบไฟล์ที่อาจมีข้อมูลสำคัญ
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        sensitive_files = self._find_files_by_patterns(sensitive_patterns)
        if sensitive_files:
            print(f"⚠️ ไฟล์ที่อาจมีข้อมูลสำคัญ: {len(sensitive_files)} files")
            risks.append(('sensitive_files', sensitive_files))
            
        # ตรวจสอบไฟล์ executable
        exe_files = self._get_files_by_extensions(['.exe', '.bat', '.cmd', '.ps1'])
        if exe_files:
            print(f"⚡ ไฟล์ Executable: {len(exe_files)} files")
            risks.append(('executable_files', exe_files))
            
        # ตรวจสอบไฟล์ที่อาจเป็น malware
        suspicious_patterns = ['virus', 'malware', 'trojan', 'spyware']
        suspicious_files = self._find_files_by_patterns(suspicious_patterns)
        if suspicious_files:
            print(f"🚨 ไฟล์ที่น่าสงสัย: {len(suspicious_files)} files")
            risks.append(('suspicious_files', suspicious_files))
            
        self.analysis_results['security_risks'] = risks
        
    def _generate_smart_recommendations(self):
        """สร้างคำแนะนำอัจฉริยะ"""
        print("\n🎯 7. คำแนะนำอัจฉริยะ")
        print("-" * 40)
        
        recommendations = []
        
        # วิเคราะห์จากผลการวิเคราะห์
        project_type = self.analysis_results.get('project_type', {}).get('type', 'Unknown')
        
        if project_type == "Obsidian Vault":
            recommendations.extend(self._get_obsidian_recommendations())
        elif project_type == "Web Project":
            recommendations.extend(self._get_web_recommendations())
        else:
            recommendations.extend(self._get_general_recommendations())
            
        # แสดงคำแนะนำ
        for i, (category, recs) in enumerate(recommendations, 1):
            print(f"\n📋 {category}:")
            for j, rec in enumerate(recs, 1):
                print(f"  {i}.{j} {rec}")
                
        self.analysis_results['recommendations'] = recommendations
        
    def _get_obsidian_recommendations(self):
        """คำแนะนำสำหรับ Obsidian Vault"""
        recommendations = []
        
        # ตรวจสอบ plugins ที่ไม่ได้ใช้
        plugins = self._get_obsidian_plugins()
        if len(plugins) > 20:
            recommendations.append(("Optimization", "พิจารณาลบ plugins ที่ไม่ได้ใช้ (มี plugins มากกว่า 20 ตัว)"))
            
        # ตรวจสอบไฟล์ RAR
        rar_files = self._get_files_by_extensions(['.rar'])
        if rar_files:
            recommendations.append(("Archive Management", "ตรวจสอบไฟล์ RAR ว่าจำเป็นต้องเก็บไว้หรือไม่"))
            
        # ตรวจสอบไฟล์ที่ไม่ได้ตั้งชื่อ
        unnamed_files = self._find_files_by_patterns(['ยังไม่ได้ตั้งชื่อ', 'untitled', 'new'])
        if unnamed_files:
            recommendations.append(("File Organization", "ตั้งชื่อไฟล์ที่ยังไม่ได้ตั้งชื่อให้เหมาะสม"))
            
        return recommendations
        
    def _get_web_recommendations(self):
        """คำแนะนำสำหรับ Web Project"""
        recommendations = []
        
        # ตรวจสอบไฟล์ JavaScript ที่ซ้ำ
        js_files = self._get_files_by_extensions(['.js'])
        if len(js_files) > 50:
            recommendations.append(("Code Organization", "พิจารณาใช้ bundler เพื่อรวมไฟล์ JavaScript"))
            
        return recommendations
        
    def _get_general_recommendations(self):
        """คำแนะนำทั่วไป"""
        recommendations = []
        
        # ตรวจสอบไฟล์ซ้ำ
        duplicates = self._get_duplicate_files()
        if duplicates:
            recommendations.append(("Storage Optimization", f"ลบไฟล์ซ้ำเพื่อประหยัดพื้นที่ {len(duplicates)} กลุ่ม"))
            
        # ตรวจสอบไฟล์เก่า
        old_files = self.analysis_results.get('usage_patterns', {}).get('old_files', [])
        if len(old_files) > 100:
            recommendations.append(("Archive Management", "พิจารณาเก็บไฟล์เก่าใน archive"))
            
        return recommendations
        
    # Helper methods
    def _execute_sql(self, sql, params):
        """Execute SQL query"""
        params_dict = {
            'action': 'query_sql',
            'sql': sql,
            'params': params,
            'session_id': self.session_id
        }
        result = self.tool._run(json.dumps(params_dict))
        return json.loads(result)
        
    def _get_key_files(self):
        """Get key files for project type detection"""
        sql = """
        SELECT file_name, file_path, file_extension 
        FROM files 
        WHERE session_id = ? 
        ORDER BY file_size DESC 
        LIMIT 20
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_files_by_extensions(self, extensions):
        """Get files by extensions"""
        ext_list = "', '".join(extensions)
        sql = f"""
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? AND file_extension IN ('{ext_list}')
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _find_files_by_patterns(self, patterns):
        """Find files by name patterns"""
        pattern_conditions = " OR ".join([f"file_name LIKE '%{pattern}%'" for pattern in patterns])
        sql = f"""
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? AND ({pattern_conditions})
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_recent_files(self, days=7):
        """Get recently modified files"""
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date > datetime('now', '-{} days')
        """.format(days)
        return self._execute_sql(sql, [self.session_id])
        
    def _get_old_files(self, days=90):
        """Get old files"""
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date < datetime('now', '-{} days')
        """.format(days)
        return self._execute_sql(sql, [self.session_id])
        
    def _get_duplicate_files(self):
        """Get duplicate files"""
        sql = """
        SELECT hash_md5, COUNT(*) as count 
        FROM files 
        WHERE session_id = ? AND hash_md5 IS NOT NULL 
        GROUP BY hash_md5 
        HAVING COUNT(*) > 1
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _get_obsidian_plugins(self):
        """Get Obsidian plugins"""
        sql = """
        SELECT file_name, file_path, file_size 
        FROM files 
        WHERE session_id = ? 
        AND file_path LIKE '%.obsidian\\plugins%'
        AND file_name = 'main.js'
        """
        return self._execute_sql(sql, [self.session_id])
        
    def _identify_unused_files(self):
        """Identify potentially unused files"""
        # ไฟล์ที่ไม่ได้แก้ไขนานและมีขนาดเล็ก
        sql = """
        SELECT file_name, file_path, file_size, modified_date 
        FROM files 
        WHERE session_id = ? 
        AND modified_date < datetime('now', '-30 days')
        AND file_size < 1024
        """
        return self._execute_sql(sql, [self.session_id])

def main():
    session_id = 'scan_1755714528'  # Vault session
    analyzer = SmartAnalyzer(session_id)
    analyzer.analyze_project_structure()
    
    # บันทึกผลการวิเคราะห์
    with open('smart_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(analyzer.analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 บันทึกผลการวิเคราะห์ใน: smart_analysis_report.json")

if __name__ == "__main__":
    main()
