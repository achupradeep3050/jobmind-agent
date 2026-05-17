"""
Crew Setup Module
Orchestrates all agents together as a CrewAI crew for parallel processing.
"""

import os
import sys

# Fix import path so 'utils' resolves to src/utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crewai import Crew, Process
import litellm

from config import (
    AGENT_VERBOSE,
    DEFAULT_MODEL,
    BLACKBOX_API_BASE,
    get_blackbox_api_key,
    MAX_RESEARCH_MINUTES
)

# Configure litellm to use Blackbox API
litellm.api_base = BLACKBOX_API_BASE
litellm.model = DEFAULT_MODEL


# Import all agents - direct module imports (avoiding __init__.py re-exports)
import importlib

def _import_agent(name):
    return importlib.import_module(f"agents.{name}")

ResumeAnalyzerAgent = _import_agent("resume_analyzer").ResumeAnalyzerAgent
JDAnalyzerAgent = _import_agent("jd_analyzer").JDAnalyzerAgent
MatchMakerAgent = _import_agent("match_maker").MatchMakerAgent
InterviewCoachAgent = _import_agent("interview_coach").InterviewCoachAgent
CoverLetterAgent = _import_agent("cover_letter_agent").CoverLetterAgent


class JobMindCrew:
    """
    Main crew class that orchestrates all agents working together.
    
    This class sets up the multi-agent system where different specialized
    agents work on different aspects of job application preparation,
    then share their results for coordinated output.
    """
    
    def __init__(self):
        """Initialize the crew with LLM and all agents."""
        # Initialize the LLM with Blackbox API key
        api_key = get_blackbox_api_key()
        
        # Use litellm to handle Blackbox/Kimi models (CrewAI compatible)
        # base_url explicitly needed — Litellm.global_state doesn't always propagate
        self.llm = litellm.LLM(
            model=DEFAULT_MODEL,
            api_key=api_key,
            base_url=BLACKBOX_API_BASE,
        )
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """
        Create instances of all specialized agents.
        Each agent gets the same LLM but has different roles/goals.
        """
        self.resume_analyzer = ResumeAnalyzerAgent(self.llm)
        self.jd_analyzer = JDAnalyzerAgent(self.llm)
        self.match_maker = MatchMakerAgent(self.llm)
        self.interview_coach = InterviewCoachAgent(self.llm)
        self.cover_letter_agent = CoverLetterAgent(self.llm)
    
    def _create_crew(self, tasks_for_agents: dict) -> Crew:
        """
        Create a CrewAI Crew with configured agents and tasks.
        
        Args:
            tasks_for_agents: Dictionary mapping agent names to task prompts
            
        Returns:
            Crew: Configured CrewAI crew ready to execute
        """
        # Map agent names to agent objects
        agent_map = {
            "resume_analyzer": self.resume_analyzer.get_agent(),
            "jd_analyzer": self.jd_analyzer.get_agent(),
            "match_maker": self.match_maker.get_agent(),
            "interview_coach": self.interview_coach.get_agent(),
            "cover_letter_agent": self.cover_letter_agent.get_agent(),
        }
        
        # Create crew with hierarchical process (sequential with manager oversight)
        # Alternative: Process.parallel for independent tasks
        crew = Crew(
            agents=list(agent_map.values()),
            tasks=[],  # Tasks added dynamically based on workflow
            verbose=AGENT_VERBOSE,
            process=Process.hierarchical,  # Sequential with agent coordination
            manager_llm=self.llm,  # LLM for manager coordination
        )
        
        return crew
    
    def run_full_analysis(self, resume_text: str, job_description: str) -> dict:
        """
        Run the complete analysis pipeline.
        
        Pipeline order:
        1. Analyze resume → extract skills, experience
        2. Analyze JD → extract requirements, keywords
        3. Match analysis → compare and score
        4. Generate interview questions
        5. Optionally generate cover letter
        
        Args:
            resume_text: Raw text of the resume
            job_description: Raw text of the job description
            
        Returns:
            dict: All analysis results keyed by type
        """
        results = {}
        
        # Step 1: Resume Analysis
        print("🔍 Analyzing resume...")
        results["resume_analysis"] = self.resume_analyzer.analyze(resume_text)
        
        # Step 2: JD Analysis
        print("📋 Analyzing job description...")
        results["jd_analysis"] = self.jd_analyzer.analyze(job_description)
        
        # Step 3: Match Analysis (uses outputs from step 1 & 2)
        print("🎯 Calculating match analysis...")
        results["match_analysis"] = self.match_maker.analyze_match(
            resume_analysis=results["resume_analysis"],
            jd_analysis=results["jd_analysis"],
            original_resume=resume_text,
            original_jd=job_description
        )
        
        # Step 4: Interview Prep (uses outputs from steps 1, 2, 3)
        print("💬 Generating interview preparation...")
        results["interview_prep"] = self.interview_coach.generate_interview_prep(
            resume_analysis=results["resume_analysis"],
            jd_analysis=results["jd_analysis"],
            match_analysis=results["match_analysis"]
        )
        
        return results
    
    def run_match_analysis_only(self, resume_text: str, job_description: str) -> dict:
        """
        Run only the match analysis portion (faster).
        
        Useful for quick evaluation before committing to full analysis.
        
        Args:
            resume_text: Raw text of the resume
            job_description: Raw text of the job description
            
        Returns:
            dict: Resume analysis, JD analysis, and match results
        """
        results = {}
        
        # Parallel analysis of resume and JD
        results["resume_analysis"] = self.resume_analyzer.analyze(resume_text)
        results["jd_analysis"] = self.jd_analyzer.analyze(job_description)
        
        # Then match
        results["match_analysis"] = self.match_maker.analyze_match(
            resume_analysis=results["resume_analysis"],
            jd_analysis=results["jd_analysis"],
            original_resume=resume_text,
            original_jd=job_description
        )
        
        return results
    
    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        match_analysis: str,
        candidate_name: str = "Candidate"
    ) -> str:
        """
        Generate a cover letter using existing analysis.
        
        This can be called separately after running full analysis,
        reusing the earlier results for efficiency.
        
        Args:
            resume_text: Original resume text
            job_description: Original job description
            match_analysis: Previously generated match analysis
            candidate_name: Candidate's name for personalization
            
        Returns:
            str: Generated cover letter
        """
        # Need fresh resume analysis
        resume_analysis = self.resume_analyzer.analyze(resume_text)
        jd_analysis = self.jd_analyzer.analyze(job_description)
        
        return self.cover_letter_agent.generate_cover_letter(
            resume_analysis=resume_analysis,
            jd_analysis=jd_analysis,
            match_analysis=match_analysis,
            candidate_name=candidate_name
        )


# ============================================================================
# CONVENIENCE FUNCTION FOR STREAMLIT INTEGRATION
# ============================================================================

def create_crew() -> JobMindCrew:
    """
    Factory function to create a configured JobMind crew.
    
    This is the main entry point for creating a working crew instance.
    Handles API key validation and returns a ready-to-use crew.
    
    Returns:
        JobMindCrew: Configured crew instance
        
    Raises:
        ValueError: If API key is missing
    """
    try:
        crew = JobMindCrew()
        return crew
    except ValueError as e:
        # Re-raise with cleaner message for UI handling
        raise e