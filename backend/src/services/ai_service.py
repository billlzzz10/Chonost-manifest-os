import os
import openai
from typing import List, Dict, Any
import json

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE')
        )
        self.default_model = "gpt-4o-mini"
        self.max_tokens = 2000
        self.temperature = 0.7
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         model: str = None, 
                         max_tokens: int = None, 
                         temperature: float = None) -> Dict[str, Any]:
        """
        Generate AI response using OpenAI API
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            
        Returns:
            Dict containing response and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'metadata': {
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None,
                'metadata': None
            }
    
    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user intent from message
        """
        system_prompt = """
        คุณเป็น AI ที่ช่วยวิเคราะห์เจตนาของผู้ใช้จากข้อความ
        จำแนกเจตนาออกเป็นหมวดหมู่ต่อไปนี้:
        - general_chat: การสนทนาทั่วไป
        - document_request: ขอความช่วยเหลือเกี่ยวกับเอกสาร
        - data_analysis: การวิเคราะห์ข้อมูล
        - automation_request: ขอสร้าง automation หรือ workflow
        - connection_help: ขอความช่วยเหลือเกี่ยวกับการเชื่อมต่อบริการ
        - settings_change: ขอเปลี่ยนแปลงการตั้งค่า
        
        ตอบกลับในรูปแบบ JSON:
        {
            "intent": "หมวดหมู่เจตนา",
            "confidence": 0.95,
            "entities": ["entity1", "entity2"],
            "suggested_actions": ["action1", "action2"]
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = self.generate_response(messages, temperature=0.3)
        
        if response['success']:
            try:
                intent_data = json.loads(response['content'])
                return {
                    'success': True,
                    'intent': intent_data
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Failed to parse intent analysis',
                    'intent': {
                        'intent': 'general_chat',
                        'confidence': 0.5,
                        'entities': [],
                        'suggested_actions': []
                    }
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'intent': None
            }
    
    def generate_chat_response(self, conversation_history: List[Dict[str, str]], 
                              user_message: str,
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate contextual chat response
        """
        system_prompt = """
        คุณเป็น AI Assistant ที่ช่วยเหลือผู้ใช้ในการจัดการและเชื่อมต่อกับบริการต่างๆ ได้แก่:
        - Notion
        - Google Drive
        - Dropbox
        - n8n
        - Google Sheets
        - Google Docs
        - Make.com
        - Airtable
        - Obsidian
        - Miro
        - Milanote
        
        คุณสามารถช่วย:
        1. สร้างและจัดการเอกสาร
        2. วิเคราะห์ข้อมูล
        3. สร้าง automation และ workflow
        4. เชื่อมต่อบริการต่างๆ
        5. ให้คำแนะนำและแก้ไขปัญหา
        
        ตอบเป็นภาษาไทยและให้ข้อมูลที่เป็นประโยชน์และแม่นยำ
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.generate_response(messages)
    
    def suggest_automation(self, user_request: str) -> Dict[str, Any]:
        """
        Suggest automation workflows based on user request
        """
        system_prompt = """
        คุณเป็นผู้เชี่ยวชาญด้าน automation ที่ช่วยแนะนำ workflow สำหรับการเชื่อมต่อบริการต่างๆ
        
        วิเคราะห์คำขอของผู้ใช้และแนะนำ automation workflow ที่เหมาะสม
        ตอบกลับในรูปแบบ JSON:
        {
            "workflow_name": "ชื่อ workflow",
            "description": "คำอธิบาย workflow",
            "services": ["บริการที่ใช้"],
            "steps": [
                {
                    "step": 1,
                    "action": "การกระทำ",
                    "service": "บริการที่ใช้",
                    "description": "รายละเอียด"
                }
            ],
            "benefits": ["ประโยชน์ที่ได้รับ"],
            "complexity": "easy|medium|hard"
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        response = self.generate_response(messages, temperature=0.5)
        
        if response['success']:
            try:
                workflow_data = json.loads(response['content'])
                return {
                    'success': True,
                    'workflow': workflow_data
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Failed to parse workflow suggestion'
                }
        else:
            return response

# Global AI service instance
ai_service = AIService()

