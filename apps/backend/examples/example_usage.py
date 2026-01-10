#!/usr/bin/env python3
"""
ตัวอย่างการใช้งาน File System MCP Tool
"""

import json
import os
from file_system_analyzer import FileSystemMCPTool

def main():
    print("🚀 File System MCP Tool - Example Usage")
    print("=" * 50)
    
    # สร้าง tool instance
    tool = FileSystemMCPTool()
    
    # ตัวอย่างการสแกนโฟลเดอร์ปัจจุบัน
    current_dir = os.getcwd()
    print(f"📁 Scanning directory: {current_dir}")
    
    # สแกนโฟลเดอร์
    scan_params = {
        "action": "scan",
        "path": current_dir,
        "config": {
            "max_depth": 3,  # จำกัดความลึก
            "include_hidden": False,  # ไม่รวมไฟล์ซ่อน
            "calculate_hashes": True,
            "hash_size_limit_mb": 10  # จำกัดขนาดไฟล์สำหรับ hash
        }
    }
    
    print("⏳ Scanning...")
    result = tool._run(json.dumps(scan_params))
    print(f"✅ Scan result: {result}")
    
    # ดึง session ID จากผลลัพธ์
    if "Session ID:" in result:
        session_id = result.split("Session ID: ")[1].strip()
        print(f"📋 Session ID: {session_id}")
        
        # ทดสอบ Natural Language Queries
        print("\n🗣️ Testing Natural Language Queries:")
        
        queries = [
            "show me large files",
            "find duplicate files", 
            "give me summary",
            "show files with extension .py"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: '{query}'")
            query_params = {
                "action": "query_natural",
                "request": query,
                "session_id": session_id
            }
            result = tool._run(json.dumps(query_params))
            print(f"Result: {result[:200]}...")
        
        # ทดสอบ SQL Queries
        print("\n💾 Testing SQL Queries:")
        
        sql_queries = [
            ("SELECT file_extension, COUNT(*) as count FROM files WHERE session_id = ? GROUP BY file_extension ORDER BY count DESC LIMIT 5", "Top 5 File Types"),
            ("SELECT file_name, file_size FROM files WHERE session_id = ? ORDER BY file_size DESC LIMIT 3", "Top 3 Largest Files")
        ]
        
        for sql, desc in sql_queries:
            print(f"\n🔍 {desc}")
            sql_params = {
                "action": "query_sql",
                "sql": sql,
                "params": [session_id],
                "session_id": session_id
            }
            result = tool._run(json.dumps(sql_params))
            print(f"Result: {result[:200]}...")
    
    print("\n🎉 Example completed!")

if __name__ == "__main__":
    main()
