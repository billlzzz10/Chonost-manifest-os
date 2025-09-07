#!/usr/bin/env python3
"""
AI-Ready File System Analyzer
สร้างข้อมูลที่ AI ใดๆ ก็สามารถเข้าใจโครงสร้างโฟลเดอร์ได้อย่างลึกซึ้ง
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from file_system_analyzer import FileSystemMCPTool

class AIReadyAnalyzer:
    def __init__(self, session_id):
        self.tool = FileSystemMCPTool()
        self.session_id = session_id
        self.analysis_data = {}
        
    def generate_ai_ready_analysis(self):
        """สร้างการวิเคราะห์ที่พร้อมสำหรับ AI"""
        print("🤖 AI-Ready File System Analysis")
        print("=" * 50)
        
        # 1. Project Context Analysis
        self._analyze_project_context()
        
        # 2. File System Intelligence
        self._analyze_file_intelligence()
        
        # 3. Content Relationship Mapping
        self._analyze_content_relationships()
        
        # 4. Usage Pattern Intelligence
        self._analyze_usage_intelligence()
        
        # 5. Risk Assessment
        self._analyze_risk_assessment()
        
        # 6. Generate AI Insights
        self._generate_ai_insights()
        
        # 7. Save AI-Ready Data
        self._save_ai_ready_data()
        
    def _analyze_project_context(self):
        """วิเคราะห์บริบทของโปรเจ็ค"""
        print("1. Analyzing Project Context...")
        
        # Detect project type and structure
        project_info = {
            "project_type": self._detect_project_type(),
            "folder_structure": self._get_folder_hierarchy(),
            "file_distribution": self._get_file_distribution(),
            "size_analysis": self._get_size_analysis()
        }
        
        self.analysis_data['project_context'] = project_info
        print(f"   Project Type: {project_info['project_type']['type']}")
        print(f"   Confidence: {project_info['project_type']['confidence']}%")
        
    def _analyze_file_intelligence(self):
        """วิเคราะห์ความฉลาดของไฟล์"""
        print("2. Analyzing File Intelligence...")
        
        file_intelligence = {
            "file_categories": self._categorize_files(),
            "file_patterns": self._analyze_file_patterns(),
            "file_relationships": self._find_file_relationships(),
            "file_metadata": self._analyze_file_metadata()
        }
        
        self.analysis_data['file_intelligence'] = file_intelligence
        print(f"   File Categories: {len(file_intelligence['file_categories'])} categories")
        
    def _analyze_content_relationships(self):
        """วิเคราะห์ความสัมพันธ์ของเนื้อหา"""
        print("3. Analyzing Content Relationships...")
        
        content_analysis = {
            "content_clusters": self._find_content_clusters(),
            "dependency_mapping": self._map_dependencies(),
            "content_hierarchy": self._build_content_hierarchy(),
            "cross_references": self._find_cross_references()
        }
        
        self.analysis_data['content_relationships'] = content_analysis
        print(f"   Content Clusters: {len(content_analysis['content_clusters'])} clusters")
        
    def _analyze_usage_intelligence(self):
        """วิเคราะห์ความฉลาดในการใช้งาน"""
        print("4. Analyzing Usage Intelligence...")
        
        usage_intelligence = {
            "activity_patterns": self._analyze_activity_patterns(),
            "access_frequency": self._analyze_access_frequency(),
            "modification_trends": self._analyze_modification_trends(),
            "usage_anomalies": self._detect_usage_anomalies()
        }
        
        self.analysis_data['usage_intelligence'] = usage_intelligence
        print(f"   Activity Patterns: {len(usage_intelligence['activity_patterns'])} patterns")
        
    def _analyze_risk_assessment(self):
        """ประเมินความเสี่ยง"""
        print("5. Analyzing Risk Assessment...")
        
        risk_assessment = {
            "security_risks": self._assess_security_risks(),
            "data_integrity": self._assess_data_integrity(),
            "storage_efficiency": self._assess_storage_efficiency(),
            "maintenance_risks": self._assess_maintenance_risks()
        }
        
        self.analysis_data['risk_assessment'] = risk_assessment
        print(f"   Security Risks: {len(risk_assessment['security_risks'])} identified")
        
    def _generate_ai_insights(self):
        """สร้างข้อมูลเชิงลึกสำหรับ AI"""
        print("6. Generating AI Insights...")
        
        ai_insights = {
            "contextual_understanding": self._generate_contextual_understanding(),
            "actionable_recommendations": self._generate_actionable_recommendations(),
            "predictive_analysis": self._generate_predictive_analysis(),
            "optimization_opportunities": self._identify_optimization_opportunities()
        }
        
        self.analysis_data['ai_insights'] = ai_insights
        print(f"   AI Insights: {len(ai_insights['actionable_recommendations'])} recommendations")
        
    def _save_ai_ready_data(self):
        """บันทึกข้อมูลที่พร้อมสำหรับ AI"""
        print("7. Saving AI-Ready Data...")
        
        # Create comprehensive AI-ready report
        ai_report = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "analyzer_version": "2.0",
                "ai_compatibility": "universal"
            },
            "analysis_results": self.analysis_data,
            "ai_instructions": self._generate_ai_instructions()
        }
        
        # Save as JSON for AI consumption
        with open('ai_ready_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(ai_report, f, ensure_ascii=False, indent=2, default=str)
            
        # Save as structured text for human reading
        self._save_human_readable_report()
        
        print("   ✅ AI-Ready data saved successfully!")
        
    # Helper methods for analysis
    def _detect_project_type(self):
        """ตรวจจับประเภทโปรเจ็ค"""
        key_files = self._execute_sql("""
            SELECT file_name, file_path, file_extension 
            FROM files WHERE session_id = ? 
            ORDER BY file_size DESC LIMIT 20
        """, [self.session_id])
        
        # Analyze patterns
        obsidian_indicators = sum(1 for _, path, _ in key_files if '.obsidian' in path)
        web_indicators = sum(1 for _, _, ext in key_files if ext in ['.html', '.css', '.js'])
        data_indicators = sum(1 for _, _, ext in key_files if ext in ['.csv', '.json', '.xlsx'])
        
        if obsidian_indicators > 0:
            return {"type": "Obsidian Vault", "confidence": 95, "indicators": obsidian_indicators}
        elif web_indicators > 5:
            return {"type": "Web Project", "confidence": 85, "indicators": web_indicators}
        elif data_indicators > 3:
            return {"type": "Data Project", "confidence": 80, "indicators": data_indicators}
        else:
            return {"type": "General Project", "confidence": 60, "indicators": 0}
            
    def _get_folder_hierarchy(self):
        """สร้างลำดับชั้นโฟลเดอร์"""
        folders = self._execute_sql("""
            SELECT parent_directory, COUNT(*) as file_count, 
                   SUM(file_size) as total_size
            FROM files WHERE session_id = ? 
            GROUP BY parent_directory 
            ORDER BY file_count DESC
        """, [self.session_id])
        
        hierarchy = {}
        for folder, count, size in folders:
            depth = folder.count('\\')
            hierarchy[folder] = {
                "depth": depth,
                "file_count": count,
                "total_size": size,
                "size_mb": size / 1024 / 1024 if size else 0
            }
            
        return hierarchy
        
    def _get_file_distribution(self):
        """วิเคราะห์การกระจายของไฟล์"""
        extensions = self._execute_sql("""
            SELECT file_extension, COUNT(*) as count, 
                   SUM(file_size) as total_size
            FROM files WHERE session_id = ? 
            GROUP BY file_extension 
            ORDER BY count DESC
        """, [self.session_id])
        
        distribution = {}
        for ext, count, size in extensions:
            ext_name = ext if ext else "[no extension]"
            distribution[ext_name] = {
                "count": count,
                "total_size": size,
                "size_mb": size / 1024 / 1024 if size else 0,
                "percentage": (count / sum(e[1] for e in extensions)) * 100
            }
            
        return distribution
        
    def _get_size_analysis(self):
        """วิเคราะห์ขนาดไฟล์"""
        size_stats = self._execute_sql("""
            SELECT 
                COUNT(*) as total_files,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_size,
                MIN(file_size) as min_size,
                MAX(file_size) as max_size
            FROM files WHERE session_id = ?
        """, [self.session_id])
        
        if size_stats:
            stats = size_stats[0]
            return {
                "total_files": stats[0],
                "total_size_bytes": stats[1],
                "total_size_mb": stats[1] / 1024 / 1024 if stats[1] else 0,
                "average_size_bytes": stats[2],
                "average_size_kb": stats[2] / 1024 if stats[2] else 0,
                "smallest_file_bytes": stats[3],
                "largest_file_bytes": stats[4],
                "largest_file_mb": stats[4] / 1024 / 1024 if stats[4] else 0
            }
        return {}
        
    def _categorize_files(self):
        """จัดหมวดหมู่ไฟล์"""
        categories = {
            "documentation": ['.md', '.txt', '.pdf', '.doc', '.docx'],
            "code": ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css'],
            "data": ['.csv', '.json', '.xml', '.sql', '.db'],
            "media": ['.jpg', '.png', '.gif', '.mp4', '.mp3', '.wav'],
            "archive": ['.zip', '.rar', '.tar', '.gz', '.7z'],
            "config": ['.config', '.ini', '.yaml', '.yml', '.toml', '.env'],
            "executable": ['.exe', '.bat', '.cmd', '.ps1']
        }
        
        categorized = {}
        for category, extensions in categories.items():
            files = self._get_files_by_extensions(extensions)
            if files:
                categorized[category] = {
                    "count": len(files),
                    "total_size": sum(size for _, _, size in files),
                    "files": [{"name": name, "path": path, "size": size} for name, path, size in files]
                }
                
        return categorized
        
    def _analyze_file_patterns(self):
        """วิเคราะห์รูปแบบไฟล์"""
        patterns = {
            "duplicate_names": self._find_duplicate_names(),
            "naming_conventions": self._analyze_naming_conventions(),
            "file_relationships": self._find_file_relationships(),
            "temporal_patterns": self._analyze_temporal_patterns()
        }
        return patterns
        
    def _find_content_clusters(self):
        """ค้นหาคลัสเตอร์ของเนื้อหา"""
        # Group files by directory and analyze content patterns
        clusters = {}
        
        # Analyze by directory structure
        directories = self._execute_sql("""
            SELECT parent_directory, COUNT(*) as file_count,
                   GROUP_CONCAT(DISTINCT file_extension) as extensions
            FROM files WHERE session_id = ? 
            GROUP BY parent_directory
        """, [self.session_id])
        
        for directory, count, extensions in directories:
            clusters[directory] = {
                "file_count": count,
                "extensions": extensions.split(',') if extensions else [],
                "content_type": self._determine_content_type(extensions),
                "complexity_score": self._calculate_complexity_score(count, extensions)
            }
            
        return clusters
        
    def _analyze_activity_patterns(self):
        """วิเคราะห์รูปแบบการใช้งาน"""
        # Analyze file modification patterns
        recent_files = self._execute_sql("""
            SELECT file_name, file_path, modified_date, file_size
            FROM files WHERE session_id = ? 
            ORDER BY modified_date DESC LIMIT 50
        """, [self.session_id])
        
        patterns = {
            "recent_activity": len(recent_files),
            "active_files": [{"name": name, "path": path, "modified": modified, "size": size} 
                           for name, path, modified, size in recent_files],
            "activity_trends": self._calculate_activity_trends(recent_files)
        }
        
        return patterns
        
    def _assess_security_risks(self):
        """ประเมินความเสี่ยงด้านความปลอดภัย"""
        risks = []
        
        # Check for sensitive files
        sensitive_files = self._find_files_by_patterns(['password', 'secret', 'key', 'token', 'credential'])
        if sensitive_files:
            risks.append({
                "type": "sensitive_data",
                "severity": "high",
                "description": "Files containing potentially sensitive information",
                "count": len(sensitive_files),
                "files": sensitive_files
            })
            
        # Check for executable files
        exe_files = self._get_files_by_extensions(['.exe', '.bat', '.cmd', '.ps1'])
        if exe_files:
            risks.append({
                "type": "executable_files",
                "severity": "medium",
                "description": "Executable files found",
                "count": len(exe_files),
                "files": exe_files
            })
            
        return risks
        
    def _generate_contextual_understanding(self):
        """สร้างความเข้าใจเชิงบริบท"""
        context = {
            "project_purpose": self._infer_project_purpose(),
            "user_workflow": self._infer_user_workflow(),
            "content_organization": self._analyze_content_organization(),
            "collaboration_patterns": self._detect_collaboration_patterns()
        }
        return context
        
    def _generate_actionable_recommendations(self):
        """สร้างคำแนะนำที่ปฏิบัติได้"""
        recommendations = []
        
        # Analyze based on project type
        project_type = self.analysis_data.get('project_context', {}).get('project_type', {}).get('type', 'Unknown')
        
        if project_type == "Obsidian Vault":
            recommendations.extend(self._get_obsidian_specific_recommendations())
        else:
            recommendations.extend(self._get_general_recommendations())
            
        return recommendations
        
    def _generate_ai_instructions(self):
        """สร้างคำแนะนำสำหรับ AI"""
        return {
            "analysis_approach": "comprehensive_file_system_intelligence",
            "focus_areas": ["content_organization", "efficiency_optimization", "security_assessment"],
            "decision_framework": "context_aware_recommendations",
            "priority_considerations": ["user_workflow", "data_integrity", "storage_efficiency"]
        }
        
    # Utility methods
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
        
    def _save_human_readable_report(self):
        """บันทึกรายงานที่อ่านได้สำหรับมนุษย์"""
        report = f"""
