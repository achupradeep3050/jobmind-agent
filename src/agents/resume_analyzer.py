"""
Resume Analyzer Agent
Analyzes the user's resume text and extracts structured information.
"""

from crewai import Agent
from config import AGENT_VERBOSE, DEFAULT_MODEL
from utils.prompts import (
    RESUME_ANALYZER_ROLE,
    RESUME_ANALYZER_GOAL,
    RESUME_ANALYZER_BACKSTORY,
    RESUME_ANALYZER_FORMAT
)


class ResumeAnalyzerAgent:
    """
    Agent responsible for parsing and extracting key information from resumes.
    
    This agent takes raw resume text and structures it into meaningful categories
    like skills, experience, education, and achievements. It's the foundation
    of our analysis pipeline.
    """
    
    def __init__(self, llm):
        """
        Initialize the Resume Analyzer Agent.
        
        Args:
            llm: The LLM instance to use for reasoning (passed from crew setup)
        """
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create and configure the CrewAI agent with role, goal, and backstory.
        
        Returns:
            Agent: Configured CrewAI agent instance
        """
        return Agent(
            role=RESUME_ANALYZER_ROLE,
            goal=RESUME_ANALYZER_GOAL,
            backstory=RESUME_ANALYZER_BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,  # This agent works alone
            memory=True,  # Retain context during conversation
        )
    
    def analyze(self, resume_text: str) -> str:
        """
        Analyze a resume and return structured findings.
        
        Args:
            resume_text: The raw text content of the resume
            
        Returns:
            str: Structured analysis with extracted resume information
            
        Raises:
            Exception: If analysis fails
        """
        # Build the task prompt with format instructions
        task_prompt = f"""
{resume_text}

---

Please analyze the resume above following this format:

{RESUME_ANALYZER_FORMAT}

Be thorough but concise. Extract as much information as possible.
If something is unclear or not present, note that explicitly.
"""
        
        # Execute the task using the agent
        response = self.agent.execute_task(task_prompt)
        
        return response
    
    def get_agent(self) -> Agent:
        """Return the underlying CrewAI agent for crew integration."""
        return self.agent