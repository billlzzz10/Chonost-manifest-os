#!/usr/bin/env python3
"""
Create Vault Structure - สร้างโครงสร้าง Vault อย่างสมบูรณ์
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def create_readme_content(folder_name: str, folder_type: str) -> str:
    """สร้างเนื้อหา README สำหรับแต่ละโฟลเดอร์"""
    
    templates = {
        "00_DASHBOARD": """# 📊 Dashboard

## 🎯 วัตถุประสงค์
Dashboard หลักสำหรับการจัดการและติดตามโครงการทั้งหมด

## 📁 โครงสร้าง
- **Overview** - ภาพรวมโครงการ
- **Progress** - ความคืบหน้า
- **Statistics** - สถิติต่างๆ
- **Quick Actions** - การดำเนินการด่วน

## 🔗 ลิงก์สำคัญ
- [[01_MANUSCRIPT/README|📝 Manuscript]]
- [[02_CHARACTERS/README|👥 Characters]]
- [[03_WORLDBUILDING/README|🌍 Worldbuilding]]
- [[04_PLOT-TIMELINE/README|📅 Plot & Timeline]]
- [[05_SYSTEMS-LORE/README|⚡ Systems & Lore]]
- [[06_NOTE/README|📝 Notes]]

---
*อัปเดตล่าสุด: {date}*
""",
        
        "01_MANUSCRIPT": """# 📝 Manuscript

## 🎯 วัตถุประสงค์
เก็บต้นฉบับและเนื้อหาหลักของเรื่อง

## 📁 โครงสร้าง
- **Chapters** - บทต่างๆ
- **Scenes** - ฉากต่างๆ
- **Drafts** - ร่างต่างๆ
- **Final** - ฉบับสมบูรณ์

## 📋 สถานะ
- [ ] บทที่ 1
- [ ] บทที่ 2
- [ ] บทที่ 3

---
*อัปเดตล่าสุด: {date}*
""",
        
        "02_CHARACTERS": """# 👥 Characters

## 🎯 วัตถุประสงค์
จัดการข้อมูลตัวละครทั้งหมด

## 📁 โครงสร้าง
- **Main Characters** - ตัวละครหลัก
- **Supporting Characters** - ตัวละครรอง
- **Antagonists** - ตัวละครฝ่ายตรงข้าม
- **Character Development** - การพัฒนาตัวละคร

## 👤 ตัวละครหลัก
- [ ] ตัวละคร 1
- [ ] ตัวละคร 2
- [ ] ตัวละคร 3

---
*อัปเดตล่าสุด: {date}*
""",
        
        "03_WORLDBUILDING": """# 🌍 Worldbuilding

## 🎯 วัตถุประสงค์
สร้างและจัดการโลกในเรื่อง

## 📁 โครงสร้าง
- **Locations** - สถานที่ต่างๆ
- **Cultures** - วัฒนธรรม
- **History** - ประวัติศาสตร์
- **Geography** - ภูมิศาสตร์
- **Politics** - การเมือง

## 🗺️ สถานที่สำคัญ
- [ ] สถานที่ 1
- [ ] สถานที่ 2
- [ ] สถานที่ 3

---
*อัปเดตล่าสุด: {date}*
""",
        
        "04_PLOT-TIMELINE": """# 📅 Plot & Timeline

## 🎯 วัตถุประสงค์
จัดการโครงเรื่องและไทม์ไลน์

## 📁 โครงสร้าง
- **Plot Outline** - โครงเรื่อง
- **Timeline** - ไทม์ไลน์
- **Story Arcs** - ส่วนโค้งของเรื่อง
- **Plot Points** - จุดสำคัญในเรื่อง

## 📈 โครงเรื่อง
- [ ] Act 1
- [ ] Act 2
- [ ] Act 3

---
*อัปเดตล่าสุด: {date}*
""",
        
        "05_SYSTEMS-LORE": """# ⚡ Systems & Lore

## 🎯 วัตถุประสงค์
จัดการระบบและตำนานในเรื่อง

## 📁 โครงสร้าง
- **Magic System** - ระบบเวทมนตร์
- **Technology** - เทคโนโลยี
- **Lore** - ตำนาน
- **Rules** - กฎต่างๆ

## 🔮 ระบบหลัก
- [ ] ระบบ 1
- [ ] ระบบ 2
- [ ] ระบบ 3

---
*อัปเดตล่าสุด: {date}*
""",
        
        "06_NOTE": """# 📝 Notes

## 🎯 วัตถุประสงค์
เก็บบันทึกและความคิดต่างๆ

## 📁 โครงสร้าง
- **Ideas** - ไอเดียต่างๆ
- **Research** - การวิจัย
- **References** - อ้างอิง
- **Misc** - อื่นๆ

## 💡 ไอเดียล่าสุด
- [ ] ไอเดีย 1
- [ ] ไอเดีย 2
- [ ] ไอเดีย 3

---
*อัปเดตล่าสุด: {date}*
"""
    }
    
    date = datetime.now().strftime("%Y-%m-%d")
    return templates.get(folder_name, f"# {folder_name}\n\n## 🎯 วัตถุประสงค์\n\n## 📁 โครงสร้าง\n\n---\n*อัปเดตล่าสุด: {date}*").format(date=date)

def create_dashboard_content() -> str:
    """สร้างเนื้อหา Dashboard หลัก"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# 🎯 Project Dashboard

