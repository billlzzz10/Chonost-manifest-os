#!/usr/bin/env python3
"""
Ollama Client for File System MCP Chat App
โมดูลสำหรับเชื่อมต่อกับ Ollama server
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b-instruct"):
        """
        Initialize Ollama Client
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ Ollama server"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                logger.info("✅ เชื่อมต่อ Ollama server สำเร็จ")
                return True
            else:
                logger.error(f"❌ ไม่สามารถเชื่อมต่อ Ollama server: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}")
            return False
    
    def list_models(self) -> List[Dict]:
        """แสดงรายการโมดเดลที่มี"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"📋 พบโมดเดล {len(models)} รายการ")
                return models
            else:
                logger.error(f"❌ ไม่สามารถดึงรายการโมดเดล: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            return []
    
    def generate_response(self, prompt: str, system_prompt: str = None, **kwargs) -> Optional[str]:
        """
        สร้างคำตอบจาก Ollama
        
        Args:
            prompt: คำถามหรือข้อความ
            system_prompt: System prompt (ถ้ามี)
            **kwargs: ตัวเลือกเพิ่มเติม
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.info(f"🤖 ส่งคำถามไปยัง {self.model}")
            response = self.session.post(f"{self.base_url}/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '')
                logger.info(f"✅ ได้คำตอบจาก {self.model}")
                return answer
            else:
                logger.error(f"❌ ไม่สามารถสร้างคำตอบ: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้างคำตอบ: {str(e)}")
            return None
    
    def analyze_file_system(self, file_data: Dict, query: str) -> Optional[str]:
        """
        วิเคราะห์ข้อมูลไฟล์ระบบด้วย AI
        
        Args:
            file_data: ข้อมูลไฟล์ที่สแกนได้
            query: คำถามหรือคำสั่ง
        """
        # สร้าง system prompt สำหรับการวิเคราะห์ไฟล์ระบบ
        system_prompt = """คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์ไฟล์ระบบและโครงสร้างโปรเจค
คุณสามารถ:
- วิเคราะห์โครงสร้างไฟล์และโฟลเดอร์
- ให้คำแนะนำเกี่ยวกับการจัดการไฟล์
- ระบุไฟล์ที่อาจมีปัญหา
- อธิบายประเภทของโปรเจค
- ให้คำแนะนำในการปรับปรุงโครงสร้าง

กรุณาตอบเป็นภาษาไทยและให้คำแนะนำที่เป็นประโยชน์"""

        # สร้าง prompt สำหรับการวิเคราะห์
        analysis_prompt = f"""
ข้อมูลไฟล์ระบบ:
{json.dumps(file_data, indent=2, ensure_ascii=False)}

คำถาม/คำสั่ง: {query}

กรุณาวิเคราะห์และตอบคำถามข้างต้น
"""
        
        return self.generate_response(analysis_prompt, system_prompt)
    
    def generate_file_report(self, file_data: Dict) -> Optional[str]:
        """
        สร้างรายงานการวิเคราะห์ไฟล์ระบบ
        
        Args:
            file_data: ข้อมูลไฟล์ที่สแกนได้
        """
        system_prompt = """คุณเป็นผู้เชี่ยวชาญในการสร้างรายงานการวิเคราะห์ไฟล์ระบบ
กรุณาสร้างรายงานที่ครอบคลุมและเป็นประโยชน์ โดยรวมถึง:
- สรุปโครงสร้างโปรเจค
- ไฟล์ที่สำคัญ
- ปัญหาที่อาจพบ
- คำแนะนำในการปรับปรุง

กรุณาตอบเป็นภาษาไทยและจัดรูปแบบให้อ่านง่าย"""

        report_prompt = f"""
กรุณาสร้างรายงานการวิเคราะห์สำหรับข้อมูลไฟล์ระบบต่อไปนี้:

{json.dumps(file_data, indent=2, ensure_ascii=False)}

กรุณาสร้างรายงานที่ครอบคลุมและเป็นประโยชน์
"""
        
        return self.generate_response(report_prompt, system_prompt)
    
    def suggest_queries(self, file_data: Dict) -> Optional[str]:
        """
        แนะนำคำถามที่เหมาะสมสำหรับข้อมูลไฟล์
        
        Args:
            file_data: ข้อมูลไฟล์ที่สแกนได้
        """
        system_prompt = """คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์ไฟล์ระบบ
กรุณาแนะนำคำถามที่เหมาะสมสำหรับการวิเคราะห์ข้อมูลไฟล์ที่ให้มา
แนะนำคำถามที่:
- ช่วยเข้าใจโครงสร้างโปรเจค
- ระบุไฟล์ที่สำคัญ
- ค้นหาปัญหาที่อาจมี
- ให้คำแนะนำในการปรับปรุง

กรุณาตอบเป็นภาษาไทยและจัดรูปแบบให้อ่านง่าย"""

        suggestion_prompt = f"""
ข้อมูลไฟล์ระบบ:
{json.dumps(file_data, indent=2, ensure_ascii=False)}

กรุณาแนะนำคำถามที่เหมาะสมสำหรับการวิเคราะห์ข้อมูลนี้
"""
        
        return self.generate_response(suggestion_prompt, system_prompt)
    
    def explain_file_structure(self, file_data: Dict) -> Optional[str]:
        """
        อธิบายโครงสร้างไฟล์
        
        Args:
            file_data: ข้อมูลไฟล์ที่สแกนได้
        """
        system_prompt = """คุณเป็นผู้เชี่ยวชาญในการอธิบายโครงสร้างไฟล์และโปรเจค
กรุณาอธิบายโครงสร้างไฟล์ที่ให้มาในรูปแบบที่เข้าใจง่าย
รวมถึง:
- ประเภทของโปรเจค
- โครงสร้างโฟลเดอร์หลัก
- ไฟล์ที่สำคัญ
- ความสัมพันธ์ระหว่างไฟล์

กรุณาตอบเป็นภาษาไทยและใช้ภาษาที่เข้าใจง่าย"""

        explanation_prompt = f"""
กรุณาอธิบายโครงสร้างไฟล์ต่อไปนี้:

{json.dumps(file_data, indent=2, ensure_ascii=False)}

กรุณาอธิบายในรูปแบบที่เข้าใจง่าย
"""
        
        return self.generate_response(explanation_prompt, system_prompt)

class FileSystemAIAnalyzer:
    """คลาสสำหรับวิเคราะห์ไฟล์ระบบด้วย AI"""
    
    def __init__(self, model: str = "deepseek-coder:6.7b-instruct"):
        self.ollama = OllamaClient(model=model)
        self.connected = self.ollama.test_connection()
        
    def is_connected(self) -> bool:
        """ตรวจสอบการเชื่อมต่อ"""
        return self.connected
    
    def analyze_with_ai(self, file_data: Dict, query: str) -> Optional[str]:
        """
        วิเคราะห์ข้อมูลไฟล์ด้วย AI
        
        Args:
            file_data: ข้อมูลไฟล์
            query: คำถามหรือคำสั่ง
        """
        if not self.connected:
            return "❌ ไม่สามารถเชื่อมต่อกับ Ollama server ได้"
        
        return self.ollama.analyze_file_system(file_data, query)
    
    def generate_report(self, file_data: Dict) -> Optional[str]:
        """
        สร้างรายงานการวิเคราะห์
        
        Args:
            file_data: ข้อมูลไฟล์
        """
        if not self.connected:
            return "❌ ไม่สามารถเชื่อมต่อกับ Ollama server ได้"
        
        return self.ollama.generate_file_report(file_data)
    
    def get_suggestions(self, file_data: Dict) -> Optional[str]:
        """
        ได้คำแนะนำสำหรับการวิเคราะห์
        
        Args:
            file_data: ข้อมูลไฟล์
        """
        if not self.connected:
            return "❌ ไม่สามารถเชื่อมต่อกับ Ollama server ได้"
        
        return self.ollama.suggest_queries(file_data)
    
    def explain_structure(self, file_data: Dict) -> Optional[str]:
        """
        อธิบายโครงสร้างไฟล์
        
        Args:
            file_data: ข้อมูลไฟล์
        """
        if not self.connected:
            return "❌ ไม่สามารถเชื่อมต่อกับ Ollama server ได้"
        
        return self.ollama.explain_file_structure(file_data)

def test_ollama_connection():
    """ทดสอบการเชื่อมต่อ Ollama"""
    print("🔍 ทดสอบการเชื่อมต่อ Ollama...")
    
    # ทดสอบการเชื่อมต่อ
    client = OllamaClient()
    if client.test_connection():
        print("✅ เชื่อมต่อสำเร็จ!")
        
        # แสดงรายการโมดเดล
        models = client.list_models()
        if models:
            print("\n📋 โมดเดลที่มี:")
            for model in models:
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_mb = size / (1024 * 1024)
                print(f"  • {name} ({size_mb:.1f} MB)")
        
        # ทดสอบการสร้างคำตอบ
        print("\n🤖 ทดสอบการสร้างคำตอบ...")
        response = client.generate_response("สวัสดีครับ")
        if response:
            print(f"✅ คำตอบ: {response}")
        else:
            print("❌ ไม่สามารถสร้างคำตอบได้")
    else:
        print("❌ ไม่สามารถเชื่อมต่อได้")
        print("💡 ตรวจสอบว่า Ollama server กำลังทำงานอยู่")

if __name__ == "__main__":
    test_ollama_connection()
