"""
Job Description Analyzer Agent
Parses job descriptions to extract requirements, keywords, and context.
"""

from crewai import Agent
from config import AGENT_VERBOSE
from utils.prompts import (
    JD_ANALYZER_ROLE,
    JD_ANALYZER_GOAL,
    JD_ANALYZER_BACKSTORY,
    JD_ANALYZER_FORMAT
)


class JDAnalyzerAgent:
    """
    Agent responsible for decoding job descriptions.
    
    This agent understands the hidden meaning behind job posting language
    and extracts both explicit requirements and subtle cues about what
    the company really wants.
    """
    
    def __init__(self, llm):
        """
        Initialize the JD Analyzer Agent.
        
        Args:
            llm: The LLM instance to use for reasoning
        """
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create and configure the CrewAI agent.
        
        Returns:
            Agent: Configured CrewAI agent instance
        """
        return Agent(
            role=JD_ANALYZER_ROLE,
            goal=JD_ANALYZER_GOAL,
            backstory=JD_ANALYZER_BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,
            memory=True,
        )
    
    def analyze(self, job_description: str) -> str:
        """
        Analyze a job description and return structured findings.
        
        Args:
            job_description: The raw text of the job posting
            
        Returns:
            str: Structured analysis with extracted requirements
        """
        task_prompt = f"""
{job_description}

---

Please analyze this job description following this format:

{JD_ANALYZER_FORMAT}

Pay special attention to:
- Repeated keywords (indicates importance)
- Vague requirements and what they might really mean
- Order of requirements (often priority indicator)
- Culture/environment hints

Be thorough and interpret recruiter shorthand where possible.
"""
        
        response = self.agent.execute_task(task_prompt)
        
        return response
    
    def get_agent(self) -> Agent:
        """Return the underlying CrewAI agent for crew integration."""
        return self.agent