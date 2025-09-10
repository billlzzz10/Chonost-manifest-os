# 🚀 CrewAI with Ollama Integration
# ตัวอย่างการใช้งาน CrewAI กับ Ollama models

import os
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from agent_model_config import AgentModelConfig

class CrewAIWithOllama:
    """CrewAI integration with Ollama models"""
    
    def __init__(self):
        self.config = AgentModelConfig()
        self.llms = {}
        self._setup_llms()
    
    def _setup_llms(self):
        """ตั้งค่า LLMs สำหรับแต่ละ model"""
        for model_name in self.config.AVAILABLE_MODELS.keys():
            try:
                self.llms[model_name] = Ollama(
                    model=model_name,
                    temperature=0.7,
                    top_p=0.9,
                    num_predict=2048
                )
                print(f"✅ Loaded model: {model_name}")
            except Exception as e:
                print(f"❌ Failed to load model {model_name}: {e}")
    
    def create_project_planner_agent(self):
        """สร้าง ProjectPlanner Agent"""
        model_config = self.config.get_agent_model("project_planner")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Project Planner',
            goal='วางแผนและแบ่งงานอย่างมีประสิทธิภาพตามกฎ 1-3-5',
            backstory="""คุณเป็นผู้เชี่ยวชาญในการจัดการโครงการที่มีประสบการณ์มากกว่า 10 ปี 
            คุณเข้าใจการแบ่งงานตามกฎ 1-3-5 และสามารถประเมินทรัพยากรได้อย่างแม่นยำ
            คุณใช้ model {model_config['primary']} สำหรับการวางแผน""",
            llm=llm,
            verbose=True,
            allow_delegation=True
        )
    
    def create_guardian_agent(self):
        """สร้าง Guardian Agent"""
        model_config = self.config.get_agent_model("guardian")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Guardian',
            goal='ป้องกันข้อมูลและจัดการความเสี่ยงอย่างต่อเนื่อง',
            backstory="""คุณเป็นผู้พิทักษ์ความปลอดภัยของระบบที่มีความระมัดระวังสูง 
            คุณตรวจสอบทุกการเปลี่ยนแปลงและแจ้งเตือนทันทีเมื่อพบความเสี่ยง
            คุณใช้ model {model_config['primary']} สำหรับการประเมินความเสี่ยง""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_developer_agent(self):
        """สร้าง Developer Agent"""
        model_config = self.config.get_agent_model("developer")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Developer',
            goal='พัฒนาโค้ดที่มีคุณภาพตามมาตรฐานที่กำหนด',
            backstory="""คุณเป็นนักพัฒนาที่มีประสบการณ์ในการเขียนโค้ดที่สะอาดและมีประสิทธิภาพ 
            คุณเข้าใจหลักการ Clean Code และสามารถสร้าง Feature Branch ได้อย่างถูกต้อง
            คุณใช้ model {model_config['primary']} สำหรับการพัฒนาโค้ด""",
            llm=llm,
            verbose=True,
            allow_delegation=True
        )
    
    def create_qa_agent(self):
        """สร้าง QA Agent"""
        model_config = self.config.get_agent_model("qa_agent")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='QA Engineer',
            goal='ประกันคุณภาพของโค้ดและสร้างรายงานการทดสอบ',
            backstory="""คุณเป็นผู้เชี่ยวชาญในการทดสอบที่มีความละเอียดอ่อนสูง 
            คุณสามารถค้นหา Bug และปัญหาคุณภาพได้อย่างแม่นยำ
            คุณใช้ model {model_config['primary']} สำหรับการทดสอบ""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_planning_task(self, issue_description: str):
        """สร้าง Task สำหรับการวางแผน"""
        return Task(
            description=f"""วิเคราะห์ GitHub Issue และสร้างแผนงาน:
            
            Issue Description: {issue_description}
            
            ขั้นตอน:
            1. แบ่งงานตามกฎ 1-3-5
            2. ประเมินเวลาและทรัพยากร
            3. สร้าง milestones
            4. กำหนดความเสี่ยง
            5. สร้างรายงานแผนงาน
            """,
            agent=self.create_project_planner_agent(),
            expected_output="แผนงานที่แบ่งย่อยพร้อม timeline และ risk assessment"
        )
    
    def create_development_task(self, planning_result: str):
        """สร้าง Task สำหรับการพัฒนา"""
        return Task(
            description=f"""พัฒนาโค้ดตามแผนงาน:
            
            Planning Result: {planning_result}
            
            ขั้นตอน:
            1. สร้าง Feature Branch
            2. เขียนโค้ดตามมาตรฐาน
            3. ทำ Unit Test
            4. Commit และ Push
            5. สร้างรายงานการพัฒนา
            """,
            agent=self.create_developer_agent(),
            expected_output="โค้ดที่พัฒนาเสร็จพร้อม test cases"
        )
    
    def create_testing_task(self, development_result: str):
        """สร้าง Task สำหรับการทดสอบ"""
        return Task(
            description=f"""ทดสอบโค้ดที่พัฒนา:
            
            Development Result: {development_result}
            
            ขั้นตอน:
            1. รัน Unit Tests
            2. ตรวจสอบ Code Coverage
            3. ทำ Integration Tests
            4. สร้างรายงาน Bug
            5. ประเมินคุณภาพโค้ด
            """,
            agent=self.create_qa_agent(),
            expected_output="รายงานการทดสอบและ Bug report"
        )
    
    def create_guardian_task(self, development_result: str, testing_result: str):
        """สร้าง Task สำหรับการตรวจสอบความเสี่ยง"""
        return Task(
            description=f"""ตรวจสอบความเสี่ยงของโค้ดใหม่:
            
            Development Result: {development_result}
            Testing Result: {testing_result}
            
            ขั้นตอน:
            1. วิเคราะห์การเปลี่ยนแปลง
            2. ประเมินความเสี่ยง
            3. สร้าง Backup ถ้าจำเป็น
            4. แจ้งเตือนถ้าพบความเสี่ยงสูง
            5. สร้างรายงานความปลอดภัย
            """,
            agent=self.create_guardian_agent(),
            expected_output="รายงานความเสี่ยงและคำแนะนำ"
        )
    
    def run_development_crew(self, issue_description: str):
        """รัน Development Crew"""
        print("🚀 Starting AI Agent Ecosystem...")
        print(f"📋 Issue: {issue_description}")
        print()
        
        # สร้าง Tasks
        planning_task = self.create_planning_task(issue_description)
        
        # สร้าง Crew
        crew = Crew(
            agents=[
                self.create_project_planner_agent(),
                self.create_guardian_agent(),
                self.create_developer_agent(),
                self.create_qa_agent()
            ],
            tasks=[planning_task],
            verbose=True,
            memory=True,
            cache=True
        )
        
        # รัน Crew
        print("🤖 Running AI Agents...")
        result = crew.kickoff()
        
        print("\n✅ Development Crew completed!")
        print(f"📊 Result: {result}")
        
        return result

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # สร้าง instance
    crew_ai = CrewAIWithOllama()
    
    # ตัวอย่าง Issue
    sample_issue = """
    สร้างระบบจัดการไฟล์ที่มีฟีเจอร์:
    - อัปโหลดไฟล์
    - ดาวน์โหลดไฟล์  
    - แชร์ไฟล์
    - จัดการสิทธิ์
    - ค้นหาไฟล์
    """
    
    # รัน Development Crew
    result = crew_ai.run_development_crew(sample_issue)
