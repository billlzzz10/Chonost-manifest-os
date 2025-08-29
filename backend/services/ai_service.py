import os
import json
from typing import List, Dict, Any, Optional
import openai
from datetime import datetime

class AIService:
    """
    AI Service สำหรับการผนวก LLM เข้ากับระบบ Chonost
    รองรับ OpenAI GPT models และสามารถขยายไปยัง models อื่นๆ ได้
    """
    
    def __init__(self):
        # ตั้งค่า OpenAI API
        openai.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        # Configuration สำหรับ models ต่างๆ
        self.models = {
            'character_analysis': 'gpt-3.5-turbo',
            'writing_assistant': 'gpt-3.5-turbo',
            'content_enhancement': 'gpt-4',
            'auto_completion': 'gpt-3.5-turbo'
        }
    
    def analyze_characters(self, content: str) -> Dict[str, Any]:
        """
        วิเคราะห์ตัวละครจากเนื้อหา
        """
        try:
            prompt = f"""
            วิเคราะห์ตัวละครจากเนื้อหาต่อไปนี้:

            {content}

            กรุณาระบุ:
            1. รายชื่อตัวละครทั้งหมด
            2. บุคลิกของแต่ละตัวละคร
            3. ความสัมพันธ์ระหว่างตัวละคร
            4. บทบาทของแต่ละตัวละคร (protagonist, antagonist, supporting)
            5. การพัฒนาตัวละคร (character development)

            ตอบกลับในรูปแบบ JSON เท่านั้น
            """
            
            response = openai.ChatCompletion.create(
                model=self.models['character_analysis'],
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญด้านการวิเคราะห์วรรณกรรมและตัวละคร ตอบเป็นภาษาไทยและให้ข้อมูลในรูปแบบ JSON"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            try:
                # พยายามแปลง response เป็น JSON
                analysis = json.loads(result)
            except json.JSONDecodeError:
                # หาก response ไม่ใช่ JSON ให้สร้าง structure พื้นฐาน
                analysis = {
                    "characters": self._extract_character_names(content),
                    "analysis_text": result,
                    "relationships": [],
                    "themes": []
                }
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": self._fallback_character_analysis(content)
            }
    
    def writing_assistant(self, content: str, request_type: str = "improve") -> Dict[str, Any]:
        """
        ผู้ช่วยการเขียน - ปรับปรุงเนื้อหา, แนะนำ, หรือต่อเติมเรื่อง
        """
        try:
            prompts = {
                "improve": f"ปรับปรุงเนื้อหาต่อไปนี้ให้น่าสนใจและลื่นไหลมากขึ้น:\n\n{content}",
                "continue": f"ต่อเติมเรื่องต่อไปนี้อย่างสมเหตุสมผล:\n\n{content}",
                "suggest": f"แนะนำการพัฒนาเรื่องราวต่อไปนี้:\n\n{content}",
                "grammar": f"ตรวจสอบและแก้ไขไวยากรณ์ของเนื้อหาต่อไปนี้:\n\n{content}"
            }
            
            prompt = prompts.get(request_type, prompts["improve"])
            
            response = openai.ChatCompletion.create(
                model=self.models['writing_assistant'],
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้ช่วยนักเขียนมืออาชีพ ให้คำแนะนำที่สร้างสรรค์และเป็นประโยชน์"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return {
                "success": True,
                "suggestion": response.choices[0].message.content,
                "request_type": request_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestion": self._fallback_writing_suggestion(content, request_type)
            }
    
    def auto_complete(self, content: str, cursor_position: int = None) -> Dict[str, Any]:
        """
        Auto-completion สำหรับการเขียน
        """
        try:
            # หาข้อความก่อนหน้า cursor
            if cursor_position:
                context = content[:cursor_position]
            else:
                context = content
            
            # ใช้ข้อความ 200 ตัวอักษรสุดท้ายเป็น context
            context = context[-200:] if len(context) > 200 else context
            
            prompt = f"ต่อเติมข้อความต่อไปนี้อย่างเป็นธรรมชาติ (ไม่เกิน 50 คำ):\n\n{context}"
            
            response = openai.ChatCompletion.create(
                model=self.models['auto_completion'],
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้ช่วยเขียนที่ต่อเติมข้อความอย่างเป็นธรรมชาติและสอดคล้องกับบริบท"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            completion = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "completion": completion,
                "context_length": len(context),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_completion": "..."
            }
    
    def enhance_content(self, content: str, enhancement_type: str = "general") -> Dict[str, Any]:
        """
        ปรับปรุงเนื้อหาด้วย AI ขั้นสูง
        """
        try:
            enhancement_prompts = {
                "general": "ปรับปรุงเนื้อหาให้น่าสนใจและมีคุณภาพมากขึ้น",
                "dialogue": "ปรับปรุงบทสนทนาให้เป็นธรรมชาติและมีชีวิตชีวามากขึ้น",
                "description": "ปรับปรุงการบรรยายให้มีภาพพจน์และสื่ออารมณ์ได้ดีขึ้น",
                "pacing": "ปรับจังหวะการเล่าเรื่องให้เหมาะสมและน่าติดตาม",
                "emotion": "เพิ่มความลึกทางอารมณ์และความรู้สึกให้กับเรื่องราว"
            }
            
            enhancement_instruction = enhancement_prompts.get(enhancement_type, enhancement_prompts["general"])
            
            prompt = f"""
            {enhancement_instruction}

            เนื้อหาต้นฉบับ:
            {content}

            กรุณาให้:
            1. เนื้อหาที่ปรับปรุงแล้ว
            2. คำอธิบายสั้นๆ ว่าปรับปรุงอะไรบ้าง
            3. คะแนนการปรับปรุง (1-10)
            """
            
            response = openai.ChatCompletion.create(
                model=self.models['content_enhancement'],
                messages=[
                    {"role": "system", "content": "คุณเป็นบรรณาธิการมืออาชีพที่เชี่ยวชาญในการปรับปรุงงานเขียน"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return {
                "success": True,
                "enhanced_content": response.choices[0].message.content,
                "enhancement_type": enhancement_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_content": content
            }
    
    def _extract_character_names(self, content: str) -> List[str]:
        """
        ฟังก์ชัน fallback สำหรับการหาชื่อตัวละคร
        """
        # รายชื่อทั่วไปที่อาจเป็นชื่อตัวละคร
        common_names = [
            'อิกนัส', 'ลิโอซานดร้า', 'เรน่า', 'อาร์ยา', 'เดวิด', 'มายา',
            'แอนนา', 'จอห์น', 'มาเรีย', 'ปีเตอร์', 'ซาร่า', 'ไมเคิล'
        ]
        
        found_names = []
        for name in common_names:
            if name in content:
                found_names.append(name)
        
        return found_names
    
    def _fallback_character_analysis(self, content: str) -> Dict[str, Any]:
        """
        การวิเคราะห์ตัวละครแบบ fallback
        """
        return {
            "characters": self._extract_character_names(content),
            "analysis": "การวิเคราะห์พื้นฐาน: พบตัวละครหลายตัวในเรื่อง",
            "confidence": 0.5
        }
    
    def _fallback_writing_suggestion(self, content: str, request_type: str) -> str:
        """
        คำแนะนำการเขียนแบบ fallback
        """
        suggestions = {
            "improve": "ลองเพิ่มรายละเอียดและอารมณ์ให้กับตัวละครมากขึ้น",
            "continue": "พิจารณาพัฒนาความขัดแย้งหรือเหตุการณ์ที่น่าสนใจต่อไป",
            "suggest": "อาจเพิ่มบทสนทนาหรือการกระทำที่แสดงบุคลิกตัวละคร",
            "grammar": "ตรวจสอบการใช้เครื่องหมายวรรคตอนและการสะกดคำ"
        }
        
        return suggestions.get(request_type, "ลองพัฒนาเรื่องราวให้น่าสนใจมากขึ้น")

