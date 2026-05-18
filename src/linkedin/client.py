"""LinkedIn API Client — uses existing authenticated Playwright session from Hermes."""
import asyncio
import re
from pathlib import Path
from typing import Optional

LINKEDIN_SESSION_PATH = Path.home() / ".hermes" / ".linkedin_session.pkl"


class LinkedInClient:
    """Handles all LinkedIn operations using the existing authenticated session.

    The session is pre-authenticated via li_at cookie saved at ~/.hermes/.linkedin_session.pkl.
    This client just reuses that session — no login needed.
    """

    def __init__(self):
        self.session_path = LINKEDIN_SESSION_PATH
        self._browser = None
        self._context = None

    async def get_context(self):
        """Load existing Playwright session from Hermes cookie store."""
        if self._context is None:
            from playwright.async_api import async_playwright
            pw = await async_playwright().start()
            self._browser = await pw.chromium.launch(headless=True)
            if self.session_path.exists():
                self._context = await self._browser.new_context(
                    storage_state=str(self.session_path)
                )
            else:
                self._context = await self._browser.new_context()
            self._pw = pw
        return self._context

    async def scrape_profile(self, profile_url: str) -> dict:
        """Scrape a LinkedIn profile.

        Args:
            profile_url: Full URL or just username (e.g. 'achu-pradeep-702667404')

        Returns:
            dict with name, headline, location, connections, url, raw_text
        """
        ctx = await self.get_context()
        page = await ctx.new_page()

        if not profile_url.startswith("http"):
            profile_url = f"https://www.linkedin.com/in/{profile_url}"

        await page.goto(profile_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 600)")
            await page.wait_for_timeout(800)

        text = await page.inner_text("body")
        await page.close()

        # Extract key fields from rendered text
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        name = lines[0] if lines else "Unknown"

        # Headline (usually near name)
        headline = ""
        for i, line in enumerate(lines[:20]):
            if any(kw in line for kw in ["DevOps", "Engineer", "Developer", "Administrator", "SRE", "Manager"]):
                headline = line
                break

        # Location
        location = ""
        for line in lines[:50]:
            if any(loc in line for loc in ["Kerala", "Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "India", "Kochi"]):
                location = line
                break

        # Connections
        conn_match = re.search(r"(\d+)\s*(?:connections|connection)", text)
        connections = conn_match.group(1) if conn_match else "N/A"

        # About section
        about = ""
        about_match = re.search(r"(?:About|About me)(.{500})", text, re.DOTALL)
        if about_match:
            about = about_match.group(1)[:300].strip()

        return {
            "name": name,
            "headline": headline,
            "location": location,
            "connections": connections,
            "about": about,
            "url": profile_url,
            "raw_text": text[:8000],
        }

    async def search_jobs(self, keywords: str, location: str = "India", limit: int = 30) -> list:
        """Search LinkedIn jobs and return structured results.

        Args:
            keywords: Job title/keyword (e.g. "DevOps Engineer Python")
            location: Location filter
            limit: Max results to return

        Returns:
            list of dicts: {title, company, location, posted, snippet}
        """
        ctx = await self.get_context()
        page = await ctx.new_page()

        query_enc = keywords.replace(" ", "%20")
        loc_enc = location.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query_enc}&location={loc_enc}&f_TPR=r2592000"

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(800)

        text = await page.inner_text("body")
        await page.close()

        # Parse job cards — LinkedIn shows title @ company | location | time
        jobs = []
        seen = set()

        # Split into lines and find job-like entries
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for i, line in enumerate(lines):
            # Skip very short or very long lines
            if len(line) < 10 or len(line) > 200:
                continue
            if line in seen:
                continue

            # Job title indicators
            if any(kw in line for kw in ["DevOps", "SRE", "Engineer", "Developer", "Python", "Cloud", "Platform", "Site Reliability", "Infrastructure"]):
                # Get next lines as company/location context
                company = lines[i+1] if i+1 < len(lines) else ""
                time_marker = ""
                for n in lines[i:i+5]:
                    if any(tm in n for tm in ["ago", "day", "week", "month", "hour"]):
                        time_marker = n
                        break

                jobs.append({
                    "title": line[:150],
                    "company": company[:100] if company else "N/A",
                    "location": location,
                    "posted": time_marker or "N/A",
                    "raw": line,
                })
                seen.add(line)

            if len(jobs) >= limit:
                break

        return jobs

    async def close(self):
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
        if hasattr(self, "_pw"):
            await self._pw.stop()


async def search_jobs(keywords: str, location: str = "India", limit: int = 25) -> list:
    """Convenience wrapper — search LinkedIn jobs synchronously."""
    client = LinkedInClient()
    try:
        return await client.search_jobs(keywords, location, limit)
    finally:
        await client.close()