#!/usr/bin/env python3
"""
Create Vault Structure.
This script creates a complete structure for an Obsidian vault, including
folders and README files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def create_readme_content(folder_name: str, folder_type: str) -> str:
    """
    Creates the content for a README file for a given folder.

    Args:
        folder_name (str): The name of the folder.
        folder_type (str): The type of the folder, which is used to determine
                           the template for the README file.

    Returns:
        str: The content of the README file.
    """
    
    templates = {
        "00_DASHBOARD": """# 📊 Dashboard

## 🎯 Purpose
The main dashboard for managing and tracking all projects.

## 📁 Structure
- **Overview** - Project overview
- **Progress** - Progress
- **Statistics** - Various statistics
- **Quick Actions** - Quick actions

## 🔗 Important Links
- [[01_MANUSCRIPT/README|📝 Manuscript]]
- [[02_CHARACTERS/README|👥 Characters]]
- [[03_WORLDBUILDING/README|🌍 Worldbuilding]]
- [[04_PLOT-TIMELINE/README|📅 Plot & Timeline]]
- [[05_SYSTEMS-LORE/README|⚡ Systems & Lore]]
- [[06_NOTE/README|📝 Notes]]

---
*Last updated: {date}*
""",
        
        "01_MANUSCRIPT": """# 📝 Manuscript

## 🎯 Purpose
To store the manuscript and main content of the story.

## 📁 Structure
- **Chapters** - Various chapters
- **Scenes** - Various scenes
- **Drafts** - Various drafts
- **Final** - Final version

## 📋 Status
- [ ] Chapter 1
- [ ] Chapter 2
- [ ] Chapter 3

---
*Last updated: {date}*
""",
        
        "02_CHARACTERS": """# 👥 Characters

## 🎯 Purpose
To manage all character information.

## 📁 Structure
- **Main Characters** - Main characters
- **Supporting Characters** - Supporting characters
- **Antagonists** - Antagonists
- **Character Development** - Character development

## 👤 Main Characters
- [ ] Character 1
- [ ] Character 2
- [ ] Character 3

---
*Last updated: {date}*
""",
        
        "03_WORLDBUILDING": """# 🌍 Worldbuilding

## 🎯 Purpose
To create and manage the world in the story.

## 📁 Structure
- **Locations** - Various locations
- **Cultures** - Cultures
- **History** - History
- **Geography** - Geography
- **Politics** - Politics

## 🗺️ Important Locations
- [ ] Location 1
- [ ] Location 2
- [ ] Location 3

---
*Last updated: {date}*
""",
        
        "04_PLOT-TIMELINE": """# 📅 Plot & Timeline

## 🎯 Purpose
To manage the plot and timeline.

## 📁 Structure
- **Plot Outline** - Plot outline
- **Timeline** - Timeline
- **Story Arcs** - Story arcs
- **Plot Points** - Plot points

## 📈 Plot
- [ ] Act 1
- [ ] Act 2
- [ ] Act 3

---
*Last updated: {date}*
""",
        
        "05_SYSTEMS-LORE": """# ⚡ Systems & Lore

## 🎯 Purpose
To manage the systems and lore in the story.

## 📁 Structure
- **Magic System** - Magic system
- **Technology** - Technology
- **Lore** - Lore
- **Rules** - Various rules

## 🔮 Main Systems
- [ ] System 1
- [ ] System 2
- [ ] System 3

---
*Last updated: {date}*
""",
        
        "06_NOTE": """# 📝 Notes

## 🎯 Purpose
To store notes and ideas.

## 📁 Structure
- **Ideas** - Various ideas
- **Research** - Research
- **References** - References
- **Misc** - Miscellaneous

## 💡 Latest Ideas
- [ ] Idea 1
- [ ] Idea 2
- [ ] Idea 3

---
*Last updated: {date}*
"""
    }
    
    date = datetime.now().strftime("%Y-%m-%d")
    return templates.get(folder_name, f"# {folder_name}\n\n## 🎯 Purpose\n\n## 📁 Structure\n\n---\n*Last updated: {date}*").format(date=date)

def create_dashboard_content() -> str:
    """
    Creates the content for the main dashboard file.

    Returns:
        str: The content of the main dashboard file.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# 🎯 Project Dashboard

## 📊 Project Status
- **Status**: In development
- **Progress**: 0%
- **Last updated**: {date}

## 🎯 Goals
- [ ] Create basic structure
- [ ] Develop main characters
- [ ] Create the world of the story
- [ ] Write Chapter 1

