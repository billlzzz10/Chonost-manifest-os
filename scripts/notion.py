#!/usr/bin/env python3
"""
Enhanced Notion.py - Notion API integration for RAG pipeline with Dual-Identity support
Syncs Notion data to manuscript vault and generates structured data for chonost.manifest.json
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Third-party imports
try:
    from notion_client import Client
    import requests
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("📦 Install with: pip install notion-client requests googletrans==4.0.0rc1")
    sys.exit(1)

# Optional: Google Translate for dual-identity (fallback to manual mapping if not available)
try:
    from googletrans import Translator
    translator = Translator()
    TRANSLATION_AVAILABLE = True
except ImportError:
    print("⚠️  googletrans not available - using manual dual-identity mapping")
    TRANSLATION_AVAILABLE = False
    translator = None

class NotionSync:
    def __init__(self, token=None, vault_path="./manuscript-vault"):
        self.notion = Client(auth=token or os.getenv('NOTION_TOKEN'))
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        self.sync_log = []
        self.dual_identity_enabled = os.getenv('DUAL_IDENTITY_ENABLED', 'false').lower() == 'true'
        self.generate_dual_identity_flag = False
        
        print(f"📝 Enhanced Notion Sync initialized")
        print(f"📁 Vault path: {self.vault_path.absolute()}")
        print(f"🔄 Dual-identity enabled: {self.dual_identity_enabled}")
        print(f"🌐 Translation available: {TRANSLATION_AVAILABLE}")

    def sync_vault(self, generate_dual_identity: bool = False):
        """Sync Notion pages to manuscript vault with dual-identity support"""
        self.generate_dual_identity_flag = generate_dual_identity
        sync_data = []
        sync_count = 0
        
        try:
            # Get database ID from environment or argument
            database_id = os.getenv('NOTION_DATABASE_ID', 'your-database-id')
            
            if database_id == 'your-database-id':
                print("⚠️  Please set NOTION_DATABASE_ID environment variable")
                return {'status': 'error', 'message': 'Database ID not configured'}
            
            print("🔍 Fetching Notion data from database...")
            results = self.notion.databases.query(
                database_id=database_id,
                page_size=100  # Get up to 100 pages per request
            )
            
            # Handle pagination if needed
            while True:
                for page in results['results']:
                    sync_data.append(self.process_notion_page(page))
                    sync_count += 1
                    self.sync_log.append(f"Synced: {page_data['title']}")
                    print(f"✅ Synced page {sync_count}: {page_data['title']}")
                
                # Check for next page
                if not results.get('has_more') or not results.get('next_cursor'):
                    break
                
                print(f"🔄 Fetching next page... (cursor: {results.get('next_cursor')})")
                results = self.notion.databases.query(
                    database_id=database_id,
                    start_cursor=results['next_cursor'],
                    page_size=100
                )
            
            # Save individual files to vault
            for page_data in sync_data:
                vault_file = self.vault_path / f"notion_{page_data['id']}.json"
                with open(vault_file, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved: {vault_file}")
            
            # Generate structured output for manifest
            manifest_output = self.prepare_manifest_data(sync_data)
            
            # Save sync log
            log_file = self.vault_path / "sync_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'sync_count': sync_count,
                    'timestamp': datetime.now().isoformat(),
                    'log': self.sync_log,
                    'dual_identity_generated': generate_dual_identity,
                    'total_items': len(sync_data)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"🎉 Sync completed! {sync_count} items processed.")
            if generate_dual_identity:
                print(f"📋 Dual-identity data generated for {len(manifest_output['projects'] + manifest_output['files'] + manifest_output['diagrams'])} items")
                # Output structured JSON for sidecar.js to parse
                print("\n--- MANIFEST_DATA_START ---")
                print(json.dumps(manifest_output, ensure_ascii=False, indent=2))
                print("--- MANIFEST_DATA_END ---")
            
            return {
                'status': 'success',
                'count': sync_count,
                'manifest_data': manifest_output if generate_dual_identity else None
            }
            
        except Exception as e:
            error_msg = f"❌ Sync failed: {str(e)}"
            print(error_msg)
            self.sync_log.append(error_msg)
            return {'status': 'error', 'message': str(e), 'traceback': str(e)}

    def process_notion_page(self, page: Dict) -> Dict:
        """Process individual Notion page and extract comprehensive data"""
        properties = page['properties']
        
        # Extract title with fallback handling
        title = self.extract_page_title(properties)
        
        # Determine page type
        page_type = self.infer_page_type(properties, page.get('children', []))
        
        # Extract dual-identity if enabled
        dual_identity = {}
        if self.generate_dual_identity_flag and self.dual_identity_enabled:
            dual_identity = self.generate_dual_identity({
                'title': title,
                'type': page_type,
                'properties': properties,
                'content_preview': self.extract_content_preview(page.get('children', []))
            })
        
        page_data = {
            'id': page['id'].replace('-', ''),
            'title': title,
            'type': page_type,
            'created_time': page['created_time'],
            'last_edited_time': page['last_edited_time'],
            'url': page['url'],
            'parent_id': page['parent'].get('page_id') if isinstance(page['parent'], dict) else None,
            'icon': self.extract_icon(page),
            'properties': {k: self.simplify_property(v) for k, v in properties.items()},
            'dual_identity': dual_identity,
            'content_preview': self.extract_content_preview(page.get('children', [])),
            'tags': self.extract_tags(page),
            'timestamp': datetime.now().isoformat()
        }
        
        return page_data

    def extract_page_title(self, properties: Dict) -> str:
        """Extract page title with multiple fallback strategies"""
        # Common title property names
        title_properties = ['Name', 'Title', 'ชื่อ', 'ชื่อเรื่อง']
        
        for prop_name in title_properties:
            if prop_name in properties:
                prop = properties[prop_name]
                if 'title' in prop and prop['title']:
                    return prop['title'][0]['text']['content']
                elif 'rich_text' in prop and prop['rich_text']:
                    return prop['rich_text'][0]['plain_text']
        
        # Fallback to first rich_text property
        for prop_name, prop in properties.items():
            if 'rich_text' in prop and prop['rich_text']:
                return prop['rich_text'][0]['plain_text']
        
        return 'Untitled Page'

    def infer_page_type(self, properties: Dict, children: List = None) -> str:
        """Infer page type based on properties and content"""
        prop_names = [k.lower() for k in properties.keys()]
        
        # Project indicators
        project_keywords = ['project', 'โปรเจกต์', 'task', 'งาน', 'milestone', 'เป้าหมาย']
        if any(keyword in ' '.join(prop_names) for keyword in project_keywords):
            return 'project'
        
        # Diagram indicators
        diagram_keywords = ['diagram', 'แผนภาพ', 'chart', 'กราฟ', 'flow', 'visual']
        content_has_diagram = (
            children and any(
                any(keyword in block.get('rich_text', [{}])[0].get('plain_text', '').lower()
                for keyword in diagram_keywords
                if block.get('rich_text'))
                for block in children[:10]  # Check first 10 blocks
            )
        )
        
        if any(keyword in ' '.join(prop_names) for keyword in diagram_keywords) or content_has_diagram:
            return 'diagram'
        
        return 'file'

    def generate_dual_identity(self, page_data: Dict) -> Dict:
        """Generate Thai/English dual-identity for page"""
        title = page_data['title']
        page_type = page_data['type']
        content_preview = page_data.get('content_preview', '')
        
        # Base dual identity structure
        dual_identity = {
            'thai_name': '',
            'english_name': title,
            'type': page_type,
            'confidence': 0.8,  # Default confidence
            'translation_method': 'manual'
        }
        
        if not TRANSLATION_AVAILABLE:
            # Manual mapping for common terms
            dual_identity['thai_name'] = self.manual_translate(title, page_type)
            dual_identity['translation_method'] = 'manual_mapping'
            return dual_identity
        
        try:
            # Use Google Translate for Thai to English (or vice versa)
            # Detect if title is already in Thai (contains Thai characters)
            thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
            is_thai = bool(thai_pattern.search(title))
            
            if is_thai:
                # Translate Thai to English
                result = translator.translate(title, src='th', dest='en')
                dual_identity['english_name'] = result.text
                dual_identity['thai_name'] = title
                dual_identity['translation_method'] = 'google_translate_th_en'
            else:
                # Translate English to Thai
                result = translator.translate(title, src='en', dest='th')
                dual_identity['thai_name'] = result.text
                dual_identity['english_name'] = title
                dual_identity['translation_method'] = 'google_translate_en_th'
            
            # Enhance with type-specific terms
            dual_identity['thai_name'] = self.enhance_type_translation(
                dual_identity['thai_name'], page_type
            )
            
            # Extract additional context from content
            if content_preview:
                dual_identity['context_keywords'] = self.extract_context_keywords(
                    content_preview, max_keywords=5
                )
            
            dual_identity['confidence'] = min(1.0, dual_identity['confidence'] + 0.1)
            
        except Exception as translate_error:
            print(f"⚠️  Translation failed for '{title}': {translate_error}")
            # Fallback to manual translation
            dual_identity['thai_name'] = self.manual_translate(title, page_type)
            dual_identity['translation_method'] = 'fallback_manual'
            dual_identity['confidence'] = 0.5
        
        return dual_identity

    def manual_translate(self, text: str, page_type: str) -> str:
        """Manual translation mapping for common terms"""
        # Type-specific prefixes
        type_prefixes = {
            'project': 'โปรเจกต์ ',
            'diagram': 'แผนภาพ ',
            'file': 'เอกสาร ',
            'report': 'รายงาน ',
            'notes': 'บันทึก '
        }
        
        prefix = type_prefixes.get(page_type, 'เอกสาร ')
        
        # Common word mappings
        word_map = {
            'project': 'โปรเจกต์',
            'report': 'รายงาน',
            'document': 'เอกสาร',
            'analysis': 'การวิเคราะห์',
            'draft': 'ร่าง',
            'final': 'ฉบับสมบูรณ์',
            'notes': 'บันทึก',
            'diagram': 'แผนภาพ',
            'chart': 'แผนภูมิ',
            'flow': 'กระแส',
            'task': 'งาน',
            'goal': 'เป้าหมาย',
            'plan': 'แผน',
            'summary': 'สรุป'
        }
        
        thai_text = prefix + text
        
        for english, thai in word_map.items():
            thai_text = re.sub(rf'\b{re.escape(english)}\b', thai, thai_text, flags=re.IGNORECASE)
        
        return thai_text.strip()

    def enhance_type_translation(self, thai_name: str, page_type: str) -> str:
        """Enhance translation based on page type"""
        type_enhancements = {
            'project': ['โปรเจกต์', 'โครงการ'],
            'diagram': ['แผนภาพ', 'ไดอะแกรม', 'ชาร์ต'],
            'report': ['รายงาน', 'สรุปผล'],
            'notes': ['บันทึก', 'โน้ต']
        }
        
        if page_type in type_enhancements:
            for enhancement in type_enhancements[page_type]:
                if enhancement not in thai_name:
                    # Add type indicator if not present
                    thai_name = f"{enhancement}: {thai_name}"
                    break
        
        return thai_name

    def extract_content_preview(self, blocks: List) -> str:
        """Extract text preview from first few blocks (max 500 chars)"""
        preview = []
        max_chars = 500
        
        for block in blocks[:10]:  # First 10 blocks
            if len(''.join(preview)) >= max_chars:
                break
            
            block_type = block.get('type', 'paragraph')
            if block_type == 'paragraph' and block['paragraph'].get('rich_text'):
                text = block['paragraph']['rich_text'][0].get('plain_text', '')
                preview.append(text)
            elif block_type == 'heading_1' and block['heading_1'].get('rich_text'):
                text = block['heading_1']['rich_text'][0].get('plain_text', '')
                preview.append(f"## {text}")
            elif block_type == 'heading_2' and block['heading_2'].get('rich_text'):
                text = block['heading_2']['rich_text'][0].get('plain_text', '')
                preview.append(f"### {text}")
            elif block_type == 'code' and block['code'].get('rich_text'):
                text = block['code']['rich_text'][0].get('plain_text', '')
                preview.append(f"```code\n{text[:100]}...\n```")
        
        return ' '.join(preview)[:max_chars]

    def extract_tags(self, page: Dict) -> List[str]:
        """Extract tags/keywords from page content and properties"""
        tags = set()
        
        # Extract from properties
        for prop_name, prop_value in page['properties'].items():
            if 'select' in prop_value and prop_value['select']:
                tags.add(prop_value['select']['name'])
            elif 'multi_select' in prop_value and prop_value['multi_select']:
                for select in prop_value['multi_select']:
                    tags.add(select['name'])
            elif 'rich_text' in prop_value and prop_value['rich_text']:
                text = prop_value['rich_text'][0]['plain_text'].lower()
                # Extract hashtags
                hashtags = re.findall(r'#\w+', text)
                tags.update(hashtags)
        
        # Extract from content preview
        if 'content_preview' in page:
            content = page['content_preview'].lower()
            # Common keywords for auto-tagging
            keyword_patterns = [
                r'\bproject\b', r'\bโปรเจกต์\b',  # Project
                r'\breport\b', r'\bรายงาน\b',     # Report
                r'\banalysis\b', r'\bวิเคราะห์\b', # Analysis
                r'\bdiagram\b', r'\bแผนภาพ\b',    # Diagram
                r'\bgoal\b', r'\bเป้าหมาย\b',    # Goal
                r'\btask\b', r'\bงาน\b'           # Task
            ]
            
            for pattern in keyword_patterns:
                if re.search(pattern, content):
                    tag = re.sub(r'\b\w+\b', lambda m: m.group().title(), pattern)
                    tags.add(tag.lower())
        
        # Type-based tags
        if page.get('type'):
            tags.add(page['type'])
        
        return sorted(list(tags))

    def extract_context_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """Extract contextual keywords from content (simple TF-IDF like approach)"""
        # Remove common stop words (Thai + English)
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'เป็น', 'ที่', 'ของ', 'ใน', 'และ', 'หรือ', 'แต่', 'เพื่อ', 'จาก'
        }
        
        # Extract words
        words = re.findall(r'\b\w{3,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords by frequency
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, freq in sorted_keywords[:max_keywords]]

    def extract_icon(self, page: Dict) -> Optional[str]:
        """Extract page icon (emoji or external URL)"""
        icon = page.get('icon')
        if not icon:
            return None
        
        if icon.get('type') == 'emoji':
            return icon['emoji']
        elif icon.get('type') == 'external':
            return icon['external']['url']
        elif icon.get('type') == 'file':
            return icon['file']['url']
        
        return None

    def simplify_property(self, property_value: Dict) -> Any:
        """Simplify Notion property for JSON serialization"""
        if 'title' in property_value and property_value['title']:
            return [t['text']['content'] for t in property_value['title']]
        elif 'rich_text' in property_value and property_value['rich_text']:
            return [rt['plain_text'] for rt in property_value['rich_text']]
        elif 'select' in property_value:
            return property_value['select']['name'] if property_value['select'] else None
        elif 'multi_select' in property_value and property_value['multi_select']:
            return [s['name'] for s in property_value['multi_select']]
        elif 'number' in property_value:
            return property_value['number']
        elif 'date' in property_value and property_value['date']:
            return property_value['date']['start']
        elif 'checkbox' in property_value:
            return property_value['checkbox']
        else:
            return str(property_value)

    def prepare_manifest_data(self, sync_data: List[Dict]) -> Dict:
        """Prepare structured data for chonost.manifest.json"""
        projects = []
        files = []
        diagrams = []
        
        for item in sync_data:
            if item['dual_identity']:
                entry = {
                    'id': item['id'],
                    'thai_name': item['dual_identity']['thai_name'],
                    'english_name': item['dual_identity']['english_name'],
                    'type': item['type'],
                    'local_path': f"{self.vault_path}/notion_{item['id']}.json",
                    'cloud_id': item['id'],
                    'tags': item['tags'],
                    'created': item['created_time'],
                    'updated': item['last_edited_time'],
                    'url': item['url'],
                    'confidence': item['dual_identity']['confidence'],
                    'translation_method': item['dual_identity']['translation_method'],
                    'context_keywords': item['dual_identity'].get('context_keywords', [])
                }
                
                if item['type'] == 'project':
                    projects.append(entry)
                elif item['type'] == 'diagram':
                    diagrams.append(entry)
                else:
                    files.append(entry)
        
        manifest_data = {
            'projects': projects,
            'files': files,
            'diagrams': diagrams,
            'metadata': {
                'version': '1.0.0',
                'last_sync': datetime.now().isoformat(),
                'total_items': len(sync_data),
                'projects_count': len(projects),
                'files_count': len(files),
                'diagrams_count': len(diagrams),
                'dual_identity_enabled': self.dual_identity_enabled,
                'translation_available': TRANSLATION_AVAILABLE,
                'sync_source': 'notion_database'
            }
        }
        
        return manifest_data

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Notion API integration for RAG pipeline with Dual-Identity support'
    )
    parser.add_argument('--sync-vault', action='store_true',
                       help='Sync Notion data to manuscript vault')
    parser.add_argument('--generate-dual-identity', action='store_true',
                       help='Generate dual-identity data for chonost.manifest.json')
    parser.add_argument('--token', help='Notion API token (overrides env var)')
    parser.add_argument('--vault', default='./manuscript-vault',
                       help='Manuscript vault path')
    parser.add_argument('--database-id', help='Notion database ID (overrides env var)')
    
    args = parser.parse_args()
    
    # Set environment variables from arguments
    if args.token:
        os.environ['NOTION_TOKEN'] = args.token
    
    if args.database_id:
        os.environ['NOTION_DATABASE_ID'] = args.database_id
    
    # Enable dual-identity based on flag or environment
    if args.generate_dual_identity:
        os.environ['DUAL_IDENTITY_ENABLED'] = 'true'
    
    print("🚀 Starting Enhanced Notion sync...")
    print(f"📋 Arguments: {vars(args)}")
    print(f"🔧 Environment: DUAL_IDENTITY_ENABLED={os.getenv('DUAL_IDENTITY_ENABLED', 'false')}")
    
    sync = NotionSync(
        token=os.getenv('NOTION_TOKEN'),
        vault_path=args.vault
    )
    
    if args.sync_vault:
        # Enable dual-identity if flag is set
        generate_dual = bool(args.generate_dual_identity)
        result = sync.sync_vault(generate_dual_identity=generate_dual)
        
        print(f"\n📊 Final Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Exit with appropriate code
        if result['status'] == 'success':
            sys.exit(0)
        else:
            print(f"❌ Error details: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    else:
        print("ℹ️  No action specified.")
        print("Usage: --sync-vault [--generate-dual-identity] [--token <token>] [--vault <path>]")
        sys.exit(0)

if __name__ == '__main__':
    main()