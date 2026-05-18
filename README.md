# JobMind 2.0 — AI-Powered Job Application Agent

Unified job application pipeline: **LinkedIn search → JD extraction → match scoring → interview prep → cover letter generation**.

Replace the profile placeholders in `config/profile.yml` with your own details.

---

## Stack

| Component | Technology |
|-----------|------------|
| LLM | Kimi (via BlackBox API) |
| Multi-Agent | CrewAI (parallel agents) |
| Web Scraping | ScrapeGraphAI (local repo + Kimi) |
| LinkedIn | Playwright (authenticated session) |
| UI | Streamlit |

---

## Quick Start

```bash
cd ~/projects/job-application-agent

# 1. Authenticate LinkedIn once (saves session cookie for future runs)
python -m playwright install chromium  # if not already installed
# Then in browser, log into LinkedIn normally — session auto-saved

# 2. Run the app
streamlit run app.py
```

**Requirements:**
- `BLACKBOX_API_KEY` in `~/.hermes/.env.local`
- LinkedIn session at `~/.hermes/.linkedin_session.pkl` (set once, reused forever)
- ScrapeGraphAI repo at `~/Scrapegraph-ai` (git clone, no pip install needed)

---

## Modes

### 🎯 Analyze Application
Paste resume + job description → get match score, interview questions, cover letter.
- **JD Input:** Paste text directly, or enter a URL and ScrapeGraphAI extracts it automatically
- Supports any job board: LinkedIn, Greenhouse, Lever, Ashby, Indeed, Naukri, etc.

### 🔍 LinkedIn Job Search
Search LinkedIn jobs using your authenticated session — no LinkedIn API key needed.
- Keywords + location filter
- Quick-select buttons for common searches
- Jobs ranked by relevance score

### 👤 LinkedIn Profile
Scrape any LinkedIn profile using the authenticated session.
- Get recruiter/hiring manager details for outreach

### 📋 Application Tracker
Track every job through: Evaluated → Applied → Interviewing → Offer/Rejected.

### 💼 Pipeline (URL Inbox)
Queue job URLs, then run the full evaluation pipeline on all of them at once.

---

## Pipeline Flow

```
LinkedIn Job Search (playwright)
         ↓
  Job Queue (pipeline.md)
         ↓
JD Extraction (ScrapeGraphAI + Kimi)
         ↓
Resume Analysis (CrewAI agent)
JD Analysis (CrewAI agent)
         ↓
Match Scoring (CrewAI agent)
         ↓
Interview Prep (CrewAI agent)
Cover Letter (CrewAI agent)
         ↓
Application Tracker (data/applications.md)
```

---

## Project Structure

```
job-application-agent/
├── app.py                      # Streamlit UI (5 modes)
├── config.py                   # API keys, model config
├── requirements.txt
├── config/
│   └── profile.yml.template # Your profile (targets, proof points, comp) — EDIT THIS
├── data/
│   ├── applications.md         # Application tracker
│   ├── pipeline.md             # Job URL inbox
│   ├── follow-ups.md           # Outreach tracking
│   └── scan-history.tsv        # LinkedIn scan history
├── interview-prep/
│   └── story-bank.md           # STAR+R story bank
├── src/
│   ├── agents/
│   │   ├── resume_analyzer.py
│   │   ├── jd_analyzer.py
│   │   ├── match_maker.py
│   │   ├── interview_coach.py
│   │   ├── cover_letter_agent.py
│   │   ├── jd_scraper_agent.py      # NEW: ScrapeGraphAI JD extraction
│   │   └── linkedin_scraper_agent.py # NEW: LinkedIn job + profile search
│   ├── crew/
│   │   └── crew_setup.py            # UPDATED: registers all agents
│   ├── linkedin/
│   │   ├── __init__.py
│   │   ├── client.py                 # Playwright session client
│   │   ├── scrape_utils.py          # ScrapeGraphAI + Kimi integration
│   │   ├── linkedin_search.py
│   │   └── outreach.py              # Connection request message templates
│   └── utils/
│       └── prompts.py
```

---

## Key Features

**ScrapeGraphAI Integration**
- Uses SmartScraperGraph from local repo with Kimi as the LLM
- Works without an SGAI API key — just your BlackBox key
- Supports: LinkedIn, Greenhouse, Lever, Ashby, Indeed, Naukri, AngelList, any job board

**LinkedIn Session Reuse**
- Login once → session cookie saved at `~/.hermes/.linkedin_session.pkl`
- All future runs use the saved session — no re-login needed
- Scrapes job listings AND profiles

**career-ops Pipeline Adoption**
- Full application tracker (A-G evaluation format from career-ops)
- Portal scanning (Greenhouse, Lever, Ashby API support)
- Star+R interview prep with story bank
- 7-day follow-up cadence with LinkedIn DM + email touch points

---

## Environment Variables

```bash
# In ~/.hermes/.env.local
BLACKBOX_API_KEY=your_key_here
```

---

## Credits

- CrewAI multi-agent framework
- ScrapeGraphAI (local install from https://github.com/ScrapeGraphAI/Scrapegraph-ai)
- career-ops framework (https://github.com/santifer/career-ops)
- Kimi/Kimi-large via BlackBox API