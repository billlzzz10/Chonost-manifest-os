"""
🚀 Enhanced RAG System - High Performance & Deep Document Scanning
ระบบ RAG ที่ปรับปรุงประสิทธิภาพและรองรับการสแกนเอกสารระดับลึก

Features:
- Parallel Document Processing
- Intelligent File Type Detection
- Advanced Caching Strategy
- Performance Monitoring
- Deep Code Analysis
- Document Content Extraction
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import sqlite3
import redis
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing
import mimetypes
import magic
import re
import os

# Document Processing Imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

# Code Analysis Imports
try:
    import ast
    import tokenize
    AST_AVAILABLE = True
except ImportError:
    AST_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """เก็บข้อมูลประสิทธิภาพการทำงาน"""
    start_time: float
    end_time: float
    files_processed: int
    documents_extracted: int
    embeddings_generated: int
    cache_hits: int
    cache_misses: int
    errors: List[str]
    
    @property
    def total_time(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def files_per_second(self) -> float:
        return self.files_processed / self.total_time if self.total_time > 0 else 0
    
    @property
    def documents_per_second(self) -> float:
        return self.documents_extracted / self.total_time if self.total_time > 0 else 0

@dataclass
class DocumentContent:
    """เนื้อหาของเอกสารที่สกัดได้"""
    file_path: str
    content_type: str  # 'text', 'code', 'document', 'image', 'binary'
    content: str
    metadata: Dict[str, Any]
    extracted_at: datetime
    file_size: int
    processing_time: float

class IntelligentFileProcessor:
    """ระบบประมวลผลไฟล์อัจฉริยะ"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.supported_extensions = {
            # Text & Code Files
            '.txt': 'text', '.md': 'text', '.rst': 'text', '.log': 'text',
            '.py': 'code', '.js': 'code', '.ts': 'code', '.jsx': 'code', '.tsx': 'code',
            '.java': 'code', '.cpp': 'code', '.c': 'code', '.h': 'code', '.hpp': 'code',
            '.cs': 'code', '.php': 'code', '.rb': 'code', '.go': 'code', '.rs': 'code',
            '.swift': 'code', '.kt': 'code', '.scala': 'code', '.dart': 'code',
            '.html': 'code', '.css': 'code', '.scss': 'code', '.sass': 'code',
            '.xml': 'code', '.json': 'code', '.yaml': 'code', '.yml': 'code',
            '.toml': 'code', '.ini': 'code', '.cfg': 'code', '.conf': 'code',
            '.sh': 'code', '.bat': 'code', '.ps1': 'code', '.sql': 'code',
            
            # Document Files
            '.pdf': 'document', '.docx': 'document', '.doc': 'document',
            '.xlsx': 'document', '.xls': 'document', '.pptx': 'document',
            '.ppt': 'document', '.odt': 'document', '.ods': 'document',
            
            # Data Files
            '.csv': 'data', '.tsv': 'data', '.xml': 'data', '.json': 'data',
            
            # Configuration Files
            '.env': 'config', '.gitignore': 'config', '.dockerfile': 'config',
            '.dockerignore': 'config', 'docker-compose.yml': 'config',
            'package.json': 'config', 'requirements.txt': 'config',
            'pom.xml': 'config', 'build.gradle': 'config', 'Cargo.toml': 'config',
            'go.mod': 'config', 'composer.json': 'config', 'Gemfile': 'config'
        }
        
        # File size limits (in bytes)
        self.size_limits = {
            'text': 10 * 1024 * 1024,  # 10MB
            'code': 5 * 1024 * 1024,   # 5MB
            'document': 50 * 1024 * 1024,  # 50MB
            'data': 100 * 1024 * 1024,  # 100MB
            'config': 1 * 1024 * 1024   # 1MB
        }
        
        # Performance settings
        self.max_workers = self.config.get('max_workers', min(32, (os.cpu_count() or 1) + 4))
        self.chunk_size = self.config.get('chunk_size', 1000)
        self.chunk_overlap = self.config.get('chunk_overlap', 200)
        
        logger.info(f"🚀 Intelligent File Processor พร้อมใช้งาน (Workers: {self.max_workers})")
    
    async def process_directory_deep(self, root_path: str, 
                                   include_patterns: List[str] = None,
                                   exclude_patterns: List[str] = None) -> List[DocumentContent]:
        """ประมวลผลโฟลเดอร์แบบลึก"""
        start_time = time.time()
        
        try:
            # สร้าง patterns สำหรับการกรอง
            include_patterns = include_patterns or ['*']
            exclude_patterns = exclude_patterns or [
                '*.exe', '*.dll', '*.so', '*.dylib', '*.bin',
                '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
                '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wmv',
                '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp',
                '*.iso', '*.img', '*.vmdk', '*.vhd'
            ]
            
            # หาไฟล์ทั้งหมด
            all_files = self._find_files_recursive(root_path, include_patterns, exclude_patterns)
            logger.info(f"🔍 พบไฟล์ {len(all_files)} ไฟล์ใน {root_path}")
            
            # ประมวลผลแบบ parallel
            documents = await self._process_files_parallel(all_files)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"✅ ประมวลผลเสร็จสิ้น: {len(documents)} เอกสาร ใน {processing_time:.2f} วินาที")
            logger.info(f"📊 อัตราเร็ว: {len(documents)/processing_time:.2f} เอกสาร/วินาที")
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลโฟลเดอร์: {e}")
            return []
    
    def _find_files_recursive(self, root_path: str, include_patterns: List[str], 
                            exclude_patterns: List[str]) -> List[str]:
        """หาไฟล์แบบ recursive พร้อม pattern matching"""
        files = []
        root_path = Path(root_path)
        
        try:
            for pattern in include_patterns:
                for file_path in root_path.rglob(pattern):
                    if file_path.is_file():
                        # ตรวจสอบ exclude patterns
                        should_exclude = False
                        for exclude_pattern in exclude_patterns:
                            if file_path.match(exclude_pattern):
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            files.append(str(file_path))
            
            # ลบไฟล์ที่ซ้ำ
            files = list(set(files))
            return files
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการหาไฟล์: {e}")
            return []
    
    async def _process_files_parallel(self, file_paths: List[str]) -> List[DocumentContent]:
        """ประมวลผลไฟล์แบบ parallel"""
        documents = []
        
        # แบ่งไฟล์เป็น batches
        batch_size = max(1, len(file_paths) // self.max_workers)
        batches = [file_paths[i:i + batch_size] for i in range(0, len(file_paths), batch_size)]
        
        # ประมวลผลแบบ parallel
        tasks = []
        for batch in batches:
            task = asyncio.create_task(self._process_file_batch(batch))
            tasks.append(task)
        
        # รอผลลัพธ์ทั้งหมด
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # รวมผลลัพธ์
        for batch_result in batch_results:
            if isinstance(batch_result, list):
                documents.extend(batch_result)
            else:
                logger.error(f"❌ Batch processing error: {batch_result}")
        
        return documents
    
    async def _process_file_batch(self, file_paths: List[str]) -> List[DocumentContent]:
        """ประมวลผล batch ของไฟล์"""
        documents = []
        
        for file_path in file_paths:
            try:
                doc = await self._process_single_file(file_path)
                if doc:
                    documents.append(doc)
            except Exception as e:
                logger.warning(f"⚠️ ไม่สามารถประมวลผลไฟล์ {file_path}: {e}")
                continue
        
        return documents
    
    async def _process_single_file(self, file_path: str) -> Optional[DocumentContent]:
        """ประมวลผลไฟล์เดียว"""
        start_time = time.time()
        
        try:
            file_path = Path(file_path)
            
            # ตรวจสอบว่าไฟล์มีอยู่จริง
            if not file_path.exists():
                return None
            
            # ตรวจสอบขนาดไฟล์
            file_size = file_path.stat().st_size
            if file_size == 0:
                return None
            
            # กำหนดประเภทไฟล์
            content_type = self._determine_content_type(file_path)
            if not content_type:
                return None
            
            # ตรวจสอบขนาดไฟล์ตามประเภท
            size_limit = self.size_limits.get(content_type, 1 * 1024 * 1024)
            if file_size > size_limit:
                logger.info(f"⚠️ ข้ามไฟล์ {file_path} (ขนาดใหญ่เกินไป: {file_size} bytes)")
                return None
            
            # สกัดเนื้อหา
            content = await self._extract_content(file_path, content_type)
            if not content:
                return None
            
            # สร้าง metadata
            metadata = self._create_metadata(file_path, content_type, file_size)
            
            processing_time = time.time() - start_time
            
            return DocumentContent(
                file_path=str(file_path),
                content_type=content_type,
                content=content,
                metadata=metadata,
                extracted_at=datetime.now(),
                file_size=file_size,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลไฟล์ {file_path}: {e}")
            return None
    
    def _determine_content_type(self, file_path: Path) -> Optional[str]:
        """กำหนดประเภทเนื้อหาของไฟล์"""
        file_name = file_path.name.lower()
        
        # ตรวจสอบจาก extension
        for ext, content_type in self.supported_extensions.items():
            if file_name.endswith(ext):
                return content_type
        
        # ตรวจสอบจากชื่อไฟล์
        for pattern, content_type in self.supported_extensions.items():
            if pattern in file_name:
                return content_type
        
        # ใช้ magic number สำหรับไฟล์ที่ไม่รู้จัก
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                if mime_type.startswith('text/'):
                    return 'text'
                elif mime_type.startswith('application/'):
                    return 'document'
        except:
            pass
        
        return None
    
    async def _extract_content(self, file_path: Path, content_type: str) -> Optional[str]:
        """สกัดเนื้อหาจากไฟล์"""
        try:
            if content_type == 'text':
                return await self._extract_text_content(file_path)
            elif content_type == 'code':
                return await self._extract_code_content(file_path)
            elif content_type == 'document':
                return await self._extract_document_content(file_path)
            elif content_type == 'data':
                return await self._extract_data_content(file_path)
            elif content_type == 'config':
                return await self._extract_config_content(file_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสกัดเนื้อหา {file_path}: {e}")
            return None
    
    async def _extract_text_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาข้อความ"""
        try:
            # ลองอ่านเป็น UTF-8 ก่อน
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except UnicodeDecodeError:
                # ลอง encoding อื่นๆ
                encodings = ['latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        return content
                    except UnicodeDecodeError:
                        continue
                
                # ถ้าไม่ได้เลย ให้อ่านเป็น binary และ decode แบบ ignore
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                return content
                
        except Exception as e:
            logger.error(f"❌ ไม่สามารถอ่านไฟล์ข้อความ {file_path}: {e}")
            return None
    
    async def _extract_code_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาโค้ด"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # เพิ่ม metadata สำหรับโค้ด
            code_metadata = self._analyze_code_structure(content, file_path.suffix)
            
            # รวม metadata เข้ากับเนื้อหา
            enhanced_content = f"// File: {file_path.name}\n"
            enhanced_content += f"// Language: {code_metadata.get('language', 'unknown')}\n"
            enhanced_content += f"// Functions: {len(code_metadata.get('functions', []))}\n"
            enhanced_content += f"// Classes: {len(code_metadata.get('classes', []))}\n"
            enhanced_content += "// Content:\n"
            enhanced_content += content
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหาโค้ด {file_path}: {e}")
            return None
    
    def _analyze_code_structure(self, content: str, file_extension: str) -> Dict[str, Any]:
        """วิเคราะห์โครงสร้างโค้ด"""
        metadata = {
            'language': self._get_language_from_extension(file_extension),
            'functions': [],
            'classes': [],
            'imports': [],
            'comments': []
        }
        
        try:
            if file_extension == '.py' and AST_AVAILABLE:
                # วิเคราะห์ Python code
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            metadata['functions'].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            metadata['classes'].append(node.name)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                metadata['imports'].append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                metadata['imports'].append(node.module)
                except:
                    pass
            
            # หา comments
            comment_patterns = {
                '.py': [r'#.*$', r'""".*?"""', r"'''.*?'''"],
                '.js': [r'//.*$', r'/\*.*?\*/'],
                '.ts': [r'//.*$', r'/\*.*?\*/'],
                '.java': [r'//.*$', r'/\*.*?\*/'],
                '.cpp': [r'//.*$', r'/\*.*?\*/'],
                '.c': [r'//.*$', r'/\*.*?\*/'],
                '.html': [r'<!--.*?-->'],
                '.css': [r'/\*.*?\*/'],
                '.sql': [r'--.*$', r'/\*.*?\*/']
            }
            
            patterns = comment_patterns.get(file_extension, [])
            for pattern in patterns:
                comments = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                metadata['comments'].extend(comments)
            
        except Exception as e:
            logger.warning(f"⚠️ ไม่สามารถวิเคราะห์โครงสร้างโค้ดได้: {e}")
        
        return metadata
    
    def _get_language_from_extension(self, extension: str) -> str:
        """แปลง extension เป็นชื่อภาษา"""
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.jsx': 'React JSX', '.tsx': 'React TSX', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.h': 'C Header', '.hpp': 'C++ Header',
            '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go',
            '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin',
            '.scala': 'Scala', '.dart': 'Dart', '.html': 'HTML',
            '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
            '.xml': 'XML', '.json': 'JSON', '.yaml': 'YAML',
            '.yml': 'YAML', '.toml': 'TOML', '.ini': 'INI',
            '.cfg': 'Config', '.conf': 'Config', '.sh': 'Shell',
            '.bat': 'Batch', '.ps1': 'PowerShell', '.sql': 'SQL'
        }
        return language_map.get(extension, 'Unknown')
    
    def _create_metadata(self, file_path: Path, content_type: str, file_size: int) -> Dict[str, Any]:
        """สร้าง metadata สำหรับไฟล์"""
        try:
            stat = file_path.stat()
            
            return {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'content_type': content_type,
                'file_size': file_size,
                'file_extension': file_path.suffix.lower(),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_hidden': file_path.name.startswith('.'),
                'parent_directory': str(file_path.parent),
                'depth_level': len(file_path.parts) - 1
            }
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสร้าง metadata สำหรับ {file_path}: {e}")
            return {}
    
    async def _extract_document_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจากเอกสาร"""
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.pdf' and PDF_AVAILABLE:
                return await self._extract_pdf_content(file_path)
            elif extension == '.docx' and DOCX_AVAILABLE:
                return await self._extract_docx_content(file_path)
            elif extension in ['.xlsx', '.xls'] and EXCEL_AVAILABLE:
                return await self._extract_excel_content(file_path)
            elif extension in ['.html', '.htm'] and HTML_AVAILABLE:
                return await self._extract_html_content(file_path)
            else:
                # Fallback to text extraction
                return await self._extract_text_content(file_path)
                
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหาเอกสาร {file_path}: {e}")
            return None
    
    async def _extract_pdf_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก PDF"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                content = await loop.run_in_executor(executor, self._extract_pdf_sync, file_path)
            return content
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา PDF {file_path}: {e}")
            return None
    
    def _extract_pdf_sync(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก PDF (sync version)"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
                return content
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {e}")
            return None
    
    async def _extract_docx_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก DOCX"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                content = await loop.run_in_executor(executor, self._extract_docx_sync, file_path)
            return content
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา DOCX {file_path}: {e}")
            return None
    
    def _extract_docx_sync(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก DOCX (sync version)"""
        try:
            doc = docx.Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        except Exception as e:
            logger.error(f"❌ DOCX extraction error: {e}")
            return None
    
    async def _extract_excel_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก Excel"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                content = await loop.run_in_executor(executor, self._extract_excel_sync, file_path)
            return content
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา Excel {file_path}: {e}")
            return None
    
    def _extract_excel_sync(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก Excel (sync version)"""
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            content = ""
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                content += f"Sheet: {sheet_name}\n"
                for row in sheet.iter_rows(values_only=True):
                    row_content = [str(cell) if cell is not None else "" for cell in row]
                    content += "\t".join(row_content) + "\n"
                content += "\n"
            return content
        except Exception as e:
            logger.error(f"❌ Excel extraction error: {e}")
            return None
    
    async def _extract_html_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก HTML"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # ใช้ BeautifulSoup เพื่อสกัดข้อความ
            soup = BeautifulSoup(content, 'html.parser')
            
            # ลบ script และ style tags
            for script in soup(["script", "style"]):
                script.decompose()
            
            # สกัดข้อความ
            text = soup.get_text()
            
            # ทำความสะอาดข้อความ
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา HTML {file_path}: {e}")
            return None
    
    async def _extract_data_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจากไฟล์ข้อมูล"""
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.csv':
                return await self._extract_csv_content(file_path)
            elif extension == '.json':
                return await self._extract_json_content(file_path)
            elif extension == '.xml':
                return await self._extract_xml_content(file_path)
            else:
                return await self._extract_text_content(file_path)
                
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหาข้อมูล {file_path}: {e}")
            return None
    
    async def _extract_csv_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก CSV"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # เพิ่ม metadata
            lines = content.split('\n')
            if lines:
                headers = lines[0].split(',')
                content = f"CSV File: {file_path.name}\n"
                content += f"Columns: {len(headers)}\n"
                content += f"Headers: {', '.join(headers)}\n"
                content += f"Rows: {len(lines) - 1}\n"
                content += "Content:\n" + '\n'.join(lines[:100])  # จำกัด 100 แถวแรก
            
            return content
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา CSV {file_path}: {e}")
            return None
    
    async def _extract_json_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก JSON"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # Parse JSON เพื่อเพิ่ม metadata
            try:
                data = json.loads(content)
                content = f"JSON File: {file_path.name}\n"
                content += f"Type: {type(data).__name__}\n"
                if isinstance(data, dict):
                    content += f"Keys: {', '.join(data.keys())}\n"
                elif isinstance(data, list):
                    content += f"Items: {len(data)}\n"
                content += "Content:\n" + content
            
            except json.JSONDecodeError:
                # ถ้า parse ไม่ได้ ให้ใช้เนื้อหาเดิม
                pass
            
            return content
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา JSON {file_path}: {e}")
            return None
    
    async def _extract_xml_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจาก XML"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # ใช้ BeautifulSoup เพื่อ parse XML
            soup = BeautifulSoup(content, 'xml')
            
            # สกัดข้อมูลสำคัญ
            content = f"XML File: {file_path.name}\n"
            content += f"Root Element: {soup.find().name if soup.find() else 'None'}\n"
            content += "Content:\n" + soup.get_text()
            
            return content
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา XML {file_path}: {e}")
            return None
    
    async def _extract_config_content(self, file_path: Path) -> Optional[str]:
        """สกัดเนื้อหาจากไฟล์ config"""
        try:
            content = await self._extract_text_content(file_path)
            if not content:
                return None
            
            # เพิ่ม metadata สำหรับ config files
            content = f"Config File: {file_path.name}\n"
            content += f"Type: Configuration\n"
            content += "Content:\n" + content
            
            return content
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถสกัดเนื้อหา config {file_path}: {e}")
            return None

class EnhancedRAGSystem:
    """Enhanced RAG System ที่มีประสิทธิภาพสูง"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.file_processor = IntelligentFileProcessor(config.get('file_processor', {}))
        
        # Performance monitoring
        self.metrics = PerformanceMetrics(
            start_time=0,
            end_time=0,
            files_processed=0,
            documents_extracted=0,
            embeddings_generated=0,
            cache_hits=0,
            cache_misses=0,
            errors=[]
        )
        
        # Cache system
        self.cache = redis.Redis(
            host=self.config.get("redis_host", "localhost"),
            port=self.config.get("redis_port", 6379),
            db=self.config.get("redis_db", 1),  # ใช้ DB 1 สำหรับ enhanced system
            decode_responses=True
        )
        
        logger.info("🚀 Enhanced RAG System พร้อมใช้งาน")
    
    async def scan_directory_deep(self, root_path: str, 
                                include_patterns: List[str] = None,
                                exclude_patterns: List[str] = None,
                                max_depth: int = 10) -> Dict[str, Any]:
        """สแกนโฟลเดอร์แบบลึก"""
        start_time = time.time()
        self.metrics.start_time = start_time
        
        try:
            logger.info(f"🔍 เริ่มสแกนโฟลเดอร์แบบลึก: {root_path}")
            
            # ประมวลผลไฟล์
            documents = await self.file_processor.process_directory_deep(
                root_path, include_patterns, exclude_patterns
            )
            
            # อัพเดท metrics
            self.metrics.files_processed = len(documents)
            self.metrics.documents_extracted = len(documents)
            
            # Cache documents
            await self._cache_documents(documents)
            
            # สร้าง embeddings (ถ้าต้องการ)
            if self.config.get('generate_embeddings', True):
                await self._generate_embeddings_batch(documents)
            
            end_time = time.time()
            self.metrics.end_time = end_time
            
            # สร้างรายงาน
            report = self._create_scan_report(documents)
            
            logger.info(f"✅ สแกนเสร็จสิ้น: {len(documents)} เอกสาร ใน {end_time - start_time:.2f} วินาที")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสแกน: {e}")
            self.metrics.errors.append(str(e))
            return {'error': str(e)}
    
    async def _cache_documents(self, documents: List[DocumentContent]):
        """Cache เอกสาร"""
        try:
            for doc in documents:
                cache_key = f"doc:{hashlib.md5(doc.file_path.encode()).hexdigest()}"
                cache_data = {
                    'file_path': doc.file_path,
                    'content_type': doc.content_type,
                    'content': doc.content[:10000],  # จำกัดขนาด
                    'metadata': doc.metadata,
                    'extracted_at': doc.extracted_at.isoformat(),
                    'file_size': doc.file_size,
                    'processing_time': doc.processing_time
                }
                
                # Cache 1 ชั่วโมง
                self.cache.setex(cache_key, 3600, json.dumps(cache_data))
            
            logger.info(f"✅ Cache เอกสาร {len(documents)} ไฟล์")
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการ cache: {e}")
    
    async def _generate_embeddings_batch(self, documents: List[DocumentContent]):
        """สร้าง embeddings แบบ batch"""
        try:
            # ใช้ RAG system เดิม
            from .rag_system import RAGSystem
            
            rag = RAGSystem(self.config)
            
            for doc in documents:
                if doc.content:
                    success = await rag.add_document(
                        content=doc.content,
                        metadata=doc.metadata,
                        source=doc.file_path
                    )
                    if success:
                        self.metrics.embeddings_generated += 1
            
            logger.info(f"✅ สร้าง embeddings {self.metrics.embeddings_generated} เอกสาร")
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้าง embeddings: {e}")
    
    def _create_scan_report(self, documents: List[DocumentContent]) -> Dict[str, Any]:
        """สร้างรายงานการสแกน"""
        try:
            # จัดกลุ่มตามประเภทเนื้อหา
            content_types = {}
            file_extensions = {}
            total_size = 0
            
            for doc in documents:
                # Content types
                content_type = doc.content_type
                if content_type not in content_types:
                    content_types[content_type] = 0
                content_types[content_type] += 1
                
                # File extensions
                ext = doc.metadata.get('file_extension', 'unknown')
                if ext not in file_extensions:
                    file_extensions[ext] = 0
                file_extensions[ext] += 1
                
                # Total size
                total_size += doc.file_size
            
            # Performance metrics
            performance = {
                'total_time': self.metrics.total_time,
                'files_per_second': self.metrics.files_per_second,
                'documents_per_second': self.metrics.documents_per_second,
                'embeddings_generated': self.metrics.embeddings_generated,
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses
            }
            
            return {
                'summary': {
                    'total_documents': len(documents),
                    'total_size_bytes': total_size,
                    'total_size_mb': total_size / (1024 * 1024),
                    'content_types': content_types,
                    'file_extensions': dict(sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:20]),
                    'performance': performance
                },
                'documents': [
                    {
                        'file_path': doc.file_path,
                        'content_type': doc.content_type,
                        'file_size': doc.file_size,
                        'processing_time': doc.processing_time,
                        'metadata': doc.metadata
                    }
                    for doc in documents[:100]  # จำกัด 100 เอกสารแรก
                ],
                'errors': self.metrics.errors
            }
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้างรายงาน: {e}")
            return {'error': str(e)}
    
    async def search_documents(self, query: str, content_types: List[str] = None, 
                             top_k: int = 10) -> List[Dict[str, Any]]:
        """ค้นหาเอกสาร"""
        try:
            # ตรวจสอบ cache
            cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                self.metrics.cache_hits += 1
                logger.info("✅ ใช้ผลลัพธ์จาก cache")
                return json.loads(cached_result)
            
            self.metrics.cache_misses += 1
            
            # ค้นหาใน RAG system
            from .rag_system import RAGSystem
            rag = RAGSystem(self.config)
            
            results = await rag.search(query, top_k)
            
            # แปลงผลลัพธ์
            search_results = []
            for result in results:
                search_results.append({
                    'file_path': result.document.source,
                    'content': result.document.content[:500],  # จำกัดขนาด
                    'score': result.score,
                    'relevance': result.relevance,
                    'metadata': result.document.metadata
                })
            
            # Cache ผลลัพธ์
            self.cache.setex(cache_key, 1800, json.dumps(search_results))  # 30 นาที
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการค้นหา: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """ดึงข้อมูลประสิทธิภาพ"""
        return {
            'total_time': self.metrics.total_time,
            'files_processed': self.metrics.files_processed,
            'documents_extracted': self.metrics.documents_extracted,
            'embeddings_generated': self.metrics.embeddings_generated,
            'files_per_second': self.metrics.files_per_second,
            'documents_per_second': self.metrics.documents_per_second,
            'cache_hits': self.metrics.cache_hits,
            'cache_misses': self.metrics.cache_misses,
            'cache_hit_rate': self.metrics.cache_hits / (self.metrics.cache_hits + self.metrics.cache_misses) if (self.metrics.cache_hits + self.metrics.cache_misses) > 0 else 0,
            'errors': self.metrics.errors
        }
