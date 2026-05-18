"""
Job Description Scraper Agent — extracts JDs from URLs using ScrapeGraphAI + Kimi.

Supports: LinkedIn, Greenhouse, Lever, Ashby, Indeed, Naukri, AngelList, and any
standard job posting page.

Note: ScrapeGraphAI is imported INSIDE methods to avoid loading the entire package
tree at app startup (cleanup_html.py requires minify_html which isn't installed).
"""
from crewai import Agent
from config import AGENT_VERBOSE, DEFAULT_MODEL, BLACKBOX_API_BASE, get_blackbox_api_key
import litellm
import os
import sys


ROLE = "JD Extraction Specialist"
GOAL = (
    "Given a job posting URL, extract the complete job description including "
    "title, company, location, responsibilities, requirements, skills, salary (if any), "
    "and benefits. Return well-structured text."
)
BACKSTORY = (
    "You are a meticulous job posting extractor. You use ScrapeGraphAI to navigate "
    "any job board and pull out exactly what matters for job applications. "
    "You have extracted thousands of JDs from LinkedIn, Greenhouse, Lever, Ashby, and more."
)
FORMAT = """Return the extracted job description in this structure:

**JOB TITLE:**
**COMPANY:**
**LOCATION:**
**REMOTE POLICY:**
**JOB TYPE:**
**POSTED DATE:**

**ABOUT THE ROLE:**
[brief description]

**KEY RESPONSIBILITIES:**
- ...

**REQUIRED QUALIFICATIONS:**
- Hard skills
- Soft skills

**PREFERRED/NICE-TO-HAVE:**
- ...

**EDUCATION:**
**EXPERIENCE:**
**SALARY RANGE:** (note "Not specified" if absent)
**BENEFITS:**
**APPLICATION DEADLINE:**
"""


class JDScraperAgent:
    """Uses ScrapeGraphAI + Kimi to extract JDs from URLs."""

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

    def _get_scrapegraph_config(self) -> dict:
        api_key = get_blackbox_api_key()
        return {
            "llm": {
                "model": DEFAULT_MODEL,
                "api_key": api_key,
                "base_url": BLACKBOX_API_BASE,
                "temperature": 0.0,
            },
            "verbose": False,
            "headless": True,
        }

    def extract_from_url(self, url: str) -> str:
        """Extract JD directly using ScrapeGraphAI (no LLM agent needed)."""
        # Lazy import: only load ScrapeGraphAI when actually scraping
        # This avoids minify_html dependency crash at app startup
        import sys as _sys
        SCRAPEGRAPH_REPO = os.path.expanduser("~/Scrapegraph-ai")
        if SCRAPEGRAPH_REPO not in _sys.path:
            _sys.path.insert(0, SCRAPEGRAPH_REPO)
        from scrapegraphai.graphs import SmartScraperGraph

        config = self._get_scrapegraph_config()
        prompt = (
            "Extract the complete job posting including:\n"
            "- Job title, company name, location, remote policy\n"
            "- Responsibilities and duties\n"
            "- Required qualifications, skills, education\n"
            "- Salary range (if present), benefits, posting date\n"
            "Return all information verbatim."
        )

        try:
            scraper = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config=config,
            )
            result = scraper.run()
            if isinstance(result, dict):
                return result.get("answer", result.get("output", str(result)))
            return str(result) if result else "Could not extract content."
        except Exception as e:
            return f"ERROR: Could not extract from {url}: {e}"

    def analyze_and_extract(self, url: str) -> str:
        """CrewAI-compatible analyze method — uses LLM to parse and format."""
        raw = self.extract_from_url(url)

        prompt = (
            f"You have extracted the following job description from a web page. "
            f"Parse and format it cleanly. If the extraction failed or looks wrong, note it.\n\n"
            f"RAW EXTRACTION:\n{raw}\n\n"
            f"Now format it as:\n{FORMAT}"
        )

        try:
            response = litellm.completion(
                model=DEFAULT_MODEL,
                api_key=get_blackbox_api_key(),
                base_url=BLACKBOX_API_BASE,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Formatting error: {e}\n\nRaw extraction:\n{raw}"