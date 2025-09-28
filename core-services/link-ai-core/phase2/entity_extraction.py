#!/usr/bin/env python3
"""
Entity Extraction Pipeline for Project Manifest System - Phase 2

Extracts entities, concepts, and relationships from source code and documentation files.
Uses NLP models to identify important terms and their relationships.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

@dataclass
class Entity:
    """
    Represents an extracted entity.

    Attributes:
        name (str): The entity name.
        type (str): The entity type (function, class, concept, etc.).
        confidence (float): Confidence score of the extraction.
        context (str): Surrounding context where the entity was found.
        file_path (str): Path to the file where the entity was found.
        line_number (int): Line number where the entity appears.
        metadata (Dict[str, Any]): Additional metadata.
    """
    name: str
    type: str
    confidence: float
    context: str
    file_path: str
    line_number: int
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class EntityExtractor:
    """
    Extracts entities from various file types using NLP and pattern matching.

    Supports multiple file types and uses different extraction strategies
    for code files, documentation, and configuration files.

    Attributes:
        nlp (spacy.Language): SpaCy language model for NLP processing.
        ner_pipeline: HuggingFace NER pipeline for named entity recognition.
        device (str): Device to run models on ('cpu' or 'cuda').
    """

    def __init__(self):
        """Initialize the entity extractor with required models."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logging.info(f"Using device: {self.device}")

        # Initialize SpaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("SpaCy model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Initialize NER pipeline
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                device=0 if self.device == 'cuda' else -1,
                aggregation_strategy="simple"
            )
        except Exception as e:
            logging.warning(f"Could not load NER model: {e}. Using fallback.")
            self.ner_pipeline = None

        # Define file type handlers
        self.file_handlers = {
            '.py': self._extract_from_python,
            '.js': self._extract_from_javascript,
            '.ts': self._extract_from_typescript,
            '.tsx': self._extract_from_typescript,
            '.md': self._extract_from_markdown,
            '.txt': self._extract_from_text,
            '.json': self._extract_from_json,
            '.yaml': self._extract_from_yaml,
            '.yml': self._extract_from_yaml,
        }

    def extract_entities(self, file_path: str) -> List[Entity]:
        """
        Extract entities from a file.

        Args:
            file_path (str): Path to the file to analyze.

        Returns:
            List[Entity]: List of extracted entities.
        """
        try:
            path = Path(file_path)

            if not path.exists():
                logging.warning(f"File does not exist: {file_path}")
                return []

            # Get file extension and find appropriate handler
            extension = path.suffix.lower()
            handler = self.file_handlers.get(extension, self._extract_from_generic)

            # Extract entities using the appropriate handler
            entities = handler(file_path)

            logging.info(f"Extracted {len(entities)} entities from {file_path}")
            return entities

        except Exception as e:
            logging.error(f"Error extracting entities from {file_path}: {e}")
            return []

    def _extract_from_python(self, file_path: str) -> List[Entity]:
        """Extract entities from Python files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Extract classes
            class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=class_name,
                    type='class',
                    confidence=0.95,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'python'}
                ))

            # Extract functions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=func_name,
                    type='function',
                    confidence=0.90,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'python'}
                ))

            # Extract imports and key terms
            entities.extend(self._extract_key_terms(content, file_path, 'python'))

        except Exception as e:
            logging.error(f"Error processing Python file {file_path}: {e}")

        return entities

    def _extract_from_javascript(self, file_path: str) -> List[Entity]:
        """Extract entities from JavaScript files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Extract classes
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=class_name,
                    type='class',
                    confidence=0.95,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'javascript'}
                ))

            # Extract functions
            func_pattern = r'(?:function\s+|const\s+|let\s+|var\s+)\s*(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function\s*\([^)]*\))'
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=func_name,
                    type='function',
                    confidence=0.85,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'javascript'}
                ))

            # Extract key terms
            entities.extend(self._extract_key_terms(content, file_path, 'javascript'))

        except Exception as e:
            logging.error(f"Error processing JavaScript file {file_path}: {e}")

        return entities

    def _extract_from_typescript(self, file_path: str) -> List[Entity]:
        """Extract entities from TypeScript files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Extract interfaces
            interface_pattern = r'interface\s+(\w+)'
            for match in re.finditer(interface_pattern, content):
                interface_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=interface_name,
                    type='interface',
                    confidence=0.95,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'typescript'}
                ))

            # Extract types
            type_pattern = r'type\s+(\w+)\s*='
            for match in re.finditer(type_pattern, content):
                type_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                context = self._get_context(lines, line_num - 1)

                entities.append(Entity(
                    name=type_name,
                    type='type',
                    confidence=0.90,
                    context=context,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'typescript'}
                ))

            # Extract classes and functions (similar to JS)
            entities.extend(self._extract_from_javascript(file_path))

        except Exception as e:
            logging.error(f"Error processing TypeScript file {file_path}: {e}")

        return entities

    def _extract_from_markdown(self, file_path: str) -> List[Entity]:
        """Extract entities from Markdown files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract headers as concepts
            header_pattern = r'^(#{1,6})\s+(.+)$'
            for match in re.finditer(header_pattern, content, re.MULTILINE):
                header_text = match.group(2).strip()
                line_num = content[:match.start()].count('\n') + 1

                entities.append(Entity(
                    name=header_text,
                    type='concept',
                    confidence=0.80,
                    context=header_text,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'markdown', 'level': len(match.group(1))}
                ))

            # Extract key terms from content
            entities.extend(self._extract_key_terms(content, file_path, 'markdown'))

        except Exception as e:
            logging.error(f"Error processing Markdown file {file_path}: {e}")

        return entities

    def _extract_from_text(self, file_path: str) -> List[Entity]:
        """Extract entities from plain text files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract key terms
            entities.extend(self._extract_key_terms(content, file_path, 'text'))

        except Exception as e:
            logging.error(f"Error processing text file {file_path}: {e}")

        return entities

    def _extract_from_json(self, file_path: str) -> List[Entity]:
        """Extract entities from JSON files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract keys as entities
            import json
            try:
                data = json.loads(content)
                keys = self._extract_json_keys(data, [])
                for key_path in keys:
                    entities.append(Entity(
                        name=key_path[-1],  # Last part of the key path
                        type='config_key',
                        confidence=0.70,
                        context='.'.join(key_path),
                        file_path=file_path,
                        line_number=1,  # JSON doesn't have meaningful line numbers
                        metadata={'language': 'json', 'key_path': key_path}
                    ))
            except json.JSONDecodeError:
                pass

        except Exception as e:
            logging.error(f"Error processing JSON file {file_path}: {e}")

        return entities

    def _extract_from_yaml(self, file_path: str) -> List[Entity]:
        """Extract entities from YAML files."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Simple key extraction from YAML
            key_pattern = r'^(\s*)([\w\-]+):'
            for match in re.finditer(key_pattern, content, re.MULTILINE):
                key_name = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                indent_level = len(match.group(1))

                entities.append(Entity(
                    name=key_name,
                    type='config_key',
                    confidence=0.70,
                    context=key_name,
                    file_path=file_path,
                    line_number=line_num,
                    metadata={'language': 'yaml', 'indent_level': indent_level}
                ))

        except Exception as e:
            logging.error(f"Error processing YAML file {file_path}: {e}")

        return entities

    def _extract_from_generic(self, file_path: str) -> List[Entity]:
        """Extract entities from generic files using NLP."""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract key terms
            entities.extend(self._extract_key_terms(content, file_path, 'generic'))

        except Exception as e:
            logging.error(f"Error processing generic file {file_path}: {e}")

        return entities

    def _extract_key_terms(self, content: str, file_path: str, language: str) -> List[Entity]:
        """Extract key terms using NLP and pattern matching."""
        entities = []

        try:
            # Use SpaCy for NLP processing
            doc = self.nlp(content[:10000])  # Limit content length

            # Extract noun phrases and important terms
            for chunk in doc.noun_chunks:
                if len(chunk.text.strip()) > 3:  # Filter out very short terms
                    # Calculate confidence based on term characteristics
                    confidence = min(0.8, len(chunk.text.strip()) / 20)

                    entities.append(Entity(
                        name=chunk.text.strip(),
                        type='term',
                        confidence=confidence,
                        context=chunk.sent.text.strip()[:200],
                        file_path=file_path,
                        line_number=1,  # Approximate
                        metadata={'language': language, 'source': 'nlp'}
                    ))

            # Use NER if available
            if self.ner_pipeline:
                try:
                    ner_results = self.ner_pipeline(content[:2000])  # Limit for performance
                    for result in ner_results:
                        entities.append(Entity(
                            name=result['word'],
                            type=result['entity_group'].lower(),
                            confidence=result['score'],
                            context=content[max(0, result['start']-50):result['end']+50],
                            file_path=file_path,
                            line_number=1,
                            metadata={'language': language, 'source': 'ner'}
                        ))
                except Exception as e:
                    logging.warning(f"NER processing failed: {e}")

        except Exception as e:
            logging.error(f"Error extracting key terms: {e}")

        return entities

    def _extract_json_keys(self, data: Any, path: List[str]) -> List[List[str]]:
        """Recursively extract keys from JSON data."""
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = path + [key]
                keys.append(current_path)
                keys.extend(self._extract_json_keys(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                keys.extend(self._extract_json_keys(item, path + [str(i)]))

        return keys

    def _get_context(self, lines: List[str], line_index: int, context_lines: int = 2) -> str:
        """Get context around a line."""
        start = max(0, line_index - context_lines)
        end = min(len(lines), line_index + context_lines + 1)
        return '\n'.join(lines[start:end]).strip()

def main():
    """Test the entity extractor."""
    extractor = EntityExtractor()

    # Test with current file
    entities = extractor.extract_entities(__file__)

    print(f"Extracted {len(entities)} entities:")
    for entity in entities[:10]:  # Show first 10
        print(f"- {entity.name} ({entity.type}): {entity.confidence:.2f}")

if __name__ == "__main__":
    main()