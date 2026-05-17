"""
JobMind Tasks — Define CrewAI tasks for each agent.
"""

from crewai import Task

def create_resume_analysis_task(resume_text: str, agent):
    return Task(
        description=f"Analyze the resume and extract key information.\nResume:\n{resume_text}",
        agent=agent,
        expected_output="Structured resume analysis with skills, experience, education summary.",
    )

def create_jd_analysis_task(job_description: str, agent):
    return Task(
        description=f"Analyze the job description to understand requirements.\nJob Description:\n{job_description}",
        agent=agent,
        expected_output="Key requirements, must-have skills, and qualifications from the JD.",
    )

def create_match_task(resume_summary: str, jd_analysis: str, agent):
    return Task(
        description=f"Match resume to job description.\nResume Summary:\n{resume_summary}\n\nJob Requirements:\n{jd_analysis}",
        agent=agent,
        expected_output="Match score with strengths and gaps identified.",
    )

def create_interviewPrep_task(job_desc: str, resume: str, agent):
    return Task(
        description=f"Prepare interview questions based on job description and resume.\nJob Description:\n{job_desc}\n\nResume:\n{resume}",
        agent=agent,
        expected_output="Top 10 likely interview questions with suggested answers.",
    )

def create_coverLetter_task(job_desc: str, resume: str, agent):
    return Task(
        description=f"Write a tailored cover letter.\nJob Description:\n{job_desc}\n\nResume:\n{resume}",
        agent=agent,
        expected_output="Professional cover letter customized for the position.",
    )