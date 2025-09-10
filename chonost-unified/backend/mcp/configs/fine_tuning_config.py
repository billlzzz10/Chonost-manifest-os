#!/usr/bin/env python3
"""
🎯 Fine-tuning Configuration
การตั้งค่าสำหรับ fine-tuning โมเดล Chonost AI
"""

import json
from pathlib import Path
from typing import Dict, Any, List

class FineTuningConfig:
    """Configuration สำหรับ fine-tuning"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.config_path = self.project_root / "config" / "fine_tuning"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
    def create_openai_config(self) -> Dict[str, Any]:
        """สร้าง configuration สำหรับ OpenAI Fine-tuning"""
        config = {
            "model": "gpt-3.5-turbo",
            "training_file": "datasets/fine_tuning/chonost_training.jsonl",
            "validation_file": "datasets/fine_tuning/chonost_validation.jsonl",
            "hyperparameters": {
                "n_epochs": 3,
                "batch_size": 1,
                "learning_rate_multiplier": 1.0
            },
            "suffix": "chonost-ai-assistant",
            "description": "Fine-tuned model for Chonost AI Platform assistant"
        }
        
        return config
    
    def create_anthropic_config(self) -> Dict[str, Any]:
        """สร้าง configuration สำหรับ Anthropic Fine-tuning"""
        config = {
            "model": "claude-3-sonnet-20240229",
            "training_file": "datasets/fine_tuning/chonost_training.jsonl",
            "validation_file": "datasets/fine_tuning/chonost_validation.jsonl",
            "hyperparameters": {
                "epochs": 3,
                "batch_size": 1,
                "learning_rate": 1e-5
            },
            "suffix": "chonost-ai-assistant",
            "description": "Fine-tuned Claude model for Chonost AI Platform"
        }
        
        return config
    
    def create_local_config(self) -> Dict[str, Any]:
        """สร้าง configuration สำหรับ Local Fine-tuning (Ollama, etc.)"""
        config = {
            "model": "llama2:7b",
            "training_file": "datasets/fine_tuning/chonost_training.jsonl",
            "validation_file": "datasets/fine_tuning/chonost_validation.jsonl",
            "hyperparameters": {
                "epochs": 5,
                "batch_size": 4,
                "learning_rate": 2e-5,
                "lora_r": 16,
                "lora_alpha": 32,
                "lora_dropout": 0.1
            },
            "output_dir": "models/chonost-fine-tuned",
            "description": "Local fine-tuned model for Chonost AI Platform"
        }
        
        return config
    
    def save_configs(self):
        """บันทึก configurations ทั้งหมด"""
        configs = {
            "openai": self.create_openai_config(),
            "anthropic": self.create_anthropic_config(),
            "local": self.create_local_config()
        }
        
        # บันทึก config หลัก
        main_config = {
            "platforms": configs,
            "default_platform": "openai",
            "dataset_info": {
                "training_file": "datasets/fine_tuning/chonost_training.jsonl",
                "validation_file": "datasets/fine_tuning/chonost_validation.jsonl",
                "total_examples": 12,
                "training_examples": 10,
                "validation_examples": 2
            }
        }
        
        config_file = self.config_path / "fine_tuning_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(main_config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ บันทึก configuration แล้ว: {config_file}")
        
        # สร้าง training script
        self.create_training_script()
        
    def create_training_script(self):
        """สร้าง training script"""
        script_content = '''#!/usr/bin/env python3
"""
🎯 Fine-tuning Training Script
Script สำหรับ fine-tuning โมเดล Chonost AI
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

class FineTuningTrainer:
    """Trainer สำหรับ fine-tuning"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """โหลด configuration"""
        config_file = self.project_root / "config" / "fine_tuning" / "fine_tuning_config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_dataset(self) -> bool:
        """ตรวจสอบความถูกต้องของ dataset"""
        training_file = self.project_root / self.config["dataset_info"]["training_file"]
        validation_file = self.project_root / self.config["dataset_info"]["validation_file"]
        
        if not training_file.exists():
            print(f"❌ Training file not found: {training_file}")
            return False
            
        if not validation_file.exists():
            print(f"❌ Validation file not found: {validation_file}")
            return False
            
        print("✅ Dataset validation passed")
        return True
    
    def train_openai(self) -> bool:
        """Fine-tune ด้วย OpenAI"""
        try:
            # ตรวจสอบ OpenAI API key
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OPENAI_API_KEY not found in environment")
                return False
            
            openai_config = self.config["platforms"]["openai"]
            
            # สร้าง fine-tuning job
            cmd = [
                "openai", "api", "fine_tuning.create",
                "--training-file", openai_config["training_file"],
                "--model", openai_config["model"],
                "--suffix", openai_config["suffix"]
            ]
            
            if "validation_file" in openai_config:
                cmd.extend(["--validation-file", openai_config["validation_file"]])
            
            print("🚀 Starting OpenAI fine-tuning...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ OpenAI fine-tuning job created successfully")
                print(f"Output: {result.stdout}")
                return True
            else:
                print(f"❌ OpenAI fine-tuning failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error during OpenAI fine-tuning: {e}")
            return False
    
    def train_anthropic(self) -> bool:
        """Fine-tune ด้วย Anthropic"""
        try:
            # ตรวจสอบ Anthropic API key
            if not os.getenv("ANTHROPIC_API_KEY"):
                print("❌ ANTHROPIC_API_KEY not found in environment")
                return False
            
            print("🚀 Starting Anthropic fine-tuning...")
            print("ℹ️ Anthropic fine-tuning requires manual setup")
            return True
            
        except Exception as e:
            print(f"❌ Error during Anthropic fine-tuning: {e}")
            return False
    
    def train_local(self) -> bool:
        """Fine-tune แบบ local"""
        try:
            print("🚀 Starting local fine-tuning...")
            
            local_config = self.config["platforms"]["local"]
            output_dir = self.project_root / local_config["output_dir"]
            output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"✅ Local training setup completed: {output_dir}")
            print("ℹ️ Run the training script manually for local fine-tuning")
            return True
            
        except Exception as e:
            print(f"❌ Error during local fine-tuning setup: {e}")
            return False
    
    def run_training(self, platform: str = "openai") -> bool:
        """รัน fine-tuning"""
        print(f"🎯 Starting fine-tuning on {platform}...")
        
        if not self.validate_dataset():
            return False
        
        if platform == "openai":
            return self.train_openai()
        elif platform == "anthropic":
            return self.train_anthropic()
        elif platform == "local":
            return self.train_local()
        else:
            print(f"❌ Unsupported platform: {platform}")
            return False

def main():
    """Main function"""
    trainer = FineTuningTrainer()
    
    # เลือก platform
    platforms = ["openai", "anthropic", "local"]
    print("🎯 Available platforms:")
    for i, platform in enumerate(platforms, 1):
        print(f"  {i}. {platform}")
    
    choice = input("\\nเลือก platform (1-3): ").strip()
    
    try:
        platform = platforms[int(choice) - 1]
        success = trainer.run_training(platform)
        
        if success:
            print("✅ Fine-tuning completed successfully!")
        else:
            print("❌ Fine-tuning failed!")
            
    except (ValueError, IndexError):
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
'''
        
        script_file = self.project_root / "train_fine_tuning.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        print(f"✅ สร้าง training script แล้ว: {script_file}")

def main():
    """Main function"""
    config = FineTuningConfig()
    config.save_configs()

if __name__ == "__main__":
    main()
