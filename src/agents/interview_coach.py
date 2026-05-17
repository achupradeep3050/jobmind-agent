"""
Interview Coach Agent
Generates targeted interview questions with model answers.
"""

from crewai import Agent
from config import AGENT_VERBOSE
from utils.prompts import (
    INTERVIEW_COACH_ROLE,
    INTERVIEW_COACH_GOAL,
    INTERVIEW_COACH_BACKSTORY,
    INTERVIEW_COACH_FORMAT
)


class InterviewCoachAgent:
    """
    Agent responsible for generating interview questions and coaching tips.
    
    This agent creates practice questions that reflect real interview scenarios,
    complete with model answers and strategic tips. It helps candidates prepare
    thoroughly for their target role.
    """
    
    def __init__(self, llm):
        """
        Initialize the Interview Coach Agent.
        
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
            role=INTERVIEW_COACH_ROLE,
            goal=INTERVIEW_COACH_GOAL,
            backstory=INTERVIEW_COACH_BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,
            memory=True,
        )
    
    def generate_interview_prep(
        self,
        resume_analysis: str,
        jd_analysis: str,
        match_analysis: str
    ) -> str:
        """
        Generate interview questions tailored to the role and candidate profile.
        
        Args:
            resume_analysis: Structured resume analysis
            jd_analysis: Structured job description analysis
            match_analysis: Match maker analysis with gaps identified
            
        Returns:
            str: Comprehensive interview prep guide with questions and answers
        """
        task_prompt = f"""
## Interview Preparation Request

### CANDIDATE PROFILE (from resume analysis):
---
{resume_analysis}
---

### ROLE REQUIREMENTS (from JD analysis):
---
{jd_analysis}
---

### MATCH ANALYSIS (strengths and gaps identified):
---
{match_analysis}
---

Please generate a comprehensive interview preparation guide:

{INTERVIEW_COACH_FORMAT}

GENERATION GUIDELINES:
1. **Technical Questions**: Based on the REQUIRED skills in the JD, not just
   general questions. If the job requires Python, ask Python-specific questions.

2. **Behavioral Questions**: Use the STAR method. Choose stories that highlight
   relevant experiences based on the role.

3. **Situational Questions**: Create scenarios relevant to the job's
   responsibilities, especially for gaps in experience.

4. **Question Count**: Generate 6-10 questions total:
   - 3-4 Technical questions
   - 3-4 Behavioral questions  
   - 1-2 Situational questions

5. **Difficulty Calibration**: Match question difficulty to the job level
   (Junior = easier, Senior = harder/strategic)

6. **Model Answers**: Provide substantive answers, not just "what to say."
   Explain WHY certain answers work better.

7. **Personalize**: Use specific skills/technologies mentioned in both
   the resume and job description.
"""
        
        response = self.agent.execute_task(task_prompt)
        
        return response
    
    def get_agent(self) -> Agent:
        """Return the underlying CrewAI agent for crew integration."""
        return self.agent