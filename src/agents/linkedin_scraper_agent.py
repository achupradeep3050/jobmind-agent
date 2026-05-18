"""
LinkedIn Specialist Agent — searches LinkedIn jobs and scrapes profiles.

Uses the existing authenticated Playwright session from Hermes
(~/.hermes/.linkedin_session.pkl) so no login needed.
"""
from crewai import Agent
from config import AGENT_VERBOSE, DEFAULT_MODEL, BLACKBOX_API_BASE, get_blackbox_api_key
import litellm
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "linkedin"))
from client import LinkedInClient


ROLE = "LinkedIn Job & Profile Researcher"
GOAL = (
    "Search LinkedIn for relevant job postings matching the user's target roles "
    "(DevOps, SRE, Python Developer, AI Engineer, Platform Engineer). "
    "Also scrape LinkedIn profiles for recruiting contacts, hiring managers, or peers. "
    "Use the existing authenticated Playwright session — no login needed."
)
BACKSTORY = (
    "You are a LinkedIn power user who knows how to navigate the platform efficiently. "
    "You use browser automation to search jobs and profiles on LinkedIn without manual browsing. "
    "You've helped engineers find hidden job opportunities and connect with the right people."
)
FORMAT = """For job searches, return:
1. Top 5-10 relevant job listings with: title, company, location, posted time, and match reason
2. Overall market demand for this role (High/Medium/Low)

For profile scraping, return:
1. Name, headline, location, connections count
2. Brief summary of background and expertise
3. Whether this person is a good contact for the user's job search
"""


class LinkedInScraperAgent:
    """Handles all LinkedIn operations — job search and profile scraping."""

    def __init__(self, llm):
        self.llm = llm

    def get_agent(self) -> Agent:
        return Agent(
            role=ROLE,
            goal=GOAL,
            backstory=BACKSTORY,
            verbose=AGENT_VERBOSE,
            llm=self.llm,
            allow_delegation=False,
        )

    def search_jobs(self, keywords: str, location: str = "India", limit: int = 25) -> str:
        """Search LinkedIn jobs directly — returns formatted results."""
        try:
            jobs = asyncio.run(LinkedInClient().search_jobs(keywords, location, limit))

            if not jobs:
                return "No jobs found. Try broadening your search keywords."

            lines = ["## LinkedIn Job Search Results\n"]
            lines.append(f"**Query:** {keywords} | **Location:** {location}\n")
            lines.append(f"**Found:** {len(jobs)} listings\n")

            for i, job in enumerate(jobs[:10], 1):
                lines.append(f"\n### {i}. {job.get('title', 'N/A')}")
                lines.append(f"- **Company:** {job.get('company', 'N/A')}")
                lines.append(f"- **Location:** {job.get('location', location)}")
                lines.append(f"- **Posted:** {job.get('posted', 'N/A')}")

            lines.append("\n\n## Top Picks")
            # Score jobs by keyword relevance
            scored = []
            for job in jobs:
                title_lower = job.get("title", "").lower()
                score = 0
                for kw in ["devops", "sre", "site reliability", "platform", "aws", "kubernetes", "python", "ai", "cloud"]:
                    if kw in title_lower:
                        score += 1
                scored.append((score, job))

            scored.sort(key=lambda x: x[0], reverse=True)
            for score, job in scored[:5]:
                lines.append(f"- [{job.get('title', 'N/A')}] @ {job.get('company', 'N/A')} ({job.get('location', '')}) — score: {score}/5")

            return "\n".join(lines)
        except Exception as e:
            return f"LinkedIn search failed: {e}\n\nMake sure you have an active LinkedIn session in Hermes."

    def scrape_profile(self, profile_url: str) -> str:
        """Scrape a LinkedIn profile — returns formatted summary."""
        try:
            profile = asyncio.run(LinkedInClient().scrape_profile(profile_url))

            lines = ["## LinkedIn Profile\n"]
            lines.append(f"**Name:** {profile.get('name', 'Unknown')}")
            lines.append(f"**Headline:** {profile.get('headline', 'N/A')}")
            lines.append(f"**Location:** {profile.get('location', 'N/A')}")
            lines.append(f"**Connections:** {profile.get('connections', 'N/A')}")
            lines.append(f"**URL:** {profile.get('url', profile_url)}")
            if profile.get("about"):
                lines.append(f"\n**About:**\n{profile.get('about')[:500]}")
            lines.append(f"\n**Raw text preview:**\n{profile.get('raw_text', '')[:1000]}")

            return "\n".join(lines)
        except Exception as e:
            return f"Profile scrape failed: {e}"