## 📈 Statistics
- **Total files**: 0
- **Characters**: 0
- **Scenes**: 0
- **Chapters**: 0

## 🔗 Quick Links
- [[01_MANUSCRIPT/README|📝 Manuscript]]
- [[02_CHARACTERS/README|👥 Characters]]
- [[03_WORLDBUILDING/README|🌍 Worldbuilding]]
- [[04_PLOT-TIMELINE/README|📅 Plot & Timeline]]
- [[05_SYSTEMS-LORE/README|⚡ Systems & Lore]]
- [[06_NOTE/README|📝 Notes]]

## 🛠️ Tools
- [[08_Templates-Tools/README|🔧 Templates & Tools]]

---
*Last updated: {date}*
"""

def create_templates_readme() -> str:
    """
    Creates the content for the README file in the '08_Templates-Tools' directory.

    Returns:
        str: The content of the README file.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# 🔧 Templates & Tools

## 🎯 Purpose
To store templates and tools for writing.

## 📁 Structure

### 📝 Prompts
- **General**: General prompts for AI
- **Default_Prompts**: Prompts for Copilot
- **Smart_Connections**: Prompts for Smart Connections

### 📄 Document_Templates
Templates for various documents.

### 🛠️ Tools_and_Utilities
Various tools and scripts.

### 🗄️ Databases
Databases and reference data.

## 📊 Statistics
- **Prompts**: 20 files
- **Templates**: 0 files
- **Tools**: 0 files
- **Databases**: 0 files

---
*Last updated: {date}*
"""

def create_vault_structure():
    """
    Creates the complete vault structure.

    This function creates the main folders, README files for each folder,
    the main dashboard, and README files for the templates and prompts directories.
    """
    vault_path = r"F:\01_WRI\Obsidian\Vault"
    
    print("🎯 Starting to create the complete vault structure")
    print("=" * 60)
    
    # 1. Create README for main folders
    main_folders = [
        '00_DASHBOARD', '01_MANUSCRIPT', '02_CHARACTERS', 
        '03_WORLDBUILDING', '04_PLOT-TIMELINE', '05_SYSTEMS-LORE', '06_NOTE'
    ]
    
    print("\n📝 Creating READMEs for main folders...")
    for folder in main_folders:
        folder_path = os.path.join(vault_path, folder)
        readme_path = os.path.join(folder_path, "README.md")
        
        if not os.path.exists(readme_path):
            content = create_readme_content(folder, folder)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created README: {folder}")
    
    # 2. Create main dashboard
    print("\n📊 Creating main dashboard...")
    dashboard_path = os.path.join(vault_path, "00_DASHBOARD", "Dashboard.md")
    if not os.path.exists(dashboard_path):
        content = create_dashboard_content()
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Created main dashboard")
    
    # 3. Create README for 08_Templates-Tools
    print("\n🔧 Creating README for Templates & Tools...")
    templates_readme_path = os.path.join(vault_path, "08_Templates-Tools", "README.md")
    if not os.path.exists(templates_readme_path):
        content = create_templates_readme()
        with open(templates_readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Created README for Templates & Tools")
    
    # 4. Create README for subfolders of Prompts
    print("\n📝 Creating READMEs for Prompts...")
    prompts_path = os.path.join(vault_path, "08_Templates-Tools", "Prompts")
    
    prompt_types = {
        "General": "General prompts for AI",
        "Default_Prompts": "Prompts for Copilot and general use",
        "Smart_Connections": "Prompts for Smart Connections"
    }
    
    for prompt_type, description in prompt_types.items():
        prompt_folder_path = os.path.join(prompts_path, prompt_type)
        readme_path = os.path.join(prompt_folder_path, "README.md")
        
        if not os.path.exists(readme_path):
            date = datetime.now().strftime("%Y-%m-%d")
            content = f"""# 📝 {prompt_type}

## 🎯 Purpose
{description}

## 📁 Files in this folder
"""
            
            # Add a list of existing files
            if os.path.exists(prompt_folder_path):
                files = [f for f in os.listdir(prompt_folder_path) if f.endswith('.md') and f != 'README.md']
                for file in sorted(files):
                    content += f"- [[{file}|{file.replace('.md', '')}]]\n"
            
            content += f"\n---\n*Last updated: {date}*"
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created README: Prompts/{prompt_type}")
    
    print("\n🎉 Structure creation complete!")

if __name__ == "__main__":
    create_vault_structure()
