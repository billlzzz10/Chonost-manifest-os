# 🤖 Agent Model Configuration
# กำหนดค่า Ollama models สำหรับแต่ละ Agent

class AgentModelConfig:
    """กำหนดค่า Ollama models สำหรับ AI Agent Ecosystem"""
    
    # Models ที่มีอยู่ในระบบ
    AVAILABLE_MODELS = {
        "deepseek-coder:6.7b-instruct": {
            "size": "3.8 GB",
            "strengths": ["coding", "debugging", "code review"],
            "best_for": ["Developer Agent", "QA_Agent"]
        },
        "llama3.1:8b": {
            "size": "4.9 GB", 
            "strengths": ["planning", "project management", "general reasoning"],
            "best_for": ["ProjectPlanner Agent"]
        },
        "qwen3:8b": {
            "size": "5.2 GB",
            "strengths": ["analysis", "risk assessment", "decision making"],
            "best_for": ["Guardian Agent"]
        },
        "deepseek-r1:7b": {
            "size": "4.7 GB",
            "strengths": ["text analysis", "risk assessment", "general tasks"],
            "best_for": ["Text Analysis", "Risk Assessment"]
        },
        "phi4:latest": {
            "size": "9.1 GB",
            "strengths": ["general purpose", "reasoning", "complex tasks"],
            "best_for": ["General Purpose", "Complex Analysis"]
        }
    }
    
    # การกำหนด Model ให้แต่ละ Agent
    AGENT_MODELS = {
        "project_planner": {
            "primary": "llama3.1:8b",
            "fallback": "deepseek-r1:7b",
            "reason": "เก่งในการวางแผนและจัดการโครงการ"
        },
        "guardian": {
            "primary": "qwen3:8b", 
            "fallback": "deepseek-r1:7b",
            "reason": "เก่งในการวิเคราะห์และประเมินความเสี่ยง"
        },
        "developer": {
            "primary": "deepseek-coder:6.7b-instruct",
            "fallback": "phi4:latest",
            "reason": "เก่งในการเขียนโค้ดและแก้ไขปัญหา"
        },
        "qa_agent": {
            "primary": "deepseek-coder:6.7b-instruct",
            "fallback": "llama3.1:8b", 
            "reason": "เก่งในการทดสอบและตรวจสอบคุณภาพโค้ด"
        }
    }
    
    @classmethod
    def get_agent_model(cls, agent_name: str) -> dict:
        """ดึงข้อมูล model สำหรับ Agent"""
        return cls.AGENT_MODELS.get(agent_name, {
            "primary": "llama3.1:8b",
            "fallback": "deepseek-r1:7b",
            "reason": "Default model"
        })
    
    @classmethod
    def list_available_models(cls) -> dict:
        """แสดงรายการ models ที่มีอยู่"""
        return cls.AVAILABLE_MODELS
    
    @classmethod
    def get_model_info(cls, model_name: str) -> dict:
        """ดึงข้อมูล model"""
        return cls.AVAILABLE_MODELS.get(model_name, {})
    
    @classmethod
    def validate_model(cls, model_name: str) -> bool:
        """ตรวจสอบว่า model มีอยู่หรือไม่"""
        return model_name in cls.AVAILABLE_MODELS

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    config = AgentModelConfig()
    
    print("🤖 Available Models:")
    for model, info in config.list_available_models().items():
        print(f"  - {model} ({info['size']})")
        print(f"    Strengths: {', '.join(info['strengths'])}")
        print(f"    Best for: {', '.join(info['best_for'])}")
        print()
    
    print("👥 Agent Model Assignments:")
    for agent, model_info in config.AGENT_MODELS.items():
        print(f"  - {agent}: {model_info['primary']}")
        print(f"    Reason: {model_info['reason']}")
        print(f"    Fallback: {model_info['fallback']}")
        print()
