"""
🎯 Integrated Chonost System
ระบบที่ผนวกรวมทุกฟีเจอร์เข้าด้วยกัน:
1. Enhanced RAG System
2. Advanced AI Agents
3. Manuscript Management
4. Real-time Collaboration
5. Analytics & Insights

Author: Assistant
"""
import asyncio
import json
import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import re
from pathlib import Path
import aiohttp
import aiofiles
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from sentence_transformers import SentenceTransformer
import faiss
import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import seaborn as sns
import websockets
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chonost_integrated.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & DATA STRUCTURES
# =============================================================================

class AgentType(Enum):
    """ประเภทของ AI Agents"""
    BACKGROUND = "background"  # Fast/Local processing
    INLINE_EDITOR = "inline_editor"  # On-demand refinement
    ASSISTANT_CHAT = "assistant_chat"  # Deep/collaborative
    CHARACTER_ANALYZER = "character_analyzer"
    PLOT_ANALYZER = "plot_analyzer"
    WRITING_ASSISTANT = "writing_assistant"
    RAG_ENGINE = "rag_engine"


class TaskPriority(Enum):
    """ระดับความสำคัญของงาน"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """สถานะของงาน"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """โครงสร้างข้อมูลงาน"""
    id: str
    title: str
    description: str
    agent_type: AgentType
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None


@dataclass
class Manuscript:
    """โครงสร้างข้อมูล Manuscript"""
    id: str
    title: str
    content: str
    characters: List[str] = field(default_factory=list)
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[np.ndarray] = None


@dataclass
class Character:
    """โครงสร้างข้อมูลตัวละคร"""
    id: str
    name: str
    description: str
    personality: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    appearances: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """โครงสร้างข้อมูลผู้ใช้"""
    id: str
    username: str
    email: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


# =============================================================================
# INTEGRATED SYSTEM CORE
# =============================================================================

class IntegratedChonostSystem:
    """
    ระบบหลักที่ผนวกรวมทุกฟีเจอร์เข้าด้วยกัน
    """
    
    def __init__(self, db_path: str = "chonost_integrated.db"):
        self.db_path = db_path
        self.initialize_database()
        
        # Initialize AI components
        self.openai_client = openai
        self.openai_client.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.embedding_model = None
        
        # Initialize vector store
        self.vector_store = None
        self.initialize_vector_store()
        
        # Task queue for background processing
        self.task_queue = asyncio.Queue()
        self.running_tasks = {}
        
        # Start background workers
        self.start_background_workers()
        
        logger.info("Integrated Chonost System initialized successfully")
    
    def initialize_database(self):
        """สร้างฐานข้อมูล SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Manuscripts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manuscripts (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT NOT NULL,
                content TEXT,
                characters TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                manuscript_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                personality TEXT,
                relationships TEXT,
                appearances TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manuscript_id) REFERENCES manuscripts (id)
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                agent_type TEXT NOT NULL,
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                metadata TEXT,
                result TEXT
            )
        ''')
        
        # Embeddings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def initialize_vector_store(self):
        """สร้าง Vector Store สำหรับ RAG"""
        try:
            # สร้าง FAISS index สำหรับ embeddings
            dimension = 384  # สำหรับ all-MiniLM-L6-v2
            self.vector_store = faiss.IndexFlatIP(dimension)
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize vector store: {e}")
    
    def start_background_workers(self):
        """เริ่มต้น background workers"""
        def run_background_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.background_worker())
        
        worker_thread = threading.Thread(target=run_background_worker, daemon=True)
        worker_thread.start()
        logger.info("Background workers started")
    
    async def background_worker(self):
        """Background worker สำหรับประมวลผลงาน"""
        while True:
            try:
                task = await self.task_queue.get()
                await self.process_task(task)
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Error in background worker: {e}")
                await asyncio.sleep(1)
    
    async def process_task(self, task: Task):
        """ประมวลผลงาน"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
            
            if task.agent_type == AgentType.BACKGROUND:
                result = await self.process_background_task(task)
            elif task.agent_type == AgentType.INLINE_EDITOR:
                result = await self.process_inline_editor_task(task)
            elif task.agent_type == AgentType.ASSISTANT_CHAT:
                result = await self.process_assistant_chat_task(task)
            elif task.agent_type == AgentType.CHARACTER_ANALYZER:
                result = await self.process_character_analysis_task(task)
            elif task.agent_type == AgentType.PLOT_ANALYZER:
                result = await self.process_plot_analysis_task(task)
            elif task.agent_type == AgentType.WRITING_ASSISTANT:
                result = await self.process_writing_assistant_task(task)
            elif task.agent_type == AgentType.RAG_ENGINE:
                result = await self.process_rag_task(task)
            else:
                raise ValueError(f"Unknown agent type: {task.agent_type}")
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now()
            
            # บันทึกผลลัพธ์ลงฐานข้อมูล
            self.save_task_result(task)
            
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            task.updated_at = datetime.now()
            self.save_task_result(task)
    
    async def process_background_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Background Agent (Fast/Local)"""
        content = task.metadata.get('content', '')
        
        # NER และ Sentiment Analysis
        entities = self.extract_entities(content)
        sentiment = self.analyze_sentiment(content)
        
        # สร้าง embeddings
        if self.embedding_model:
            embedding = self.embedding_model.encode(content)
            self.save_embedding(f"manuscript_{task.metadata.get('manuscript_id')}", embedding)
        
        return {
            "entities": entities,
            "sentiment": sentiment,
            "word_count": len(content.split()),
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_inline_editor_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Inline Editor (On-demand/Refinement)"""
        content = task.metadata.get('content', '')
        action = task.metadata.get('action', 'improve')
        
        # ดึง context จาก RAG
        context = await self.retrieve_context(content)
        
        # สร้าง prompt
        prompt = self.create_refinement_prompt(content, action, context)
        
        # เรียก AI API
        response = await self.call_ai_api(prompt, model="gpt-3.5-turbo")
        
        return {
            "suggestion": response,
            "context_used": context,
            "action": action,
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_assistant_chat_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Assistant Chat (Deep/Collaborative)"""
        question = task.metadata.get('question', '')
        user_id = task.metadata.get('user_id', '')
        
        # ดึงข้อมูลจาก Knowledge Hub
        context = await self.retrieve_deep_context(question, user_id)
        
        # สร้าง prompt
        prompt = self.create_analysis_prompt(question, context)
        
        # เรียก AI API
        response = await self.call_ai_api(prompt, model="gpt-4")
        
        return {
            "answer": response,
            "context_used": context,
            "confidence": 0.85,
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_character_analysis_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Character Analysis"""
        content = task.metadata.get('content', '')
        
        # วิเคราะห์ตัวละคร
        characters = self.extract_characters(content)
        relationships = self.analyze_relationships(characters, content)
        development = self.analyze_character_development(characters, content)
        
        return {
            "characters": characters,
            "relationships": relationships,
            "development": development,
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_plot_analysis_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Plot Analysis"""
        content = task.metadata.get('content', '')
        
        # วิเคราะห์โครงเรื่อง
        plot_structure = self.analyze_plot_structure(content)
        themes = self.extract_themes(content)
        pacing = self.analyze_pacing(content)
        
        return {
            "plot_structure": plot_structure,
            "themes": themes,
            "pacing": pacing,
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_writing_assistant_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน Writing Assistant"""
        content = task.metadata.get('content', '')
        request_type = task.metadata.get('type', 'improve')
        
        # ผู้ช่วยการเขียน
        if request_type == 'improve':
            result = await self.improve_content(content)
        elif request_type == 'continue':
            result = await self.continue_content(content)
        elif request_type == 'suggest':
            result = await self.suggest_improvements(content)
        else:
            result = await self.improve_content(content)
        
        return {
            "result": result,
            "type": request_type,
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_rag_task(self, task: Task) -> Dict[str, Any]:
        """ประมวลผลงาน RAG Engine"""
        query = task.metadata.get('query', '')
        
        # ค้นหาจาก Vector Store
        if self.vector_store and self.embedding_model:
            query_embedding = self.embedding_model.encode(query)
            results = self.search_vector_store(query_embedding, k=5)
        else:
            results = self.search_database(query)
        
        return {
            "results": results,
            "query": query,
            "processed_at": datetime.now().isoformat()
        }
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def extract_entities(self, text: str) -> List[str]:
        """สกัด entities จากข้อความ"""
        # ใช้ regex pattern สำหรับชื่อคน
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        return list(set(names))
    
    def analyze_sentiment(self, text: str) -> str:
        """วิเคราะห์ sentiment ของข้อความ"""
        # ใช้คำที่บ่งบอก sentiment
        positive_words = ['ดี', 'ดีใจ', 'สุข', 'รัก', 'ชอบ', 'สนุก', 'ดีใจ']
        negative_words = ['เสียใจ', 'เศร้า', 'โกรธ', 'เกลียด', 'ไม่ชอบ', 'แย่']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """สกัดข้อมูลตัวละคร"""
        characters = []
        names = self.extract_entities(text)
        
        for name in names:
            # หาข้อมูลเพิ่มเติมเกี่ยวกับตัวละคร
            description = self.find_character_description(text, name)
            personality = self.extract_personality_traits(text, name)
            
            characters.append({
                "name": name,
                "description": description,
                "personality": personality,
                "appearances": self.count_appearances(text, name)
            })
        
        return characters
    
    def find_character_description(self, text: str, name: str) -> str:
        """หาคำอธิบายตัวละคร"""
        # ค้นหาประโยคที่มีชื่อตัวละคร
        sentences = text.split('.')
        for sentence in sentences:
            if name in sentence:
                return sentence.strip()
        return ""
    
    def extract_personality_traits(self, text: str, name: str) -> List[str]:
        """สกัดบุคลิกภาพของตัวละคร"""
        traits = []
        personality_words = ['ใจดี', 'โกรธง่าย', 'ฉลาด', 'ขี้เกียจ', 'ขยัน', 'ใจเย็น']
        
        # ค้นหาประโยคที่มีชื่อตัวละครและคำที่บ่งบอกบุคลิกภาพ
        sentences = text.split('.')
        for sentence in sentences:
            if name in sentence:
                for trait in personality_words:
                    if trait in sentence:
                        traits.append(trait)
        
        return list(set(traits))
    
    def count_appearances(self, text: str, name: str) -> int:
        """นับจำนวนครั้งที่ตัวละครปรากฏ"""
        return text.count(name)
    
    def analyze_relationships(self, characters: List[Dict], text: str) -> List[Dict]:
        """วิเคราะห์ความสัมพันธ์ระหว่างตัวละคร"""
        relationships = []
        
        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters):
                if i != j:
                    # ค้นหาประโยคที่มีทั้งสองตัวละคร
                    sentences = text.split('.')
                    for sentence in sentences:
                        if char1['name'] in sentence and char2['name'] in sentence:
                            relationship_type = self.classify_relationship(sentence)
                            relationships.append({
                                "character1": char1['name'],
                                "character2": char2['name'],
                                "type": relationship_type,
                                "context": sentence.strip()
                            })
        
        return relationships
    
    def classify_relationship(self, sentence: str) -> str:
        """จำแนกประเภทความสัมพันธ์"""
        if any(word in sentence for word in ['รัก', 'ชอบ', 'ดีใจ']):
            return "romantic"
        elif any(word in sentence for word in ['เพื่อน', 'สนิท']):
            return "friendship"
        elif any(word in sentence for word in ['พ่อ', 'แม่', 'ลูก']):
            return "family"
        elif any(word in sentence for word in ['ศัตรู', 'เกลียด', 'โกรธ']):
            return "enemy"
        else:
            return "neutral"
    
    def analyze_character_development(self, characters: List[Dict], text: str) -> Dict[str, Any]:
        """วิเคราะห์การพัฒนาตัวละคร"""
        development = {}
        
        for character in characters:
            name = character['name']
            # วิเคราะห์การเปลี่ยนแปลงของตัวละคร
            development[name] = {
                "growth": self.analyze_growth(text, name),
                "challenges": self.find_challenges(text, name),
                "arc": self.determine_character_arc(text, name)
            }
        
        return development
    
    def analyze_growth(self, text: str, name: str) -> str:
        """วิเคราะห์การเติบโตของตัวละคร"""
        growth_indicators = ['เรียนรู้', 'พัฒนา', 'เติบโต', 'เปลี่ยน', 'เข้าใจ']
        for indicator in growth_indicators:
            if indicator in text and name in text:
                return "positive"
        return "stable"
    
    def find_challenges(self, text: str, name: str) -> List[str]:
        """หาความท้าทายของตัวละคร"""
        challenges = []
        challenge_words = ['ปัญหา', 'ยาก', 'ท้าทาย', 'อุปสรรค', 'ความกลัว']
        
        sentences = text.split('.')
        for sentence in sentences:
            if name in sentence:
                for word in challenge_words:
                    if word in sentence:
                        challenges.append(sentence.strip())
        
        return challenges
    
    def determine_character_arc(self, text: str, name: str) -> str:
        """กำหนด character arc"""
        # วิเคราะห์จากเนื้อหาทั้งหมด
        if self.analyze_growth(text, name) == "positive":
            return "growth"
        elif len(self.find_challenges(text, name)) > 0:
            return "struggle"
        else:
            return "static"
    
    def analyze_plot_structure(self, text: str) -> Dict[str, Any]:
        """วิเคราะห์โครงเรื่อง"""
        # แบ่งเป็น acts
        paragraphs = text.split('\n\n')
        total_paragraphs = len(paragraphs)
        
        act1_end = total_paragraphs // 4
        act2_end = total_paragraphs // 2
        act3_end = total_paragraphs * 3 // 4
        
        return {
            "act1": {
                "start": 0,
                "end": act1_end,
                "content": paragraphs[:act1_end]
            },
            "act2": {
                "start": act1_end,
                "end": act2_end,
                "content": paragraphs[act1_end:act2_end]
            },
            "act3": {
                "start": act2_end,
                "end": act3_end,
                "content": paragraphs[act2_end:act3_end]
            },
            "act4": {
                "start": act3_end,
                "end": total_paragraphs,
                "content": paragraphs[act3_end:]
            }
        }
    
    def extract_themes(self, text: str) -> List[str]:
        """สกัดธีมจากเนื้อหา"""
        themes = []
        theme_indicators = {
            "ความรัก": ["รัก", "หัวใจ", "ความรู้สึก"],
            "การเติบโต": ["เรียนรู้", "พัฒนา", "เติบโต"],
            "การต่อสู้": ["ต่อสู้", "สู้", "ท้าทาย"],
            "มิตรภาพ": ["เพื่อน", "มิตร", "สนิท"],
            "ครอบครัว": ["พ่อ", "แม่", "ลูก", "ครอบครัว"]
        }
        
        for theme, indicators in theme_indicators.items():
            if any(indicator in text for indicator in indicators):
                themes.append(theme)
        
        return themes
    
    def analyze_pacing(self, text: str) -> str:
        """วิเคราะห์จังหวะของเรื่อง"""
        # วิเคราะห์จากความยาวของประโยค
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if avg_sentence_length < 10:
            return "fast"
        elif avg_sentence_length < 20:
            return "medium"
        else:
            return "slow"
    
    async def retrieve_context(self, content: str) -> List[str]:
        """ดึง context จาก RAG system"""
        if self.embedding_model and self.vector_store:
            embedding = self.embedding_model.encode(content)
            results = self.search_vector_store(embedding, k=3)
            return [result['content'] for result in results]
        else:
            return []
    
    async def retrieve_deep_context(self, question: str, user_id: str) -> Dict[str, Any]:
        """ดึง context แบบลึกสำหรับ Assistant Chat"""
        # ดึงข้อมูลจาก Knowledge Hub
        user_data = self.get_user_data(user_id)
        user_manuscripts = self.get_user_manuscripts(user_id)
        user_feedback = self.get_user_feedback(user_id)
        
        return {
            "user_preferences": user_data.get('preferences', {}),
            "manuscripts": user_manuscripts,
            "feedback_history": user_feedback,
            "question": question
        }
    
    def create_refinement_prompt(self, content: str, action: str, context: List[str]) -> str:
        """สร้าง prompt สำหรับ Inline Editor"""
        context_text = "\n".join(context) if context else ""
        
        prompts = {
            "improve": f"ปรับปรุงเนื้อหาต่อไปนี้ให้น่าสนใจและลื่นไหลมากขึ้น:\n\n{content}\n\nContext:\n{context_text}",
            "continue": f"ต่อเติมเรื่องต่อไปนี้อย่างสมเหตุสมผล:\n\n{content}\n\nContext:\n{context_text}",
            "suggest": f"แนะนำการพัฒนาเรื่องราวต่อไปนี้:\n\n{content}\n\nContext:\n{context_text}",
            "grammar": f"ตรวจสอบและแก้ไขไวยากรณ์ของเนื้อหาต่อไปนี้:\n\n{content}"
        }
        
        return prompts.get(action, prompts["improve"])
    
    def create_analysis_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """สร้าง prompt สำหรับ Assistant Chat"""
        user_prefs = context.get('user_preferences', {})
        manuscripts = context.get('manuscripts', [])
        
        prompt = f"""
        คำถาม: {question}
        
        ข้อมูลผู้ใช้:
        - ความชอบ: {user_prefs}
        - จำนวน manuscripts: {len(manuscripts)}
        
        กรุณาตอบคำถามโดยใช้ข้อมูลที่มีอยู่และให้คำแนะนำที่เป็นประโยชน์
        """
        
        return prompt
    
    async def call_ai_api(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """เรียก AI API"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้ช่วยนักเขียนมืออาชีพ ให้คำแนะนำที่สร้างสรรค์และเป็นประโยชน์"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            return "ขออภัย ไม่สามารถประมวลผลได้ในขณะนี้"
    
    async def improve_content(self, content: str) -> str:
        """ปรับปรุงเนื้อหา"""
        prompt = f"ปรับปรุงเนื้อหาต่อไปนี้ให้น่าสนใจและลื่นไหลมากขึ้น:\n\n{content}"
        return await self.call_ai_api(prompt)
    
    async def continue_content(self, content: str) -> str:
        """ต่อเติมเนื้อหา"""
        prompt = f"ต่อเติมเรื่องต่อไปนี้อย่างสมเหตุสมผล:\n\n{content}"
        return await self.call_ai_api(prompt)
    
    async def suggest_improvements(self, content: str) -> str:
        """แนะนำการปรับปรุง"""
        prompt = f"แนะนำการพัฒนาเรื่องราวต่อไปนี้:\n\n{content}"
        return await self.call_ai_api(prompt)
    
    def search_vector_store(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """ค้นหาจาก Vector Store"""
        try:
            if self.vector_store is None:
                return []
            
            # ค้นหาใน FAISS index
            scores, indices = self.vector_store.search(query_embedding.reshape(1, -1), k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                # ดึงข้อมูลจากฐานข้อมูล
                content_data = self.get_content_by_index(idx)
                if content_data:
                    results.append({
                        "content": content_data['content'],
                        "score": float(score),
                        "type": content_data['type'],
                        "id": content_data['id']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def search_database(self, query: str) -> List[Dict[str, Any]]:
        """ค้นหาจากฐานข้อมูล"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ค้นหาใน manuscripts
        cursor.execute('''
            SELECT id, title, content FROM manuscripts 
            WHERE title LIKE ? OR content LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "type": "manuscript"
            })
        
        conn.close()
        return results
    
    def save_embedding(self, content_id: str, embedding: np.ndarray):
        """บันทึก embedding"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO embeddings (id, content_type, content_id, embedding)
                VALUES (?, ?, ?, ?)
            ''', (f"emb_{content_id}", "manuscript", content_id, embedding.tobytes()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving embedding: {e}")
    
    def get_content_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลจาก index"""
        # นี้เป็นตัวอย่าง ในการใช้งานจริงจะต้องมี mapping ระหว่าง index และ content
        return None
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """ดึงข้อมูลผู้ใช้"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "preferences": json.loads(row[3]) if row[3] else {},
                "created_at": row[4],
                "last_active": row[5]
            }
        else:
            return {}
    
    def get_user_manuscripts(self, user_id: str) -> List[Dict[str, Any]]:
        """ดึง manuscripts ของผู้ใช้"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM manuscripts WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        manuscripts = []
        for row in rows:
            manuscripts.append({
                "id": row[0],
                "title": row[2],
                "content": row[3],
                "characters": json.loads(row[4]) if row[4] else [],
                "word_count": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            })
        
        return manuscripts
    
    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """ดึง feedback ของผู้ใช้"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        feedback = []
        for row in rows:
            feedback.append({
                "id": row[0],
                "content_type": row[2],
                "content_id": row[3],
                "feedback_type": row[4],
                "feedback_data": json.loads(row[5]) if row[5] else {},
                "created_at": row[6]
            })
        
        return feedback
    
    def save_task_result(self, task: Task):
        """บันทึกผลลัพธ์งาน"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, result = ?, updated_at = ?
            WHERE id = ?
        ''', (task.status.value, json.dumps(task.result), task.updated_at.isoformat(), task.id))
        
        conn.commit()
        conn.close()
    
    # =============================================================================
    # PUBLIC API METHODS
    # =============================================================================
    
    async def submit_task(self, task: Task) -> str:
        """ส่งงานไปประมวลผล"""
        await self.task_queue.put(task)
        self.running_tasks[task.id] = task
        return task.id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """ดึงสถานะงาน"""
        task = self.running_tasks.get(task_id)
        if task:
            return {
                "id": task.id,
                "status": task.status.value,
                "result": task.result,
                "updated_at": task.updated_at.isoformat()
            }
        return None
    
    def create_manuscript(self, user_id: str, title: str, content: str) -> str:
        """สร้าง manuscript ใหม่"""
        manuscript_id = f"ms_{int(time.time())}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO manuscripts (id, user_id, title, content, word_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (manuscript_id, user_id, title, content, len(content.split())))
        
        conn.commit()
        conn.close()
        
        # สร้าง background task สำหรับประมวลผล
        task = Task(
            id=f"task_{int(time.time())}",
            title="Process new manuscript",
            description="Analyze and process new manuscript content",
            agent_type=AgentType.BACKGROUND,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"manuscript_id": manuscript_id, "content": content}
        )
        
        asyncio.create_task(self.submit_task(task))
        
        return manuscript_id
    
    def update_manuscript(self, manuscript_id: str, content: str) -> bool:
        """อัปเดต manuscript"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE manuscripts 
                SET content = ?, word_count = ?, updated_at = ?
                WHERE id = ?
            ''', (content, len(content.split()), datetime.now().isoformat(), manuscript_id))
            
            conn.commit()
            conn.close()
            
            # สร้าง task สำหรับประมวลผลใหม่
            task = Task(
                id=f"task_{int(time.time())}",
                title="Update manuscript analysis",
                description="Re-analyze updated manuscript content",
                agent_type=AgentType.BACKGROUND,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={"manuscript_id": manuscript_id, "content": content}
            )
            
            asyncio.create_task(self.submit_task(task))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating manuscript: {e}")
            return False
    
    def get_manuscript(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """ดึง manuscript"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM manuscripts WHERE id = ?', (manuscript_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "title": row[2],
                "content": row[3],
                "characters": json.loads(row[4]) if row[4] else [],
                "word_count": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "metadata": json.loads(row[8]) if row[8] else {}
            }
        else:
            return None


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# สร้าง global instance ของระบบ
integrated_system = IntegratedChonostSystem()

# Export สำหรับใช้งานใน routes
def get_integrated_system() -> IntegratedChonostSystem:
    """ดึง global instance ของระบบ"""
    return integrated_system