## 📊 สถานะโครงการ
- **สถานะ**: กำลังพัฒนา
- **ความคืบหน้า**: 0%
- **อัปเดตล่าสุด**: {date}

## 🎯 เป้าหมาย
- [ ] สร้างโครงสร้างพื้นฐาน
- [ ] พัฒนาตัวละครหลัก
- [ ] สร้างโลกในเรื่อง
- [ ] เขียนบทที่ 1

## 📈 สถิติ
- **ไฟล์ทั้งหมด**: 0
- **ตัวละคร**: 0
- **ฉาก**: 0
- **บท**: 0

## 🔗 ลิงก์ด่วน
- [[01_MANUSCRIPT/README|📝 Manuscript]]
- [[02_CHARACTERS/README|👥 Characters]]
- [[03_WORLDBUILDING/README|🌍 Worldbuilding]]
- [[04_PLOT-TIMELINE/README|📅 Plot & Timeline]]
- [[05_SYSTEMS-LORE/README|⚡ Systems & Lore]]
- [[06_NOTE/README|📝 Notes]]

## 🛠️ เครื่องมือ
- [[08_Templates-Tools/README|🔧 Templates & Tools]]

---
*อัปเดตล่าสุด: {date}*
"""

def create_templates_readme() -> str:
    """สร้าง README สำหรับ 08_Templates-Tools"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# 🔧 Templates & Tools

## 🎯 วัตถุประสงค์
เก็บเทมเพลตและเครื่องมือสำหรับการเขียน

## 📁 โครงสร้าง

### 📝 Prompts
- **General**: Prompts ทั่วไปสำหรับ AI
- **Default_Prompts**: Prompts สำหรับ Copilot
- **Smart_Connections**: Prompts สำหรับ Smart Connections

### 📄 Document_Templates
เทมเพลตสำหรับเอกสารต่างๆ

### 🛠️ Tools_and_Utilities
เครื่องมือและสคริปต์ต่างๆ

### 🗄️ Databases
ฐานข้อมูลและข้อมูลอ้างอิง

## 📊 สถิติ
- **Prompts**: 20 ไฟล์
- **Templates**: 0 ไฟล์
- **Tools**: 0 ไฟล์
- **Databases**: 0 ไฟล์

---
*อัปเดตล่าสุด: {date}*
"""

def create_vault_structure():
    """สร้างโครงสร้าง Vault อย่างสมบูรณ์"""
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 เริ่มสร้างโครงสร้าง Vault อย่างสมบูรณ์")
    print("=" * 60)
    
    # 1. สร้าง README สำหรับโฟลเดอร์หลัก
    main_folders = [
        '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
        '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE'
    ]
    
    print("\n📝 สร้าง README สำหรับโฟลเดอร์หลัก...")
    for folder in main_folders:
        folder_path = os.path.join(vault_path, folder)
        readme_path = os.path.join(folder_path, "README.md")
        
        if not os.path.exists(readme_path):
            content = create_readme_content(folder, folder)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ สร้าง README: {folder}")
    
    # 2. สร้าง Dashboard หลัก
    print("\n📊 สร้าง Dashboard หลัก...")
    dashboard_path = os.path.join(vault_path, "00_DASHBOARD", "Dashboard.md")
    if not os.path.exists(dashboard_path):
        content = create_dashboard_content()
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ สร้าง Dashboard หลัก")
    
    # 3. สร้าง README สำหรับ 08_Templates-Tools
    print("\n🔧 สร้าง README สำหรับ Templates & Tools...")
    templates_readme_path = os.path.join(vault_path, "08_Templates-Tools", "README.md")
    if not os.path.exists(templates_readme_path):
        content = create_templates_readme()
        with open(templates_readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ สร้าง README สำหรับ Templates & Tools")
    
    # 4. สร้าง README สำหรับ subfolders ของ Prompts
    print("\n📝 สร้าง README สำหรับ Prompts...")
    prompts_path = os.path.join(vault_path, "08_Templates-Tools", "Prompts")
    
    prompt_types = {
        "General": "Prompts ทั่วไปสำหรับ AI",
        "Default_Prompts": "Prompts สำหรับ Copilot และการใช้งานทั่วไป",
        "Smart_Connections": "Prompts สำหรับ Smart Connections"
    }
    
    for prompt_type, description in prompt_types.items():
        prompt_folder_path = os.path.join(prompts_path, prompt_type)
        readme_path = os.path.join(prompt_folder_path, "README.md")
        
        if not os.path.exists(readme_path):
            date = datetime.now().strftime("%Y-%m-%d")
            content = f"""# 📝 {prompt_type}

## 🎯 วัตถุประสงค์
{description}

## 📁 ไฟล์ในโฟลเดอร์นี้
"""
            
            # เพิ่มรายการไฟล์ที่มีอยู่
            if os.path.exists(prompt_folder_path):
                files = [f for f in os.listdir(prompt_folder_path) if f.endswith('.md') and f != 'README.md']
                for file in sorted(files):
                    content += f"- [[{file}|{file.replace('.md', '')}]]\n"
            
            content += f"\n---\n*อัปเดตล่าสุด: {date}*"
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ สร้าง README: Prompts/{prompt_type}")
    
    print("\n🎉 การสร้างโครงสร้างเสร็จสิ้น!")

if __name__ == "__main__":
    create_vault_structure()
