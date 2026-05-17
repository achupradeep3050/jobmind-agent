"""
Cover Letter Generator Agent
Creates personalized, professional cover letters.
"""

from crewai import Agent
from config import AGENT_VERBOSE
from utils.prompts import (
    COVER_LETTER_ROLE,
    COVER_LETTER_GOAL,
    COVER_LETTER_BACKSTORY,
    COVER_LETTER_INSTRUCTIONS
)


class CoverLetterAgent:
    """
    Agent responsible for writing customized cover letters.
    
    This agent crafts compelling cover letters that tell the candidate's story
    in a way that connects their experience to the specific role, going beyond
    simple resume repetition.
    """
    
    def __init__(self, llm):
        """
        Initialize the Cover Letter Agent.
        
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
            role=COVER_LETTER_ROLE,
            goal=COVER_LETTER_GOAL,
            backstory=COVER_LETTER_BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,
            memory=True,
        )
    
    def generate_cover_letter(
        self,
        resume_analysis: str,
        jd_analysis: str,
        match_analysis: str,
        candidate_name: str = "Candidate"
    ) -> str:
        """
        Generate a personalized cover letter.
        
        Args:
            resume_analysis: Structured resume analysis with candidate info
            jd_analysis: Structured job description analysis
            match_analysis: Match analysis highlighting strengths
            candidate_name: Name of the candidate for personalization
            
        Returns:
            str: Complete cover letter ready for submission
        """
        task_prompt = f"""
## Cover Letter Generation Request

### CANDIDATE INFORMATION:
{candidate_name}

---
RESUME ANALYSIS:
{resume_analysis}
---

### TARGET POSITION (from JD):
---
{jd_analysis}
---

### MATCH HIGHLIGHTS (strengths to emphasize):
---
{match_analysis}
---

{COVER_LETTER_INSTRUCTIONS}

WRITING GUIDELINES:
1. **Opening Hook**: Start with something compelling about the candidate's
   value proposition - not "I am applying for..."

2. **Body Content**: Focus on 2-3 specific achievements that directly relate
   to the job requirements. Use actual accomplishments where available.

3. **Company Research Placeholder**: Include a line like "I'm drawn to [Company]
   because..." - the user can fill in specifics

4. **Tone**: Confident but not arrogant, enthusiastic but professional

5. **Length**: Aim for 300-400 words (3-4 paragraphs)

6. **Avoid**: Repeating the resume verbatim. The cover letter should ADD context.

IMPORTANT: Return ONLY the cover letter text, no explanations or meta-commentary.
Start directly with the salutation or (if name unknown) "Dear Hiring Manager,"
"""
        
        response = self.agent.execute_task(task_prompt)
        
        return response
    
    def get_agent(self) -> Agent:
        """Return the underlying CrewAI agent for crew integration."""
        return self.agent