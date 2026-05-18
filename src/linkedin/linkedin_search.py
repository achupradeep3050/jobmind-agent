"""LinkedIn job search agent — searches LinkedIn for relevant jobs and filters by match."""
from crewai import Agent
from config import AGENT_VERBOSE, DEFAULT_MODEL, BLACKBOX_API_BASE, get_blackbox_api_key
from .client import LinkedInClient
import asyncio

ROLE = "LinkedIn Job Search Specialist"
GOAL = (
    "Find relevant job postings on LinkedIn matching DevOps, SRE, Python Developer, "
    "or AI Engineer roles. Search using Playwright on the user's authenticated session, "
    "filter by relevance, and return a curated ranked list."
)
BACKSTORY = (
    "You are a job search specialist with deep knowledge of LinkedIn's job market. "
    "You know how to find the most relevant DevOps, SRE, and Python opportunities. "
    "You focus on quality over quantity — finding 5 great matches beats 50 mediocre ones."
)


def create_linkedin_search_agent(llm) -> Agent:
    """Create the LinkedIn search agent with the shared LLM."""
    return Agent(
        role=ROLE,
        goal=GOAL,
        backstory=BACKSTORY,
        verbose=AGENT_VERBOSE,
        llm=llm,
        allow_delegation=False,
    )


async def run_linkedin_job_search(keywords: str, location: str = "India", limit: int = 25) -> list:
    """Search LinkedIn jobs using the authenticated Playwright session.

    Args:
        keywords: Search query (e.g. "DevOps Engineer Python")
        location: Location filter
        limit: Max results

    Returns:
        List of job dicts with title, company, location, posted, raw fields
    """
    client = LinkedInClient()
    try:
        return await client.search_jobs(keywords, location, limit)
    finally:
        await client.close()