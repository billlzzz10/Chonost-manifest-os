"""
Enhanced AI Agents System for Chonost

This module provides enhanced AI functionality including:
- Advanced model selection with local models
- Feedback loop and learning from mistakes
- Context-aware error handling
- User preference learning
- Block text data management
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import pickle

import openai
import anthropic
from litellm import completion
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import numpy as np

from src.config.settings import settings

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Enhanced types of user intents"""
    CREATIVE_WRITING = "creative_writing"
    CHARACTER_ANALYSIS = "character_analysis"
    PLOT_DEVELOPMENT = "plot_development"
    RESEARCH = "research"
    EDITING = "editing"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    GENERAL_QUERY = "general_query"
    ERROR_CORRECTION = "error_correction"
    CONTEXT_LEARNING = "context_learning"
    USER_PREFERENCE = "user_preference"

class ModelType(Enum):
    """Enhanced available AI models including local alternatives"""
    # Local models (Ollama alternatives)
    LOCAL_PHI3_MINI = "phi3-mini"
    LOCAL_MISTRAL_7B = "mistral-7b"
    LOCAL_DEEPSEEK_7B = "deepseek-7b"
    LOCAL_PHI4_MINI = "phi4-mini"
    
    # Specialized local models
    LOCAL_NER = "local_ner"
    LOCAL_SENTIMENT = "local_sentiment"
    LOCAL_EMBEDDING = "local_embedding"
    LOCAL_CODE_GENERATION = "local_code_generation"
    
    # Cloud models
    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35 = "gpt-3.5-turbo"
    ANTHROPIC_CLAUDE = "claude-3-sonnet-20240229"
    ANTHROPIC_CLAUDE_OPUS = "claude-3-opus-20240229"

class ErrorType(Enum):
    """Types of errors for learning"""
    GRAMMAR_ERROR = "grammar_error"
    LOGIC_ERROR = "logic_error"
    CONTEXT_ERROR = "context_error"
    STYLE_ERROR = "style_error"
    FACTUAL_ERROR = "factual_error"
    CODE_ERROR = "code_error"

@dataclass
class UserPreference:
    """User preference data"""
    user_id: str
    writing_style: str = "neutral"
    preferred_models: List[str] = field(default_factory=list)
    error_correction_style: str = "gentle"
    context_sensitivity: float = 0.7
    learning_rate: float = 0.1
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ErrorContext:
    """Error context for learning"""
    error_type: ErrorType
    original_text: str
    corrected_text: str
    context: Dict[str, Any]
    user_feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    model_used: str = ""
    confidence: float = 0.0

@dataclass
class BlockTextData:
    """Block text data structure"""
    content: str
    metadata: Dict[str, Any]
    embeddings: Optional[List[float]] = None
    context_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class AIRequest:
    """Enhanced AI request structure"""
    prompt: str
    intent: IntentType
    context: Optional[Dict[str, Any]] = None
    model_preference: Optional[ModelType] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    error_context: Optional[ErrorContext] = None
    block_text_data: Optional[BlockTextData] = None
    learning_mode: bool = False

@dataclass
class AIResponse:
    """Enhanced AI response structure"""
    content: str
    model_used: ModelType
    tokens_used: int
    latency_ms: float
    cost_estimate: float
    metadata: Dict[str, Any]
    confidence: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    error_corrections: List[Dict[str, Any]] = field(default_factory=list)

