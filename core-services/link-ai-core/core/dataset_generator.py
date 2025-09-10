#!/usr/bin/env python3
"""
Dataset Generator สำหรับ AI Agent Multi-Action
สร้างดาต้าเซ็ตจาก log และข้อมูลต่างๆ ในโปรเจ็ค
ปรับปรุงเพื่อแก้ปัญหาที่พบจากบันทึกการทำงาน
"""

import json
import re
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetEntry:
    """โครงสร้างข้อมูลสำหรับแต่ละ entry ในดาต้าเซ็ต"""
    id: str
    timestamp: str
    source: str  # 'User', 'AI', 'System', 'Error', 'Solution'
    type: str    # 'Instruction', 'Response', 'Error', 'Code', 'Correction', 'Problem', 'Solution'
    content: str
    metadata: Optional[Dict[str, Any]] = None
    relationships: Optional[Dict[str, str]] = None
    problem_context: Optional[str] = None
    solution_approach: Optional[str] = None

class DatasetGenerator:
    """คลาสหลักสำหรับการสร้างดาต้าเซ็ต - ปรับปรุงเพื่อแก้ปัญหาที่พบ"""

    def __init__(self, project_root: str = ".") -> None:
        self.project_root = Path(project_root)
        self.datasets_dir = self.project_root / "datasets"
        self.datasets_dir.mkdir(exist_ok=True)

        # สร้างโฟลเดอร์สำหรับดาต้าเซ็ตแต่ละประเภท
        self.ift_dir = self.datasets_dir / "instruction_fine_tuning"
        self.rag_dir = self.datasets_dir / "rag_knowledge_base"
        self.forecast_dir = self.datasets_dir / "forecasting_prediction"
        self.problem_solution_dir = self.datasets_dir / "problem_solution_patterns"

        for dir_path in [self.ift_dir, self.rag_dir, self.forecast_dir, self.problem_solution_dir]:
            dir_path.mkdir(exist_ok=True)

    def parse_log_file(self, log_file_path: str) -> List[DatasetEntry]:
        """แปลง log file เป็น structured data - ปรับปรุงเพื่อจับคู่ปัญหา-วิธีแก้"""
        entries: List[DatasetEntry] = []

        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # แยกบล็อกตาม --- หรือ User/AI patterns
            blocks = self._split_into_blocks(content)

            for i, block in enumerate(blocks):
                if not block.strip():
                    continue

                # ระบุประเภทของบล็อก
                entry_type = self._classify_block(block)
                source = self._extract_source(block)

                # ทำความสะอาดเนื้อหา
                cleaned_content = self._clean_content(block)

                if cleaned_content:
                    # สกัดปัญหาและวิธีแก้
                    problem_context = self._extract_problem_context(block)
                    solution_approach = self._extract_solution_approach(block)

                    entry = DatasetEntry(
                        id=f"log_entry_{i:03d}",
                        timestamp=datetime.now().isoformat(),
                        source=source,
                        type=entry_type,
                        content=cleaned_content,
                        metadata=self._extract_metadata(block),
                        relationships=self._extract_relationships(block, i),
                        problem_context=problem_context,
                        solution_approach=solution_approach
                    )
                    entries.append(entry)

            logger.info(f"Parsed {len(entries)} entries from log file")
            return entries

        except Exception as e:
            logger.error(f"Error parsing log file: {e}")
            return []

    def _split_into_blocks(self, content: str) -> List[str]:
        """แยกเนื้อหาเป็นบล็อก - ปรับปรุงเพื่อจับคู่ User/AI patterns"""
        blocks: List[str] = []
        
        # แยกตาม ---
        basic_blocks = content.split('---')
        
        for block in basic_blocks:
            if not block.strip():
                continue
                
            # แยก User/AI patterns เพิ่มเติม
            user_ai_blocks = self._split_user_ai_patterns(block)
            blocks.extend(user_ai_blocks)
        
        return blocks

    def _split_user_ai_patterns(self, block: str) -> List[str]:
        """แยก User/AI patterns ในบล็อก"""
        patterns = [
            r'(User\s*\n.*?)(?=User\s*\n|AI\s*\n|$)',
            r'(AI\s*\n.*?)(?=User\s*\n|AI\s*\n|$)',
            r'(Cursor\s*\n.*?)(?=User\s*\n|AI\s*\n|Cursor\s*\n|$)',
            r'(System\s*\n.*?)(?=User\s*\n|AI\s*\n|System\s*\n|$)',
        ]
        
        blocks: List[str] = []
        remaining = block
        
        for pattern in patterns:
            matches = re.finditer(pattern, remaining, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match.group(1).strip():
                    blocks.append(match.group(1).strip())
        
        # ถ้าไม่มี pattern ให้ใช้บล็อกเดิม
        if not blocks and block.strip():
            blocks.append(block.strip())
        
        return blocks

    def _classify_block(self, block: str) -> str:
        """ระบุประเภทของบล็อก - เพิ่มประเภทใหม่"""
        block_lower = block.lower()

        # ตรวจสอบปัญหาและวิธีแก้
        if any(keyword in block_lower for keyword in ['error', 'exception', 'failed', 'problem', 'issue']):
            return 'Problem'
        elif any(keyword in block_lower for keyword in ['fix', 'correct', 'แก้ไข', 'solution', 'resolve']):
            return 'Solution'
        elif any(keyword in block_lower for keyword in ['def ', 'class ', 'function', 'import', 'code']):
            return 'Code'
        elif any(keyword in block_lower for keyword in ['user:', 'user ']):
            return 'Instruction'
        elif any(keyword in block_lower for keyword in ['cursor:', 'ai:', 'assistant:']):
            return 'Response'
        elif any(keyword in block_lower for keyword in ['test', 'testing', 'pytest']):
            return 'Testing'
        elif any(keyword in block_lower for keyword in ['config', 'setup', 'install']):
            return 'Configuration'
        else:
            return 'System'

    def _extract_source(self, block: str) -> str:
        """สกัดแหล่งที่มาของข้อมูล"""
        if 'user:' in block.lower() or 'user ' in block.lower():
            return 'User'
        elif 'cursor:' in block.lower() or 'ai:' in block.lower():
            return 'AI'
        elif 'system:' in block.lower() or 'system ' in block.lower():
            return 'System'
        elif any(keyword in block.lower() for keyword in ['error', 'exception', 'failed']):
            return 'Error'
        else:
            return 'System'

    def _extract_problem_context(self, block: str) -> Optional[str]:
        """สกัดบริบทของปัญหา"""
        problem_patterns = [
            r'error[:\s]+(.*?)(?=\n|$)',
            r'exception[:\s]+(.*?)(?=\n|$)',
            r'failed[:\s]+(.*?)(?=\n|$)',
            r'problem[:\s]+(.*?)(?=\n|$)',
            r'issue[:\s]+(.*?)(?=\n|$)',
            r'ไม่ทำงาน(.*?)(?=\n|$)',
            r'มีปัญหา(.*?)(?=\n|$)',
        ]
        
        for pattern in problem_patterns:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_solution_approach(self, block: str) -> Optional[str]:
        """สกัดวิธีการแก้ปัญหา"""
        solution_patterns = [
            r'fix[:\s]+(.*?)(?=\n|$)',
            r'solution[:\s]+(.*?)(?=\n|$)',
            r'resolve[:\s]+(.*?)(?=\n|$)',
            r'แก้ไข[:\s]+(.*?)(?=\n|$)',
            r'แก้ปัญหา[:\s]+(.*?)(?=\n|$)',
            r'วิธีแก้[:\s]+(.*?)(?=\n|$)',
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _clean_content(self, block: str) -> str:
        """ทำความสะอาดเนื้อหา"""
        # ลบ request ID และข้อมูลที่ไม่เกี่ยวข้อง
        cleaned = re.sub(r'Request ID: [a-f0-9-]+', '', block)
        cleaned = re.sub(r'Timestamp: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', '', cleaned)

        # แก้ไขปัญหาอักขระที่ผิดเพี้ยน
        cleaned = cleaned.replace('แ', 'แ')  # แก้ไขอักขระที่ผิดเพี้ยน

        # ลบ whitespace ที่ไม่จำเป็น
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def _extract_metadata(self, block: str) -> Dict[str, Any]:
        """สกัด metadata จากบล็อก"""
        metadata: Dict[str, Any] = {}

        # สกัด file path ถ้ามี
        file_match = re.search(r'File: ([^\n]+)', block)
        if file_match:
            metadata['file_path'] = file_match.group(1)

        # สกัด language ถ้ามี
        if 'typescript' in block.lower() or '.ts' in block:
            metadata['language'] = 'TypeScript'
        elif 'python' in block.lower() or '.py' in block:
            metadata['language'] = 'Python'
        elif 'javascript' in block.lower() or '.js' in block:
            metadata['language'] = 'JavaScript'

        # สกัดประเภทปัญหา
        if self._extract_problem_context(block):
            metadata['has_problem'] = True
        if self._extract_solution_approach(block):
            metadata['has_solution'] = True

        return metadata

    def _extract_relationships(self, block: str, index: int) -> Dict[str, str]:
        """สกัดความสัมพันธ์ระหว่าง entries"""
        relationships: Dict[str, str] = {}

        # ตรวจสอบว่าตอบกลับ entry ก่อนหน้าหรือไม่
        if index > 0:
            relationships['responds_to'] = f"log_entry_{index-1:03d}"

        return relationships

    def create_ift_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตสำหรับ Instruction Fine-Tuning - ปรับปรุงเพื่อจับคู่ปัญหา-วิธีแก้"""
        ift_entries: List[Dict[str, Any]] = []

        # จับคู่ Instruction-Response ปกติ
        for entry in entries:
            if entry.type in ['Instruction', 'Problem']:
                # หา response ที่เกี่ยวข้อง
                response = self._find_related_response(entries, entry.id)

                if response:
                    ift_entry = {
                        "instruction": entry.content,
                        "context": self._extract_context(entries, entry.id),
                        "response": response.content,
                        "metadata": {
                            "source_entry": entry.id,
                            "response_entry": response.id,
                            "type": entry.type,
                            "has_problem": entry.problem_context is not None,
                            "has_solution": entry.solution_approach is not None
                        }
                    }
                    ift_entries.append(ift_entry)

        # จับคู่ปัญหา-วิธีแก้
        problem_solution_pairs = self._create_problem_solution_pairs(entries)
        ift_entries.extend(problem_solution_pairs)

        # บันทึกเป็น JSONL
        output_file = self.ift_dir / "instruction_fine_tuning_dataset.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in ift_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        logger.info(f"Created IFT dataset with {len(ift_entries)} entries")
        return str(output_file)

    def _create_problem_solution_pairs(self, entries: List[DatasetEntry]) -> List[Dict[str, Any]]:
        """สร้างคู่ปัญหา-วิธีแก้"""
        pairs: List[Dict[str, Any]] = []
        
        for i, entry in enumerate(entries):
            if entry.type == 'Problem' and entry.problem_context:
                # หาวิธีแก้ที่เกี่ยวข้อง
                solution = self._find_related_solution(entries, i)
                
                if solution:
                    pair = {
                        "instruction": f"แก้ไขปัญหา: {entry.problem_context}",
                        "context": entry.content,
                        "response": solution.content,
                        "metadata": {
                            "source_entry": entry.id,
                            "solution_entry": solution.id,
                            "type": "problem_solution",
                            "problem_type": self._classify_problem_type(entry.problem_context),
                            "solution_approach": solution.solution_approach
                        }
                    }
                    pairs.append(pair)
        
        return pairs

    def _find_related_solution(self, entries: List[DatasetEntry], problem_index: int) -> Optional[DatasetEntry]:
        """หา solution ที่เกี่ยวข้องกับปัญหา"""
        # ค้นหา solution ใน entries ถัดไป
        for i in range(problem_index + 1, min(problem_index + 5, len(entries))):
            if entries[i].type == 'Solution' or entries[i].solution_approach:
                return entries[i]
        
        return None

    def _classify_problem_type(self, problem_context: str) -> str:
        """จำแนกประเภทของปัญหา"""
        problem_lower = problem_context.lower()
        
        if any(keyword in problem_lower for keyword in ['import', 'module', 'no module']):
            return 'ImportError'
        elif any(keyword in problem_lower for keyword in ['syntax', 'indentation']):
            return 'SyntaxError'
        elif any(keyword in problem_lower for keyword in ['connection', 'timeout', 'network']):
            return 'ConnectionError'
        elif any(keyword in problem_lower for keyword in ['permission', 'access', 'denied']):
            return 'PermissionError'
        elif any(keyword in problem_lower for keyword in ['test', 'pytest', 'assertion']):
            return 'TestError'
        else:
            return 'GeneralError'

    def _find_related_response(self, entries: List[DatasetEntry], entry_id: str) -> Optional[DatasetEntry]:
        """หา response ที่เกี่ยวข้องกับ entry"""
        for entry in entries:
            if (entry.relationships and
                entry.relationships.get('responds_to') == entry_id and
                entry.type == 'Response'):
                return entry
        return None

    def _extract_context(self, entries: List[DatasetEntry], entry_id: str) -> str:
        """สกัด context จาก entries ก่อนหน้า"""
        context_parts: List[str] = []

        for entry in entries:
            if entry.id == entry_id:
                break
            if entry.type in ['Error', 'System', 'Problem']:
                context_parts.append(entry.content[:200])  # จำกัดความยาว

        return "\n".join(context_parts[-3:])  # เอาแค่ 3 entries ล่าสุด

    def create_rag_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตสำหรับ RAG Knowledge Base"""
        rag_entries: List[Dict[str, Any]] = []

        for entry in entries:
            if entry.type in ['Code', 'System', 'Configuration', 'Testing']:
                # แบ่งเป็น chunks
                chunks = self._create_chunks(entry.content)

                for i, chunk in enumerate(chunks):
                    metadata = entry.metadata or {}
                    rag_entry = {
                        "chunk_id": f"{entry.id}_chunk_{i}",
                        "content": chunk,
                        "metadata": {
                            "source_entry": entry.id,
                            "chunk_index": i,
                            "file_path": metadata.get('file_path', ''),
                            "language": metadata.get('language', ''),
                            "type": entry.type,
                            "has_problem": metadata.get('has_problem', False),
                            "has_solution": metadata.get('has_solution', False)
                        }
                    }
                    rag_entries.append(rag_entry)

        # บันทึกเป็น JSON
        output_file = self.rag_dir / "rag_knowledge_base.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": "rag_knowledge_base",
                "description": "Knowledge base for RAG system - enhanced with problem-solution patterns",
                "version": "2.0.0",
                "created_date": datetime.now().isoformat(),
                "chunks": rag_entries
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"Created RAG dataset with {len(rag_entries)} chunks")
        return str(output_file)

    def create_forecast_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตสำหรับ Forecasting & Prediction - เพิ่มการคาดการณ์ปัญหา"""
        forecast_entries: List[Dict[str, Any]] = []

        for i, entry in enumerate(entries):
            if i < len(entries) - 1:
                next_entry = entries[i + 1]

                forecast_entry = {
                    "previous_state": entry.content,
                    "action": self._extract_action(entry),
                    "new_state": next_entry.content,
                    "outcome": self._classify_outcome(entry, next_entry),
                    "metadata": {
                        "previous_entry": entry.id,
                        "next_entry": next_entry.id,
                        "timestamp": entry.timestamp,
                        "problem_predicted": entry.type == 'Problem',
                        "solution_provided": next_entry.type == 'Solution'
                    }
                }
                forecast_entries.append(forecast_entry)

        # บันทึกเป็น JSON
        output_file = self.forecast_dir / "forecasting_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": "forecasting_prediction",
                "description": "Dataset for predicting outcomes and user intent - enhanced with problem prediction",
                "version": "2.0.0",
                "created_date": datetime.now().isoformat(),
                "predictions": forecast_entries
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"Created forecasting dataset with {len(forecast_entries)} entries")
        return str(output_file)

    def create_problem_solution_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตเฉพาะสำหรับปัญหา-วิธีแก้"""
        problem_solution_entries: List[Dict[str, Any]] = []

        for entry in entries:
            if entry.type == 'Problem' and entry.problem_context:
                solution = self._find_related_solution(entries, entries.index(entry))
                
                if solution:
                    ps_entry = {
                        "problem": {
                            "description": entry.problem_context,
                            "full_context": entry.content,
                            "type": self._classify_problem_type(entry.problem_context),
                            "source": entry.source
                        },
                        "solution": {
                            "description": solution.solution_approach or solution.content,
                            "full_context": solution.content,
                            "approach": solution.solution_approach,
                            "source": solution.source
                        },
                        "metadata": {
                            "problem_entry": entry.id,
                            "solution_entry": solution.id,
                            "problem_type": self._classify_problem_type(entry.problem_context),
                            "success_rate": self._estimate_success_rate(entry, solution)
                        }
                    }
                    problem_solution_entries.append(ps_entry)

        # บันทึกเป็น JSON
        output_file = self.problem_solution_dir / "problem_solution_patterns.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": "problem_solution_patterns",
                "description": "Dataset of common problems and their solutions for AI training",
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "patterns": problem_solution_entries
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"Created problem-solution dataset with {len(problem_solution_entries)} patterns")
        return str(output_file)

    def create_planning_workflow_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตสำหรับการวางแผนและ workflow"""
        planning_entries: List[Dict[str, Any]] = []

        for entry in entries:
            if entry.type in ['Planning', 'Workflow', 'ToolSelection']:
                metadata = entry.metadata or {}
                
                planning_entry = {
                    "task_description": entry.content,
                    "planning_type": entry.type,
                    "planning_info": metadata.get('planning_info', {}),
                    "tool_info": metadata.get('tool_info', {}),
                    "workflow_steps": metadata.get('workflow_steps', []),
                    "metadata": {
                        "source_entry": entry.id,
                        "has_planning": metadata.get('planning_info') is not None,
                        "has_tools": metadata.get('tool_info') is not None,
                        "has_workflow": metadata.get('workflow_steps') is not None
                    }
                }
                planning_entries.append(planning_entry)

        # บันทึกเป็น JSON
        output_file = self.problem_solution_dir / "planning_workflow_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": "planning_workflow_dataset",
                "description": "Dataset for AI planning and workflow management",
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "planning_entries": planning_entries
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"Created planning workflow dataset with {len(planning_entries)} entries")
        return str(output_file)

    def create_tool_selection_dataset(self, entries: List[DatasetEntry]) -> str:
        """สร้างดาต้าเซ็ตสำหรับการเลือกเครื่องมือ"""
        tool_entries: List[Dict[str, Any]] = []

        for entry in entries:
            if entry.type == 'ToolSelection' or (entry.metadata and entry.metadata.get('tool_info')):
                metadata = entry.metadata or {}
                tool_info = metadata.get('tool_info', {})
                
                tool_entry = {
                    "context": entry.content,
                    "tools_used": tool_info.get('tools_used', []),
                    "commands": tool_info.get('commands', []),
                    "tool_selection_reasoning": self._extract_tool_reasoning(entry.content),
                    "success_rate": self._estimate_tool_success_rate(entry.content),
                    "metadata": {
                        "source_entry": entry.id,
                        "tool_count": len(tool_info.get('tools_used', [])),
                        "command_count": len(tool_info.get('commands', []))
                    }
                }
                tool_entries.append(tool_entry)

        # บันทึกเป็น JSON
        output_file = self.problem_solution_dir / "tool_selection_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": "tool_selection_dataset",
                "description": "Dataset for AI tool selection and command execution",
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "tool_entries": tool_entries
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"Created tool selection dataset with {len(tool_entries)} entries")
        return str(output_file)

    def _estimate_success_rate(self, problem: DatasetEntry, solution: DatasetEntry) -> float:
        """ประมาณอัตราความสำเร็จของการแก้ปัญหา"""
        # ใช้ heuristics ง่ายๆ
        success_indicators = [
            'success', 'fixed', 'resolved', 'working', 'correct',
            'สำเร็จ', 'แก้ไขแล้ว', 'ทำงานได้', 'ถูกต้อง'
        ]
        
        failure_indicators = [
            'failed', 'error', 'exception', 'not working', 'still broken',
            'ล้มเหลว', 'ยังมีปัญหา', 'ไม่ทำงาน', 'ผิดพลาด'
        ]
        
        content_lower = solution.content.lower()
        
        success_count = sum(1 for indicator in success_indicators if indicator in content_lower)
        failure_count = sum(1 for indicator in failure_indicators if indicator in content_lower)
        
        if success_count > failure_count:
            return 0.8
        elif failure_count > success_count:
            return 0.2
        else:
            return 0.5

    def _create_chunks(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """แบ่งเนื้อหาเป็น chunks"""
        chunks: List[str] = []
        lines = content.split('\n')
        current_chunk: List[str] = []
        current_size = 0

        for line in lines:
            if current_size + len(line) > max_chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def _extract_action(self, entry: DatasetEntry) -> str:
        """สกัด action จาก entry"""
        if entry.type == 'Instruction':
            return entry.content
        elif entry.type == 'Problem':
            return f"Problem occurred: {entry.problem_context or entry.content[:100]}"
        elif entry.type == 'Solution':
            return f"Solution applied: {entry.solution_approach or entry.content[:100]}"
        else:
            return "System action"

    def _classify_outcome(self, current_entry: DatasetEntry, next_entry: DatasetEntry) -> str:
        """จำแนกผลลัพธ์"""
        if next_entry.type == 'Error' or next_entry.type == 'Problem':
            return 'error'
        elif next_entry.type == 'Solution' or next_entry.type == 'Correction':
            return 'correction'
        elif next_entry.type == 'Response':
            return 'success'
        else:
            return 'neutral'

    def generate_all_datasets(self, log_file_path: str) -> Dict[str, str]:
        """สร้างดาต้าเซ็ตทั้งหมด - เพิ่ม planning และ tool selection datasets"""
        logger.info("Starting enhanced dataset generation with planning and tool selection...")

        # Parse log file
        entries = self.parse_log_file(log_file_path)

        if not entries:
            logger.error("No entries found in log file")
            return {}

        # สร้างดาต้าเซ็ตแต่ละประเภท
        results: Dict[str, str] = {}

        try:
            results['ift'] = self.create_ift_dataset(entries)
            results['rag'] = self.create_rag_dataset(entries)
            results['forecast'] = self.create_forecast_dataset(entries)
            results['problem_solution'] = self.create_problem_solution_dataset(entries)
            results['planning_workflow'] = self.create_planning_workflow_dataset(entries)
            results['tool_selection'] = self.create_tool_selection_dataset(entries)

            logger.info("All datasets generated successfully")

        except Exception as e:
            logger.error(f"Error generating datasets: {e}")

        return results

    def create_dataset_summary(self, results: Dict[str, str]) -> str:
        """สร้างรายงานสรุปดาต้าเซ็ต"""
        summary = {
            "generation_date": datetime.now().isoformat(),
            "datasets_created": len(results),
            "files": results,
            "statistics": self._calculate_statistics(results),
            "enhancements": {
                "problem_solution_patterns": True,
                "improved_classification": True,
                "context_extraction": True,
                "relationship_mapping": True
            }
        }

        summary_file = self.datasets_dir / "dataset_generation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        return str(summary_file)

    def _calculate_statistics(self, results: Dict[str, str]) -> Dict[str, Any]:
        """คำนวณสถิติของดาต้าเซ็ต"""
        stats: Dict[str, Any] = {}

        for dataset_type, file_path in results.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.jsonl'):
                        # Count lines for JSONL
                        stats[dataset_type] = sum(1 for _ in f)
                    else:
                        # Parse JSON for other formats
                        data = json.load(f)
                        if dataset_type == 'rag':
                            stats[dataset_type] = len(data.get('chunks', []))
                        elif dataset_type == 'forecast':
                            stats[dataset_type] = len(data.get('predictions', []))
                        elif dataset_type == 'problem_solution':
                            stats[dataset_type] = len(data.get('patterns', []))
                        else:
                            stats[dataset_type] = len(data)
            except Exception as e:
                logger.error(f"Error calculating statistics for {dataset_type}: {e}")
                stats[dataset_type] = 0

        return stats

    def _extract_tool_reasoning(self, content: str) -> str:
        """สกัดเหตุผลในการเลือกเครื่องมือ"""
        reasoning_patterns = [
            r'เพราะ(.*?)(?=\n|$)',
            r'เนื่องจาก(.*?)(?=\n|$)',
            r'reason[:\s]+(.*?)(?=\n|$)',
            r'why[:\s]+(.*?)(?=\n|$)',
        ]
        
        for pattern in reasoning_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "No explicit reasoning provided"

    def _estimate_tool_success_rate(self, content: str) -> float:
        """ประมาณอัตราความสำเร็จของการใช้เครื่องมือ"""
        success_indicators = [
            'success', 'worked', 'completed', 'finished', 'done',
            'สำเร็จ', 'ทำงานได้', 'เสร็จแล้ว', 'เรียบร้อย'
        ]
        
        failure_indicators = [
            'failed', 'error', 'not working', 'broken', 'timeout',
            'ล้มเหลว', 'ไม่ทำงาน', 'ผิดพลาด', 'หมดเวลา'
        ]
        
        content_lower = content.lower()
        
        success_count = sum(1 for indicator in success_indicators if indicator in content_lower)
        failure_count = sum(1 for indicator in failure_indicators if indicator in content_lower)
        
        if success_count > failure_count:
            return 0.8
        elif failure_count > success_count:
            return 0.2
        else:
            return 0.5

def main() -> None:
    """ฟังก์ชันหลักสำหรับการรัน"""
    generator = DatasetGenerator()

    # ตัวอย่างการใช้งาน
    log_file = "example_log.txt"  # เปลี่ยนเป็น path ของ log file จริง

    if os.path.exists(log_file):
        results = generator.generate_all_datasets(log_file)
        summary_file = generator.create_dataset_summary(results)

        print(f"Enhanced dataset generation completed!")
        print(f"Summary saved to: {summary_file}")
        print(f"Generated files:")
        for dataset_type, file_path in results.items():
            print(f"  - {dataset_type}: {file_path}")
    else:
        print(f"Log file not found: {log_file}")
        print("Please provide a valid log file path")

if __name__ == "__main__":
    main()
