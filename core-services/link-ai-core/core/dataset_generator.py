#!/usr/bin/env python3
"""
Dataset Generator for AI Agent Multi-Action.

Creates datasets from logs and other data in the project.
Improved to address issues found in the work log.
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
    """
    Data structure for each entry in the dataset.

    Attributes:
        id (str): The ID of the entry.
        timestamp (str): The timestamp of the entry.
        source (str): The source of the entry ('User', 'AI', 'System', 'Error', 'Solution').
        type (str): The type of the entry ('Instruction', 'Response', 'Error', 'Code', 'Correction', 'Problem', 'Solution').
        content (str): The content of the entry.
        metadata (Optional[Dict[str, Any]]): Metadata for the entry.
        relationships (Optional[Dict[str, str]]): Relationships with other entries.
        problem_context (Optional[str]): The context of the problem.
        solution_approach (Optional[str]): The approach to the solution.
    """
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
    """
    Main class for creating datasets - improved to address found issues.

    Attributes:
        project_root (Path): The root of the project.
        datasets_dir (Path): The directory for datasets.
        ift_dir (Path): The directory for instruction fine-tuning datasets.
        rag_dir (Path): The directory for RAG knowledge base datasets.
        forecast_dir (Path): The directory for forecasting and prediction datasets.
        problem_solution_dir (Path): The directory for problem-solution pattern datasets.
    """

    def __init__(self, project_root: str = ".") -> None:
        """
        Initializes the DatasetGenerator.

        Args:
            project_root (str): The root of the project.
        """
        self.project_root = Path(project_root)
        self.datasets_dir = self.project_root / "datasets"
        self.datasets_dir.mkdir(exist_ok=True)

        # Create folders for each type of dataset
        self.ift_dir = self.datasets_dir / "instruction_fine_tuning"
        self.rag_dir = self.datasets_dir / "rag_knowledge_base"
        self.forecast_dir = self.datasets_dir / "forecasting_prediction"
        self.problem_solution_dir = self.datasets_dir / "problem_solution_patterns"

        for dir_path in [self.ift_dir, self.rag_dir, self.forecast_dir, self.problem_solution_dir]:
            dir_path.mkdir(exist_ok=True)

    def parse_log_file(self, log_file_path: str) -> List[DatasetEntry]:
        """
        Converts a log file to structured data - improved to match problems and solutions.

        Args:
            log_file_path (str): The path to the log file.

        Returns:
            List[DatasetEntry]: A list of dataset entries.
        """
        entries: List[DatasetEntry] = []

        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into blocks by --- or User/AI patterns
            blocks = self._split_into_blocks(content)

            for i, block in enumerate(blocks):
                if not block.strip():
                    continue

                # Classify the block type
                entry_type = self._classify_block(block)
                source = self._extract_source(block)

                # Clean the content
                cleaned_content = self._clean_content(block)

                if cleaned_content:
                    # Extract problem and solution
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
        """
        Splits content into blocks - improved to match User/AI patterns.

        Args:
            content (str): The content to split.

        Returns:
            List[str]: A list of content blocks.
        """
        blocks: List[str] = []
        
        # Split by ---
        basic_blocks = content.split('---')
        
        for block in basic_blocks:
            if not block.strip():
                continue
                
            # Further split by User/AI patterns
            user_ai_blocks = self._split_user_ai_patterns(block)
            blocks.extend(user_ai_blocks)
        
        return blocks

    def _split_user_ai_patterns(self, block: str) -> List[str]:
        """
        Splits User/AI patterns in a block.

        Args:
            block (str): The block to split.

        Returns:
            List[str]: A list of split blocks.
        """
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
        
        # If no pattern matches, use the original block
        if not blocks and block.strip():
            blocks.append(block.strip())
        
        return blocks

    def _classify_block(self, block: str) -> str:
        """
        Classifies the type of a block - new types added.

        Args:
            block (str): The block to classify.

        Returns:
            str: The classified block type.
        """
        block_lower = block.lower()

        # Check for problems and solutions
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
        """
        Extracts the source of the data.

        Args:
            block (str): The block to extract the source from.

        Returns:
            str: The source of the data.
        """
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
        """
        Extracts the context of a problem.

        Args:
            block (str): The block to extract the problem context from.

        Returns:
            Optional[str]: The problem context, or None if not found.
        """
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
        """
        Extracts the solution approach.

        Args:
            block (str): The block to extract the solution approach from.

        Returns:
            Optional[str]: The solution approach, or None if not found.
        """
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
        """
        Cleans the content.

        Args:
            block (str): The content to clean.

        Returns:
            str: The cleaned content.
        """
        # Remove request ID and irrelevant information
        cleaned = re.sub(r'Request ID: [a-f0-9-]+', '', block)
        cleaned = re.sub(r'Timestamp: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', '', cleaned)

        # Fix garbled characters
        cleaned = cleaned.replace('แ', 'แ')  # Fix garbled characters

        # Remove unnecessary whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def _extract_metadata(self, block: str) -> Dict[str, Any]:
        """
        Extracts metadata from a block.

        Args:
            block (str): The block to extract metadata from.

        Returns:
            Dict[str, Any]: The extracted metadata.
        """
        metadata: Dict[str, Any] = {}

        # Extract file path if present
        file_match = re.search(r'File: ([^\n]+)', block)
        if file_match:
            metadata['file_path'] = file_match.group(1)

        # Extract language if present
        if 'typescript' in block.lower() or '.ts' in block:
            metadata['language'] = 'TypeScript'
        elif 'python' in block.lower() or '.py' in block:
            metadata['language'] = 'Python'
        elif 'javascript' in block.lower() or '.js' in block:
            metadata['language'] = 'JavaScript'

        # Extract problem type
        if self._extract_problem_context(block):
            metadata['has_problem'] = True
        if self._extract_solution_approach(block):
            metadata['has_solution'] = True

        return metadata

    def _extract_relationships(self, block: str, index: int) -> Dict[str, str]:
        """
        Extracts relationships between entries.

        Args:
            block (str): The block to extract relationships from.
            index (int): The index of the block.

        Returns:
            Dict[str, str]: The extracted relationships.
        """
        relationships: Dict[str, str] = {}

        # Check if it responds to the previous entry
        if index > 0:
            relationships['responds_to'] = f"log_entry_{index-1:03d}"

        return relationships

    def create_ift_dataset(self, entries: List[DatasetEntry]) -> str:
        """
        Creates a dataset for Instruction Fine-Tuning - improved to match problems and solutions.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
        ift_entries: List[Dict[str, Any]] = []

        # Match normal Instruction-Response
        for entry in entries:
            if entry.type in ['Instruction', 'Problem']:
                # Find the related response
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

        # Match problems and solutions
        problem_solution_pairs = self._create_problem_solution_pairs(entries)
        ift_entries.extend(problem_solution_pairs)

        # Save as JSONL
        output_file = self.ift_dir / "instruction_fine_tuning_dataset.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in ift_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        logger.info(f"Created IFT dataset with {len(ift_entries)} entries")
        return str(output_file)

    def _create_problem_solution_pairs(self, entries: List[DatasetEntry]) -> List[Dict[str, Any]]:
        """
        Creates problem-solution pairs.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            List[Dict[str, Any]]: A list of problem-solution pairs.
        """
        pairs: List[Dict[str, Any]] = []
        
        for i, entry in enumerate(entries):
            if entry.type == 'Problem' and entry.problem_context:
                # Find the related solution
                solution = self._find_related_solution(entries, i)
                
                if solution:
                    pair = {
                        "instruction": f"Fix the problem: {entry.problem_context}",
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
        """
        Finds a solution related to a problem.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.
            problem_index (int): The index of the problem entry.

        Returns:
            Optional[DatasetEntry]: The related solution entry, or None if not found.
        """
        # Search for a solution in the next few entries
        for i in range(problem_index + 1, min(problem_index + 5, len(entries))):
            if entries[i].type == 'Solution' or entries[i].solution_approach:
                return entries[i]
        
        return None

    def _classify_problem_type(self, problem_context: str) -> str:
        """
        Classifies the type of a problem.

        Args:
            problem_context (str): The context of the problem.

        Returns:
            str: The classified problem type.
        """
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
        """
        Finds a response related to an entry.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.
            entry_id (str): The ID of the entry to find a response for.

        Returns:
            Optional[DatasetEntry]: The related response entry, or None if not found.
        """
        for entry in entries:
            if (entry.relationships and
                entry.relationships.get('responds_to') == entry_id and
                entry.type == 'Response'):
                return entry
        return None

    def _extract_context(self, entries: List[DatasetEntry], entry_id: str) -> str:
        """
        Extracts context from previous entries.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.
            entry_id (str): The ID of the current entry.

        Returns:
            str: The extracted context.
        """
        context_parts: List[str] = []

        for entry in entries:
            if entry.id == entry_id:
                break
            if entry.type in ['Error', 'System', 'Problem']:
                context_parts.append(entry.content[:200])  # Limit length

        return "\n".join(context_parts[-3:])  # Take only the last 3 entries

    def create_rag_dataset(self, entries: List[DatasetEntry]) -> str:
        """
        Creates a dataset for the RAG Knowledge Base.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
        rag_entries: List[Dict[str, Any]] = []

        for entry in entries:
            if entry.type in ['Code', 'System', 'Configuration', 'Testing']:
                # Split into chunks
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

        # Save as JSON
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
        """
        Creates a dataset for Forecasting & Prediction - adds problem prediction.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
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

        # Save as JSON
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
        """
        Creates a dataset specifically for problems and solutions.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
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

        # Save as JSON
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
        """
        Creates a dataset for planning and workflow.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
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

        # Save as JSON
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
        """
        Creates a dataset for tool selection.

        Args:
            entries (List[DatasetEntry]): A list of dataset entries.

        Returns:
            str: The path to the created dataset file.
        """
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

        # Save as JSON
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
        """
        Estimates the success rate of a solution.

        Args:
            problem (DatasetEntry): The problem entry.
            solution (DatasetEntry): The solution entry.

        Returns:
            float: The estimated success rate.
        """
        # Use simple heuristics
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
        """
        Splits content into chunks.

        Args:
            content (str): The content to split.
            max_chunk_size (int): The maximum size of each chunk.

        Returns:
            List[str]: A list of content chunks.
        """
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
        """
        Extracts an action from an entry.

        Args:
            entry (DatasetEntry): The entry to extract the action from.

        Returns:
            str: The extracted action.
        """
        if entry.type == 'Instruction':
            return entry.content
        elif entry.type == 'Problem':
            return f"Problem occurred: {entry.problem_context or entry.content[:100]}"
        elif entry.type == 'Solution':
            return f"Solution applied: {entry.solution_approach or entry.content[:100]}"
        else:
            return "System action"

    def _classify_outcome(self, current_entry: DatasetEntry, next_entry: DatasetEntry) -> str:
        """
        Classifies the outcome of an action.

        Args:
            current_entry (DatasetEntry): The current entry.
            next_entry (DatasetEntry): The next entry.

        Returns:
            str: The classified outcome.
        """
        if next_entry.type == 'Error' or next_entry.type == 'Problem':
            return 'error'
        elif next_entry.type == 'Solution' or next_entry.type == 'Correction':
            return 'correction'
        elif next_entry.type == 'Response':
            return 'success'
        else:
            return 'neutral'

    def generate_all_datasets(self, log_file_path: str) -> Dict[str, str]:
        """
        Generates all datasets - adds planning and tool selection datasets.

        Args:
            log_file_path (str): The path to the log file.

        Returns:
            Dict[str, str]: A dictionary of the created dataset file paths.
        """
        logger.info("Starting enhanced dataset generation with planning and tool selection...")

        # Parse log file
        entries = self.parse_log_file(log_file_path)

        if not entries:
            logger.error("No entries found in log file")
            return {}

        # Create each type of dataset
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
        """
        Creates a summary report of the datasets.

        Args:
            results (Dict[str, str]): A dictionary of the created dataset file paths.

        Returns:
            str: The path to the summary file.
        """
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
        """
        Calculates statistics for the datasets.

        Args:
            results (Dict[str, str]): A dictionary of the created dataset file paths.

        Returns:
            Dict[str, Any]: A dictionary of dataset statistics.
        """
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
        """
        Extracts the reasoning for tool selection.

        Args:
            content (str): The content to extract the reasoning from.

        Returns:
            str: The extracted reasoning.
        """
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
        """
        Estimates the success rate of a tool.

        Args:
            content (str): The content to estimate the success rate from.

        Returns:
            float: The estimated success rate.
        """
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
    """Main function for running the script."""
    generator = DatasetGenerator()

    # Example usage
    log_file = "example_log.txt"  # Change to the actual log file path

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
