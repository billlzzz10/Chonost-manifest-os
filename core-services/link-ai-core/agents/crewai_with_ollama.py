# 🚀 CrewAI with Ollama Integration
# An example of using CrewAI with Ollama models.

import os
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from agent_model_config import AgentModelConfig

class CrewAIWithOllama:
    """
    CrewAI integration with Ollama models.

    Attributes:
        config (AgentModelConfig): The agent model configuration.
        llms (dict): A dictionary of loaded Ollama models.
    """
    
    def __init__(self):
        """Initializes the CrewAIWithOllama class."""
        self.config = AgentModelConfig()
        self.llms = {}
        self._setup_llms()
    
    def _setup_llms(self):
        """Sets up the LLMs for each model."""
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
        """
        Creates a ProjectPlanner Agent.

        Returns:
            Agent: The ProjectPlanner Agent.
        """
        model_config = self.config.get_agent_model("project_planner")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Project Planner',
            goal='Plan and divide tasks efficiently according to the 1-3-5 rule',
            backstory="""You are an expert in project management with over 10 years of experience.
            You understand task division according to the 1-3-5 rule and can accurately assess resources.
            You use the {model_config['primary']} model for planning.""",
            llm=llm,
            verbose=True,
            allow_delegation=True
        )
    
    def create_guardian_agent(self):
        """
        Creates a Guardian Agent.

        Returns:
            Agent: The Guardian Agent.
        """
        model_config = self.config.get_agent_model("guardian")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Guardian',
            goal='Continuously protect data and manage risks',
            backstory="""You are a highly cautious system security guardian.
            You monitor all changes and provide immediate alerts upon discovering risks.
            You use the {model_config['primary']} model for risk assessment.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_developer_agent(self):
        """
        Creates a Developer Agent.

        Returns:
            Agent: The Developer Agent.
        """
        model_config = self.config.get_agent_model("developer")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='Developer',
            goal='Develop high-quality code according to specified standards',
            backstory="""You are a developer with experience in writing clean and efficient code.
            You understand the principles of Clean Code and can create Feature Branches correctly.
            You use the {model_config['primary']} model for code development.""",
            llm=llm,
            verbose=True,
            allow_delegation=True
        )
    
    def create_qa_agent(self):
        """
        Creates a QA Agent.

        Returns:
            Agent: The QA Agent.
        """
        model_config = self.config.get_agent_model("qa_agent")
        llm = self.llms.get(model_config["primary"])
        
        return Agent(
            role='QA Engineer',
            goal='Ensure code quality and create test reports',
            backstory="""You are a highly detail-oriented testing expert.
            You can accurately find bugs and quality issues.
            You use the {model_config['primary']} model for testing.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_planning_task(self, issue_description: str):
        """
        Creates a Task for planning.

        Args:
            issue_description (str): The description of the GitHub issue.

        Returns:
            Task: The planning task.
        """
        return Task(
            description=f"""Analyze the GitHub Issue and create a work plan:
            
            Issue Description: {issue_description}
            
            Steps:
            1. Divide tasks according to the 1-3-5 rule.
            2. Estimate time and resources.
            3. Create milestones.
            4. Define risks.
            5. Create a work plan report.
            """,
            agent=self.create_project_planner_agent(),
            expected_output="A detailed work plan with a timeline and risk assessment"
        )
    
    def create_development_task(self, planning_result: str):
        """
        Creates a Task for development.

        Args:
            planning_result (str): The result of the planning task.

        Returns:
            Task: The development task.
        """
        return Task(
            description=f"""Develop code according to the work plan:
            
            Planning Result: {planning_result}
            
            Steps:
            1. Create a Feature Branch.
            2. Write code according to standards.
            3. Write Unit Tests.
            4. Commit and Push.
            5. Create a development report.
            """,
            agent=self.create_developer_agent(),
            expected_output="Completed code with test cases"
        )
    
    def create_testing_task(self, development_result: str):
        """
        Creates a Task for testing.

        Args:
            development_result (str): The result of the development task.

        Returns:
            Task: The testing task.
        """
        return Task(
            description=f"""Test the developed code:
            
            Development Result: {development_result}
            
            Steps:
            1. Run Unit Tests.
            2. Check Code Coverage.
            3. Perform Integration Tests.
            4. Create a Bug report.
            5. Assess code quality.
            """,
            agent=self.create_qa_agent(),
            expected_output="A test report and Bug report"
        )
    
    def create_guardian_task(self, development_result: str, testing_result: str):
        """
        Creates a Task for risk assessment.

        Args:
            development_result (str): The result of the development task.
            testing_result (str): The result of the testing task.

        Returns:
            Task: The risk assessment task.
        """
        return Task(
            description=f"""Assess the risk of the new code:
            
            Development Result: {development_result}
            Testing Result: {testing_result}
            
            Steps:
            1. Analyze the changes.
            2. Assess the risks.
            3. Create a Backup if necessary.
            4. Alert if high risk is found.
            5. Create a security report.
            """,
            agent=self.create_guardian_agent(),
            expected_output="A risk report and recommendations"
        )
    
    def run_development_crew(self, issue_description: str):
        """
        Runs the Development Crew.

        Args:
            issue_description (str): The description of the GitHub issue.

        Returns:
            The result of the crew kickoff.
        """
        print("🚀 Starting AI Agent Ecosystem...")
        print(f"📋 Issue: {issue_description}")
        print()
        
        # Create Tasks
        planning_task = self.create_planning_task(issue_description)
        
        # Create Crew
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
        
        # Run Crew
        print("🤖 Running AI Agents...")
        result = crew.kickoff()
        
        print("\n✅ Development Crew completed!")
        print(f"📊 Result: {result}")
        
        return result

# Example usage
if __name__ == "__main__":
    # Create instance
    crew_ai = CrewAIWithOllama()
    
    # Example Issue
    sample_issue = """
    Create a file management system with the following features:
    - Upload file
    - Download file
    - Share file
    - Manage permissions
    - Search for files
    """
    
    # Run Development Crew
    result = crew_ai.run_development_crew(sample_issue)
