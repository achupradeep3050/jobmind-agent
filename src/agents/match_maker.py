"""
Match Maker Agent
Compares resume and job description to identify gaps and calculate match scores.
"""

from crewai import Agent
from config import AGENT_VERBOSE
from utils.prompts import (
    MATCH_MAKER_ROLE,
    MATCH_MAKER_GOAL,
    MATCH_MAKER_BACKSTORY,
    MATCH_MAKER_FORMAT
)


class MatchMakerAgent:
    """
    Agent responsible for comparing resume vs. job requirements.
    
    This agent calculates the overall fit between a candidate and a role,
    highlighting strengths, gaps, and areas for improvement. It's the central
    piece that ties together the resume and JD analysis.
    """
    
    def __init__(self, llm):
        """
        Initialize the Match Maker Agent.
        
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
            role=MATCH_MAKER_ROLE,
            goal=MATCH_MAKER_GOAL,
            backstory=MATCH_MAKER_BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,
            memory=True,
        )
    
    def analyze_match(
        self,
        resume_analysis: str,
        jd_analysis: str,
        original_resume: str,
        original_jd: str
    ) -> str:
        """
        Calculate match score and identify gaps between resume and job requirements.
        
        Args:
            resume_analysis: Structured output from ResumeAnalyzerAgent
            jd_analysis: Structured output from JDAnalyzerAgent
            original_resume: Raw resume text for additional context
            original_jd: Raw job description for keyword checking
            
        Returns:
            str: Detailed match report with score and recommendations
        """
        task_prompt = f"""
## Task: Compare Resume Against Job Requirements

### RESUME ANALYSIS:
---
{resume_analysis}
---

### JOB DESCRIPTION ANALYSIS:
---
{jd_analysis}
---

### RAW RESUME (for reference):
---
{original_resume[:2000]}...
---

### RAW JOB DESCRIPTION (for ATS keyword checking):
---
{original_jd[:2000]}...
---

Please perform a comprehensive match analysis:

{MATCH_MAKER_FORMAT}

CRITICAL INSTRUCTIONS:
1. Calculate an honest overall match percentage (0-100%)
2. Be specific about skills - don't just say "technical skills"
3. Look for BOTH explicit matches AND subtle alignments
4. Identify keywords from JD that are MISSING from resume
5. Provide ACTIONABLE recommendations, not generic advice
6. Flag anything concerning (huge gaps, red flags, etc.)

The match score should reflect realistic expectations.
"""
        
        response = self.agent.execute_task(task_prompt)
        
        return response
    
    def get_agent(self) -> Agent:
        """Return the underlying CrewAI agent for crew integration."""
        return self.agent