class LocalModelManager:
    """Manager for local AI models"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self._initialized = False
        self.model_configs = {
            ModelType.LOCAL_PHI3_MINI: {
                "path": "microsoft/Phi-3-mini-4k-instruct",
                "max_length": 4096,
                "device": "auto"
            },
            ModelType.LOCAL_MISTRAL_7B: {
                "path": "mistralai/Mistral-7B-Instruct-v0.2",
                "max_length": 8192,
                "device": "auto"
            },
            ModelType.LOCAL_DEEPSEEK_7B: {
                "path": "deepseek-ai/deepseek-coder-7b-instruct",
                "max_length": 8192,
                "device": "auto"
            }
        }
    
    async def initialize(self):
        """Initialize local models"""
        if self._initialized:
            return
        
        try:
            logger.info("Skipping local models initialization (using Azure models)")
            # logger.info("Initializing local models...")
            # 
            # # Initialize basic models
            # for model_type, config in self.model_configs.items():
            #     if torch.cuda.is_available():
            #         device = "cuda"
            #     elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            #         device = "mps"
            #     else:
            #         device = "cpu"
            #     
            #     logger.info(f"Loading {model_type.value} on {device}...")
            #     
            #     try:
            #         tokenizer = AutoTokenizer.from_pretrained(config["path"])
            #         model = AutoModelForCausalLM.from_pretrained(
            #             config["path"],
            #             torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            #             device_map=device if device != "cpu" else None,
            #             low_cpu_mem_usage=True
            #         )
            #         
            #         self.tokenizers[model_type] = tokenizer
            #         self.models[model_type] = model
            #         
            #         logger.info(f"Successfully loaded {model_type.value}")
            #         
            #     except Exception as e:
            #         logger.warning(f"Failed to load {model_type.value}: {e}")
            #         continue
            
            self._initialized = True
            logger.info("Azure models will be used instead of local models")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    async def generate_completion(self, model_type: ModelType, prompt: str, **kwargs) -> str:
        """Generate completion using local model"""
        if not self._initialized:
            await self.initialize()
        
        if model_type not in self.models:
            raise ValueError(f"Model {model_type.value} not available")
        
        model = self.models[model_type]
        tokenizer = self.tokenizers[model_type]
        
        # Prepare input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        if model.device.type != "cpu":
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new content
        return generated_text[len(prompt):].strip()

class FeedbackLoopSystem:
    """System for learning from mistakes and user feedback"""
    
    def __init__(self, db_path: str = "feedback_loop.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                original_text TEXT NOT NULL,
                corrected_text TEXT NOT NULL,
                context TEXT NOT NULL,
                user_feedback TEXT,
                timestamp TEXT NOT NULL,
                model_used TEXT NOT NULL,
                confidence REAL NOT NULL,
                user_id TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                writing_style TEXT NOT NULL,
                preferred_models TEXT NOT NULL,
                error_correction_style TEXT NOT NULL,
                context_sensitivity REAL NOT NULL,
                learning_rate REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS block_text_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                embeddings TEXT,
                context_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                user_id TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def record_error(self, error_context: ErrorContext, user_id: Optional[str] = None):
        """Record an error for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO error_contexts 
            (error_type, original_text, corrected_text, context, user_feedback, 
             timestamp, model_used, confidence, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            error_context.error_type.value,
            error_context.original_text,
            error_context.corrected_text,
            json.dumps(error_context.context),
            error_context.user_feedback,
            error_context.timestamp.isoformat(),
            error_context.model_used,
            error_context.confidence,
            user_id
        ))
        
        conn.commit()
        conn.close()
    
    async def get_similar_errors(self, text: str, error_type: ErrorType, limit: int = 5) -> List[ErrorContext]:
        """Get similar errors for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM error_contexts 
            WHERE error_type = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (error_type.value, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        errors = []
        for row in rows:
            errors.append(ErrorContext(
                error_type=ErrorType(row[1]),
                original_text=row[2],
                corrected_text=row[3],
                context=json.loads(row[4]),
                user_feedback=row[5],
                timestamp=datetime.fromisoformat(row[6]),
                model_used=row[7],
                confidence=row[8]
            ))
        
        return errors
    
    async def save_user_preference(self, preference: UserPreference):
        """Save user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences 
            (user_id, writing_style, preferred_models, error_correction_style, 
             context_sensitivity, learning_rate, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            preference.user_id,
            preference.writing_style,
            json.dumps(preference.preferred_models),
            preference.error_correction_style,
            preference.context_sensitivity,
            preference.learning_rate,
            preference.last_updated.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def get_user_preference(self, user_id: str) -> Optional[UserPreference]:
        """Get user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserPreference(
                user_id=row[0],
                writing_style=row[1],
                preferred_models=json.loads(row[2]),
                error_correction_style=row[3],
                context_sensitivity=row[4],
                learning_rate=row[5],
                last_updated=datetime.fromisoformat(row[6])
            )
        
        return None
    
    async def save_block_text_data(self, block_data: BlockTextData, user_id: Optional[str] = None):
        """Save block text data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO block_text_data 
            (content, metadata, embeddings, context_hash, created_at, updated_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            block_data.content,
            json.dumps(block_data.metadata),
            json.dumps(block_data.embeddings) if block_data.embeddings else None,
            block_data.context_hash,
            block_data.created_at.isoformat(),
            block_data.updated_at.isoformat(),
            user_id
        ))
        
        conn.commit()
        conn.close()

