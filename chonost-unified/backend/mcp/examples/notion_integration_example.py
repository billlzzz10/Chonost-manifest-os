#!/usr/bin/env python3
"""
ตัวอย่างการใช้งาน Notion MCP Integration
แสดงวิธีการใช้งานฟีเจอร์ต่างๆ ของ Notion MCP Integration
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# เพิ่ม path สำหรับ import
sys.path.append('../src/server')
sys.path.append('../src/core')

from notion_mcp_integration import NotionMCPIntegration
from file_system_analyzer import FileSystemMCPTool

class NotionIntegrationExample:
    """
    ตัวอย่างการใช้งาน Notion MCP Integration
    """
    
    def __init__(self, notion_token: str = None, parent_page_id: str = None):
        """
        Initialize example
        
        Args:
            notion_token: Notion Integration Token
            parent_page_id: ID ของหน้า parent ใน Notion
        """
        self.notion_token = notion_token or os.getenv('NOTION_INTEGRATION_TOKEN')
        self.parent_page_id = parent_page_id or os.getenv('NOTION_PARENT_PAGE_ID')
        self.notion = None
        
        if not self.notion_token:
            raise ValueError("ต้องตั้งค่า Notion Integration Token")
        
        if not self.parent_page_id:
            print("⚠️  ไม่ได้ตั้งค่า parent page ID - จะใช้การค้นหาแทน")
    
    async def setup(self):
        """ตั้งค่า Notion MCP Integration"""
        print("🚀 กำลังตั้งค่า Notion MCP Integration...")
        
        self.notion = NotionMCPIntegration(self.notion_token)
        
        # เริ่มต้น MCP Server
        if await self.notion.start_mcp_server():
            print("✅ Notion MCP Integration พร้อมใช้งาน")
            return True
        else:
            print("❌ ไม่สามารถเริ่มต้น Notion MCP Integration ได้")
            return False
    
    async def cleanup(self):
        """ทำความสะอาด resources"""
        if self.notion:
            await self.notion.stop_mcp_server()
            print("✅ หยุด Notion MCP Integration แล้ว")
    
    async def example_1_basic_operations(self):
        """ตัวอย่าง 1: การใช้งานพื้นฐาน"""
        print("\n📋 ตัวอย่าง 1: การใช้งานพื้นฐาน")
        print("=" * 50)
        
        # 1. ทดสอบการเชื่อมต่อ
        print("1. ทดสอบการเชื่อมต่อ...")
        result = await self.notion.send_mcp_request("API-get-self", {})
        if "error" not in result:
            print(f"✅ เชื่อมต่อสำเร็จ: {result.get('result', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ เชื่อมต่อล้มเหลว: {result.get('error')}")
            return
        
        # 2. ค้นหาหน้า
        print("\n2. ค้นหาหน้า...")
        search_result = await self.notion.search_pages(
            query="file analysis",
            filter_type="page"
        )
        
        if "error" not in search_result:
            pages = search_result.get('result', {}).get('results', [])
            print(f"✅ พบหน้า {len(pages)} หน้า")
            for page in pages[:3]:  # แสดง 3 หน้าแรก
                title = page.get('properties', {}).get('title', {}).get('title', [])
                if title:
                    print(f"   - {title[0].get('text', {}).get('content', 'Untitled')}")
        else:
            print(f"❌ ค้นหาล้มเหลว: {search_result.get('error')}")
    
    async def example_2_file_structure_export(self):
        """ตัวอย่าง 2: การส่งออกโครงสร้างไฟล์"""
        print("\n📁 ตัวอย่าง 2: การส่งออกโครงสร้างไฟล์")
        print("=" * 50)
        
        if not self.parent_page_id:
            print("⚠️  ข้ามตัวอย่างนี้ - ไม่ได้ตั้งค่า parent page ID")
            return
        
        # 1. วิเคราะห์โครงสร้างไฟล์
        print("1. วิเคราะห์โครงสร้างไฟล์...")
        analyzer = FileSystemMCPTool()
        
        # สร้างข้อมูลตัวอย่าง
        sample_structure = {
            "summary": "การวิเคราะห์โครงสร้างไฟล์ตัวอย่าง",
            "statistics": {
                "total_files": 15,
                "total_directories": 5,
                "total_size": "2.5 MB"
            },
            "file_tree": [
                {
                    "name": "src",
                    "type": "directory",
                    "children": [
                        {
                            "name": "main.py",
                            "type": "file",
                            "size": 1024
                        },
                        {
                            "name": "utils",
                            "type": "directory",
                            "children": [
                                {
                                    "name": "helper.py",
                                    "type": "file",
                                    "size": 512
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "docs",
                    "type": "directory",
                    "children": [
                        {
                            "name": "README.md",
                            "type": "file",
                            "size": 2048
                        }
                    ]
                }
            ]
        }
        
        # 2. ส่งออกไปยัง Notion
        print("2. ส่งออกไปยัง Notion...")
        result = await self.notion.export_file_structure_to_notion(
            file_structure=sample_structure,
            parent_page_id=self.parent_page_id
        )
        
        if "error" not in result:
            page_id = result.get('result', {}).get('id', 'Unknown')
            print(f"✅ ส่งออกสำเร็จ: {page_id}")
            print(f"   ดูได้ที่: https://notion.so/{page_id.replace('-', '')}")
        else:
            print(f"❌ ส่งออกล้มเหลว: {result.get('error')}")
    
    async def example_3_database_management(self):
        """ตัวอย่าง 3: การจัดการ Database"""
        print("\n🗄️ ตัวอย่าง 3: การจัดการ Database")
        print("=" * 50)
        
        if not self.parent_page_id:
            print("⚠️  ข้ามตัวอย่างนี้ - ไม่ได้ตั้งค่า parent page ID")
            return
        
        # 1. สร้าง database
        print("1. สร้าง database สำหรับการวิเคราะห์ไฟล์...")
        database_result = await self.notion.create_file_analysis_database(
            parent_page_id=self.parent_page_id
        )
        
        if "error" in database_result:
            print(f"❌ สร้าง database ล้มเหลว: {database_result.get('error')}")
            return
        
        database_id = database_result.get('result', {}).get('id', 'Unknown')
        print(f"✅ สร้าง database สำเร็จ: {database_id}")
        
        # 2. เพิ่มข้อมูลไฟล์
        print("\n2. เพิ่มข้อมูลไฟล์ลงใน database...")
        sample_files = [
            {
                "name": "main.py",
                "path": "/path/to/main.py",
                "size": 1024,
                "modified": "2024-01-01T00:00:00Z"
            },
            {
                "name": "config.json",
                "path": "/path/to/config.json",
                "size": 512,
                "modified": "2024-01-02T00:00:00Z"
            },
            {
                "name": "README.md",
                "path": "/path/to/README.md",
                "size": 2048,
                "modified": "2024-01-03T00:00:00Z"
            }
        ]
        
        for file_info in sample_files:
            result = await self.notion.add_file_to_database(
                database_id=database_id,
                file_info=file_info
            )
            
            if "error" not in result:
                print(f"✅ เพิ่มไฟล์ {file_info['name']} สำเร็จ")
            else:
                print(f"❌ เพิ่มไฟล์ {file_info['name']} ล้มเหลว: {result.get('error')}")
        
        # 3. ค้นหาข้อมูลใน database
        print("\n3. ค้นหาข้อมูลใน database...")
        query_result = await self.notion.query_database(
            database_id=database_id,
            filter={
                "property": "File Type",
                "select": {"equals": "Code"}
            },
            sorts=[
                {
                    "property": "Size (bytes)",
                    "direction": "descending"
                }
            ]
        )
        
        if "error" not in query_result:
            results = query_result.get('result', {}).get('results', [])
            print(f"✅ พบไฟล์ Code {len(results)} ไฟล์")
            for item in results:
                properties = item.get('properties', {})
                name = properties.get('File Name', {}).get('title', [])
                if name:
                    print(f"   - {name[0].get('text', {}).get('content', 'Unknown')}")
        else:
            print(f"❌ ค้นหาล้มเหลว: {query_result.get('error')}")
    
    async def example_4_page_management(self):
        """ตัวอย่าง 4: การจัดการหน้า"""
        print("\n📄 ตัวอย่าง 4: การจัดการหน้า")
        print("=" * 50)
        
        if not self.parent_page_id:
            print("⚠️  ข้ามตัวอย่างนี้ - ไม่ได้ตั้งค่า parent page ID")
            return
        
        # 1. สร้างหน้าใหม่
        print("1. สร้างหน้าใหม่...")
        page_properties = {
            "title": {
                "title": [{"text": {"content": f"File Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]
            }
        }
        
        page_content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": "📊 File Analysis Report"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "รายงานการวิเคราะห์ไฟล์ระบบ"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": "📁 Total Files: 150"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": "📂 Total Directories: 25"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": "💾 Total Size: 15.2 MB"}}]
                }
            }
        ]
        
        create_result = await self.notion.create_page(
            parent_id=self.parent_page_id,
            properties=page_properties,
            children=page_content
        )
        
        if "error" in create_result:
            print(f"❌ สร้างหน้าล้มเหลว: {create_result.get('error')}")
            return
        
        page_id = create_result.get('result', {}).get('id', 'Unknown')
        print(f"✅ สร้างหน้าสำเร็จ: {page_id}")
        
        # 2. อัปเดตหน้า
        print("\n2. อัปเดตหน้า...")
        update_properties = {
            "title": {
                "title": [{"text": {"content": f"Updated File Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]
            }
        }
        
        update_result = await self.notion.update_page(
            page_id=page_id,
            properties=update_properties
        )
        
        if "error" not in update_result:
            print("✅ อัปเดตหน้าสำเร็จ")
        else:
            print(f"❌ อัปเดตหน้าล้มเหลว: {update_result.get('error')}")
        
        # 3. เพิ่ม content blocks
        print("\n3. เพิ่ม content blocks...")
        additional_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🔍 Analysis Details"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "รายละเอียดการวิเคราะห์เพิ่มเติม"}}]
                }
            }
        ]
        
        append_result = await self.notion.append_block_children(
            block_id=page_id,
            children=additional_blocks
        )
        
        if "error" not in append_result:
            print("✅ เพิ่ม content blocks สำเร็จ")
        else:
            print(f"❌ เพิ่ม content blocks ล้มเหลว: {append_result.get('error')}")
    
    async def example_5_batch_operations(self):
        """ตัวอย่าง 5: การประมวลผลแบบ Batch"""
        print("\n⚡ ตัวอย่าง 5: การประมวลผลแบบ Batch")
        print("=" * 50)
        
        if not self.parent_page_id:
            print("⚠️  ข้ามตัวอย่างนี้ - ไม่ได้ตั้งค่า parent page ID")
            return
        
        # สร้างข้อมูลไฟล์จำนวนมาก
        print("1. สร้างข้อมูลไฟล์จำนวนมาก...")
        batch_files = []
        for i in range(10):
            batch_files.append({
                "name": f"file_{i:03d}.py",
                "path": f"/path/to/file_{i:03d}.py",
                "size": 1024 + (i * 100),
                "modified": f"2024-01-{i+1:02d}T00:00:00Z"
            })
        
        # สร้าง database สำหรับ batch processing
        print("2. สร้าง database สำหรับ batch processing...")
        database_result = await self.notion.create_file_analysis_database(
            parent_page_id=self.parent_page_id
        )
        
        if "error" in database_result:
            print(f"❌ สร้าง database ล้มเหลว: {database_result.get('error')}")
            return
        
        database_id = database_result.get('result', {}).get('id', 'Unknown')
        print(f"✅ สร้าง database สำเร็จ: {database_id}")
        
        # เพิ่มไฟล์แบบ batch
        print("3. เพิ่มไฟล์แบบ batch...")
        success_count = 0
        error_count = 0
        
        for file_info in batch_files:
            result = await self.notion.add_file_to_database(
                database_id=database_id,
                file_info=file_info
            )
            
            if "error" not in result:
                success_count += 1
            else:
                error_count += 1
                print(f"   ❌ {file_info['name']}: {result.get('error')}")
        
        print(f"✅ เพิ่มไฟล์สำเร็จ: {success_count} ไฟล์")
        if error_count > 0:
            print(f"❌ เพิ่มไฟล์ล้มเหลว: {error_count} ไฟล์")
        
        # ค้นหาข้อมูลแบบ batch
        print("\n4. ค้นหาข้อมูลแบบ batch...")
        query_result = await self.notion.query_database(
            database_id=database_id,
            page_size=100
        )
        
        if "error" not in query_result:
            results = query_result.get('result', {}).get('results', [])
            print(f"✅ พบไฟล์ทั้งหมด {len(results)} ไฟล์")
            
            # จัดกลุ่มตามประเภทไฟล์
            file_types = {}
            for item in results:
                properties = item.get('properties', {})
                file_type = properties.get('File Type', {}).get('select', {}).get('name', 'Unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            print("   📊 สรุปตามประเภทไฟล์:")
            for file_type, count in file_types.items():
                print(f"      - {file_type}: {count} ไฟล์")
        else:
            print(f"❌ ค้นหาล้มเหลว: {query_result.get('error')}")
    
    async def run_all_examples(self):
        """รันตัวอย่างทั้งหมด"""
        print("🎯 เริ่มต้นการทดสอบ Notion MCP Integration")
        print("=" * 60)
        
        try:
            # ตั้งค่า
            if not await self.setup():
                return
            
            # รันตัวอย่าง
            await self.example_1_basic_operations()
            await self.example_2_file_structure_export()
            await self.example_3_database_management()
            await self.example_4_page_management()
            await self.example_5_batch_operations()
            
            print("\n🎉 การทดสอบเสร็จสิ้น!")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
        
        finally:
            # ทำความสะอาด
            await self.cleanup()

async def main():
    """Main function"""
    print("🚀 Notion MCP Integration Examples")
    print("=" * 40)
    
    # ตรวจสอบ environment variables
    token = os.getenv('NOTION_INTEGRATION_TOKEN')
    parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')
    
    if not token:
        print("❌ กรุณาตั้งค่า NOTION_INTEGRATION_TOKEN environment variable")
        print("ตัวอย่าง: export NOTION_INTEGRATION_TOKEN='ntn_your_token_here'")
        return
    
    if not parent_page_id:
        print("⚠️  ไม่ได้ตั้งค่า NOTION_PARENT_PAGE_ID")
        print("ตัวอย่าง: export NOTION_PARENT_PAGE_ID='your_page_id_here'")
        print("บางตัวอย่างจะถูกข้าม")
    
    # สร้างและรันตัวอย่าง
    example = NotionIntegrationExample(token, parent_page_id)
    await example.run_all_examples()

if __name__ == "__main__":
    asyncio.run(main())