# AI-Ready File System Analysis Report

## Project Overview
- **Type**: {self.analysis_data.get('project_context', {}).get('project_type', {}).get('type', 'Unknown')}
- **Total Files**: {self.analysis_data.get('project_context', {}).get('size_analysis', {}).get('total_files', 0)}
- **Total Size**: {self.analysis_data.get('project_context', {}).get('size_analysis', {}).get('total_size_mb', 0):.1f} MB

## Key Insights
{self._format_insights_for_humans()}

## Recommendations
{self._format_recommendations_for_humans()}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        with open('human_readable_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
    def _format_insights_for_humans(self):
        """จัดรูปแบบข้อมูลเชิงลึกสำหรับมนุษย์"""
        insights = self.analysis_data.get('ai_insights', {})
        return f"""
- **Content Organization**: {insights.get('contextual_understanding', {}).get('content_organization', 'Not analyzed')}
- **User Workflow**: {insights.get('contextual_understanding', {}).get('user_workflow', 'Not analyzed')}
- **Security Risks**: {len(insights.get('risk_assessment', {}).get('security_risks', []))} identified
        """
        
    def _format_recommendations_for_humans(self):
        """จัดรูปแบบคำแนะนำสำหรับมนุษย์"""
        recommendations = self.analysis_data.get('ai_insights', {}).get('actionable_recommendations', [])
        if not recommendations:
            return "No specific recommendations generated."
            
        formatted = ""
        for i, rec in enumerate(recommendations, 1):
            formatted += f"{i}. {rec}\n"
        return formatted

def main():
    session_id = 'scan_1755714528'  # Vault session
    analyzer = AIReadyAnalyzer(session_id)
    analyzer.generate_ai_ready_analysis()
    
    print("\n🎉 AI-Ready Analysis Complete!")
    print("📁 Files generated:")
    print("   - ai_ready_analysis.json (for AI consumption)")
    print("   - human_readable_report.md (for human reading)")

if __name__ == "__main__":
    main()
