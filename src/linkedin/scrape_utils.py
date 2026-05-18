"""
ScrapeGraphAI integration for JD extraction.
Uses SmartScraperGraph from pip-installed scrapegraphai with BlackBox/Kimi as the LLM.
"""

import os
import sys
import subprocess


# ------------------------------------------------------------------
# Lazy import helpers — only load ScrapeGraphAI when actually scraping
# ------------------------------------------------------------------
def _get_scraper():
    """Import and return SmartScraperGraph class (lazy load from pip-installed)."""
    from scrapegraphai.graphs import SmartScraperGraph
    return SmartScraperGraph


# -------------------------------------------------------------------------
# Config builder (safe to call at module level — no ScrapeGraphAI import)
# -------------------------------------------------------------------------
def get_scrapegraph_config() -> dict:
    """Build the LLM config for SmartScraperGraph pointing at BlackBox/Kimi."""
    src_dir = os.path.join(os.path.dirname(__file__), "..")
    sys.path.insert(0, src_dir)
    try:
        from config import get_blackbox_api_key, DEFAULT_MODEL, BLACKBOX_API_BASE
        api_key = get_blackbox_api_key()
        base_url = BLACKBOX_API_BASE
    except Exception:
        api_key = os.getenv("BLACKBOX_API_KEY", "").strip()
        base_url = "https://api.blackbox.ai/v1"

    return {
        "llm": {
            "model": "moonshotai/kimi-k2.6",
            "api_key": api_key,
            "base_url": base_url,
            "temperature": 0.0,
        },
    }


# -------------------------------------------------------------------------
# Safe wrapper: runs ScrapeGraphAI via subprocess, enforces timeout, returns JSON
# -------------------------------------------------------------------------
def _run_scrapegraph_subprocess(url: str, prompt: str, timeout: int) -> str:
    """Call SmartScraperGraph in a subprocess — killed on timeout, returns JSON str."""

    # Load env so API key is available to subprocess
    env = os.environ.copy()
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env.local")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()

    script = f"""
import sys, os
sys.path.insert(0, '.')
os.environ['BLACKBOX_API_KEY'] = {repr(env.get('BLACKBOX_API_KEY', ''))}
os.environ['BLACKBOX_API_BASE'] = {repr(env.get('BLACKBOX_API_BASE', 'https://api.blackbox.ai/v1'))}
from linkedin.scrape_utils import _get_scraper, get_scrapegraph_config
SmartScraperGraph = _get_scraper()
config = get_scrapegraph_config()
graph = SmartScraperGraph(prompt={repr(prompt)}, source={repr(url)}, config=config)
result = graph.run()
if isinstance(result, dict):
    out = result.get("answer") or result.get("output") or str(result)
elif isinstance(result, str):
    out = result
else:
    out = str(result)
print(repr(out[:3000]))
"""

    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
            env=env,
        )
        if proc.returncode == 0:
            return eval(proc.stdout.strip()) if proc.stdout.strip() else ""
        else:
            err = proc.stderr.strip()
            if not err:
                err = f"exit code {proc.returncode}"
            raise RuntimeError(err)
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"ScrapeGraphAI timed out after {timeout}s — "
            "site may be blocking automated requests. Paste the JD manually."
        )


# -------------------------------------------------------------------------
# Main extraction function — handles timeout + clear error messages
# -------------------------------------------------------------------------
def extract_jd_with_scrapegraph(url: str, timeout: int = 25) -> str:
    """Extract job description from any URL using ScrapeGraphAI + Kimi.

    Times out after `timeout` seconds with a clear user-facing message.

    Works with: Greenhouse, Lever, Ashby, Indeed, Naukri, and most job boards.
    LinkedIn job pages typically require login — use the paste JD option.

    Args:
        url: Job posting URL
        timeout: Max seconds (default 25)

    Returns:
        Extracted job description text
    """
    url_lower = url.lower()

    # Warn about LinkedIn (blocks automated scraping)
    if "linkedin.com" in url_lower:
        raise TimeoutError(
            "LinkedIn blocks automated scraping. "
            "Please use 'Paste JD text' instead — paste the job description directly from LinkedIn."
        )

    prompt = (
        "Extract the complete job posting including:\n"
        "- Job title\n"
        "- Company name and description\n"
        "- Location (city, state/country, remote policy)\n"
        "- Job type (full-time, contract, etc.)\n"
        "- Key responsibilities and duties\n"
        "- Required qualifications and skills (hard + soft)\n"
        "- Nice-to-have skills\n"
        "- Education requirements\n"
        "- Salary range (if present)\n"
        "- Benefits and perks\n"
        "- Application deadline or posting date\n"
        "Return the formatted result."
    )

    return _run_scrapegraph_subprocess(url, prompt, timeout)


def extract_jd_from_html(html: str, url: str = "local", prompt: str = "") -> str:
    """Extract JD from raw HTML using SmartScraperGraph with local HTML source."""
    SmartScraperGraph = _get_scraper()
    if not prompt:
        prompt = (
            "Extract the complete job posting including: job title, company name, "
            "location, responsibilities, qualifications, required skills, preferred skills, "
            "education, salary range (if any), benefits, and any other relevant details."
        )

    config = get_scrapegraph_config()
    config.pop("embedder", None)

    try:
        smart_scraper = SmartScraperGraph(prompt=prompt, source=html, config=config)
        result = smart_scraper.run()
        if isinstance(result, dict):
            if "answer" in result:
                return result["answer"]
            if "output" in result:
                return result["output"]
            return str(result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        raise RuntimeError(f"ScrapeGraphAI HTML extraction failed: {e}") from e


def batch_extract_jds(urls: list[str]) -> dict[str, str]:
    """Extract JDs from multiple URLs in sequence."""
    results = {}
    for url in urls:
        try:
            results[url] = extract_jd_with_scrapegraph(url)
        except Exception as e:
            results[url] = f"ERROR: {e}"
    return results