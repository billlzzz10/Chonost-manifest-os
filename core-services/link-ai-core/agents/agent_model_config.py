# 🤖 Agent Model Configuration
# Sets Ollama models for each agent.

class AgentModelConfig:
    """
    Sets Ollama models for the AI Agent Ecosystem.

    Attributes:
        AVAILABLE_MODELS (dict): A dictionary of available models in the system.
        AGENT_MODELS (dict): A dictionary mapping agents to their models.
    """
    
    # Models available in the system
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
    
    # Assigning models to each agent
    AGENT_MODELS = {
        "project_planner": {
            "primary": "llama3.1:8b",
            "fallback": "deepseek-r1:7b",
            "reason": "Excels at planning and project management"
        },
        "guardian": {
            "primary": "qwen3:8b", 
            "fallback": "deepseek-r1:7b",
            "reason": "Excels at analysis and risk assessment"
        },
        "developer": {
            "primary": "deepseek-coder:6.7b-instruct",
            "fallback": "phi4:latest",
            "reason": "Excels at writing code and debugging"
        },
        "qa_agent": {
            "primary": "deepseek-coder:6.7b-instruct",
            "fallback": "llama3.1:8b", 
            "reason": "Excels at testing and code quality assurance"
        }
    }
    
    @classmethod
    def get_agent_model(cls, agent_name: str) -> dict:
        """
        Gets the model information for an agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            dict: A dictionary containing the model information.
        """
        return cls.AGENT_MODELS.get(agent_name, {
            "primary": "llama3.1:8b",
            "fallback": "deepseek-r1:7b",
            "reason": "Default model"
        })
    
    @classmethod
    def list_available_models(cls) -> dict:
        """
        Lists the available models.

        Returns:
            dict: A dictionary of available models.
        """
        return cls.AVAILABLE_MODELS
    
    @classmethod
    def get_model_info(cls, model_name: str) -> dict:
        """
        Gets information about a model.

        Args:
            model_name (str): The name of the model.

        Returns:
            dict: A dictionary containing the model information.
        """
        return cls.AVAILABLE_MODELS.get(model_name, {})
    
    @classmethod
    def validate_model(cls, model_name: str) -> bool:
        """
        Validates if a model exists.

        Args:
            model_name (str): The name of the model.

        Returns:
            bool: True if the model exists, False otherwise.
        """
        return model_name in cls.AVAILABLE_MODELS

# Example usage
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