class EnhancedRouterAI:
    """Enhanced router for intelligent model selection with learning"""
    
    def __init__(self, feedback_system: FeedbackLoopSystem):
        self.feedback_system = feedback_system
        self.intent_model_mapping = {
            IntentType.CREATIVE_WRITING: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.CHARACTER_ANALYSIS: [
                ModelType.LOCAL_MISTRAL_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.PLOT_DEVELOPMENT: [
                ModelType.LOCAL_MISTRAL_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE_OPUS
            ],
            IntentType.RESEARCH: [
                ModelType.LOCAL_DEEPSEEK_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.EDITING: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT35, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.SUMMARIZATION: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT35, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.TRANSLATION: [
                ModelType.LOCAL_MISTRAL_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.CODE_GENERATION: [
                ModelType.LOCAL_DEEPSEEK_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.GENERAL_QUERY: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT35, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.ERROR_CORRECTION: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.CONTEXT_LEARNING: [
                ModelType.LOCAL_MISTRAL_7B, ModelType.OPENAI_GPT4, ModelType.ANTHROPIC_CLAUDE
            ],
            IntentType.USER_PREFERENCE: [
                ModelType.LOCAL_PHI3_MINI, ModelType.OPENAI_GPT35, ModelType.ANTHROPIC_CLAUDE
            ]
        }
        
        self.model_costs = {
            ModelType.LOCAL_PHI3_MINI: 0.0,
            ModelType.LOCAL_MISTRAL_7B: 0.0,
            ModelType.LOCAL_DEEPSEEK_7B: 0.0,
            ModelType.LOCAL_PHI4_MINI: 0.0,
            ModelType.OPENAI_GPT4: 0.03,
            ModelType.OPENAI_GPT35: 0.002,
            ModelType.ANTHROPIC_CLAUDE: 0.015,
            ModelType.ANTHROPIC_CLAUDE_OPUS: 0.075,
        }
    
    async def select_model(self, request: AIRequest) -> ModelType:
        """Select the best model considering user preferences and learning"""
        if request.model_preference:
            return request.model_preference
        
        # Get user preference if available
        user_preference = None
        if request.user_id:
            user_preference = await self.feedback_system.get_user_preference(request.user_id)
        
        # Get available models for this intent
        available_models = self.intent_model_mapping.get(request.intent, [ModelType.OPENAI_GPT4])
        
        # Consider user preferences
        if user_preference and user_preference.preferred_models:
            # Filter by user preferences
            preferred_models = [m for m in available_models if m.value in user_preference.preferred_models]
            if preferred_models:
                available_models = preferred_models
        
        # For now, prefer Azure models over local models
        azure_models = [m for m in available_models if m.value.startswith("gpt") or m.value.startswith("claude")]
        if azure_models:
            available_models = azure_models
        
        # Return the first available model (could be enhanced with more sophisticated selection)
        return available_models[0]

class EnhancedAIAgentSystem:
    """Enhanced AI agent system with learning capabilities"""
    
    def __init__(self):
        self.feedback_system = FeedbackLoopSystem()
        self.local_model_manager = LocalModelManager()
        self.router = EnhancedRouterAI(self.feedback_system)
        self.cloud_models = None  # Will be initialized when needed
        self._initialized = False
    
    async def initialize(self):
        """Initialize the enhanced AI agent system"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing Enhanced AI Agent System...")
            
            # Initialize local models
            await self.local_model_manager.initialize()
            
            self._initialized = True
            logger.info("Enhanced AI Agent System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced AI Agent System: {e}")
            raise
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process an AI request with learning capabilities"""
        if not self._initialized:
            await self.initialize()
        
        # Select the best model
        selected_model = await self.router.select_model(request)
        
        # Process with local models if applicable
        if selected_model.value.startswith("local"):
            return await self._process_local_request(request, selected_model)
        
        # Process with cloud models
        return await self._process_cloud_request(request, selected_model)
    
    async def _process_local_request(self, request: AIRequest, model: ModelType) -> AIResponse:
        """Process request using local models"""
        start_time = datetime.now()
        
        try:
            # Add learning context if available
            enhanced_prompt = await self._enhance_prompt_with_learning(request)
            
            # Generate completion
            content = await self.local_model_manager.generate_completion(
                model, enhanced_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Process error corrections if in learning mode
            if request.learning_mode and request.error_context:
                content = await self._apply_error_corrections(content, request.error_context)
            
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            return AIResponse(
                content=content,
                model_used=model,
                tokens_used=len(enhanced_prompt.split()),
                latency_ms=latency_ms,
                cost_estimate=0.0,
                metadata={"provider": "local", "learning_mode": request.learning_mode},
                confidence=0.8  # Local models typically have lower confidence
            )
            
        except Exception as e:
            logger.error(f"Error in local request processing: {e}")
            raise
    
    async def _process_cloud_request(self, request: AIRequest, model: ModelType) -> AIResponse:
        """Process request using cloud models"""
        start_time = datetime.now()
        
        try:
            # Add learning context if available
            enhanced_prompt = await self._enhance_prompt_with_learning(request)
            
            # Configure Azure OpenAI client
            import openai
            import os
            from dotenv import load_dotenv

            # Load .env file to ensure environment variables are available
            load_dotenv()
            
            # Get environment variables directly
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            
            if not api_key or not endpoint:
                raise ValueError("Missing Azure OpenAI credentials")
            
            client = openai.AzureOpenAI(
                api_key=api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=endpoint
            )
            
            # Map model types to Azure deployment names
            model_mapping = {
                ModelType.OPENAI_GPT4: "gpt-4.1-mini",
                ModelType.OPENAI_GPT35: "gpt-35-turbo",
                ModelType.ANTHROPIC_CLAUDE: "claude-3-sonnet-20240229",
                ModelType.ANTHROPIC_CLAUDE_OPUS: "claude-3-opus-20240229"
            }
            
            deployment_name = model_mapping.get(model, "gpt-4.1-mini")
            
            # Generate completion
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for manuscript writing and creative tasks."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Process error corrections if in learning mode
            if request.learning_mode and request.error_context:
                content = await self._apply_error_corrections(content, request.error_context)
            
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Estimate cost (rough calculation)
            cost_estimate = tokens_used * 0.00001  # Rough estimate
            
            return AIResponse(
                content=content,
                model_used=model,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cost_estimate=cost_estimate,
                metadata={"provider": "azure", "deployment": deployment_name, "learning_mode": request.learning_mode},
                confidence=0.9  # Azure models typically have higher confidence
            )
            
        except Exception as e:
            logger.error(f"Error in cloud request processing: {e}")
            raise
    
    async def _enhance_prompt_with_learning(self, request: AIRequest) -> str:
        """Enhance prompt with learning from previous errors"""
        enhanced_prompt = request.prompt
        
        if request.learning_mode and request.error_context:
            # Get similar errors for learning
            similar_errors = await self.feedback_system.get_similar_errors(
                request.error_context.original_text,
                request.error_context.error_type
            )
            
            if similar_errors:
                learning_context = "\n\nLearning from previous similar errors:\n"
                for error in similar_errors[:3]:  # Use top 3 similar errors
                    learning_context += f"- Original: {error.original_text}\n"
                    learning_context += f"  Corrected: {error.corrected_text}\n"
                    if error.user_feedback:
                        learning_context += f"  Feedback: {error.user_feedback}\n"
                
                enhanced_prompt = learning_context + "\n" + enhanced_prompt
        
        return enhanced_prompt
    
    async def _apply_error_corrections(self, content: str, error_context: ErrorContext) -> str:
        """Apply error corrections to content"""
        # This would implement intelligent error correction
        # based on the error context and learning
        return content
    
    async def record_error_for_learning(self, error_context: ErrorContext, user_id: Optional[str] = None):
        """Record an error for future learning"""
        await self.feedback_system.record_error(error_context, user_id)
    
    async def save_user_preference(self, preference: UserPreference):
        """Save user preference for personalized responses"""
        await self.feedback_system.save_user_preference(preference)
    
    async def save_block_text_data(self, block_data: BlockTextData, user_id: Optional[str] = None):
        """Save block text data for context management"""
        await self.feedback_system.save_block_text_data(block_data, user_id)

# Global instance
enhanced_ai_agent_system = EnhancedAIAgentSystem()
