# 🎯 JobMind Agent

> **Multi-Agent AI Pipeline for Intelligent Job Applications**
> CrewAI-powered job search → resume tailoring → interview prep → cover letter generation — fully autonomous.

[![Stars](https://img.shields.io/github/stars/achupradeep3050/jobmind-agent?color=f5c542&style=flat-square)](https://github.com/achupradeep3050/jobmind-agent/stargazers)
[![License](https://img.shields.io/badge/License-MIT-f5c542?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-f5c542?style=flat-square&logo=python)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agentic%20AI-f5c542?style=flat-square)](https://crewai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-f5c542?style=flat-square&logo=streamlit)](https://streamlit.io)

---

## ⚡ What It Does

JobMind is a fully autonomous job application pipeline that eliminates repetitive cover-letter grinding and interview prep. Drop in a job URL or paste a description — get back a **match score**, **tailored resume points**, **cover letter**, and **interview questions** ready to use.

```
🔍 LinkedIn Search → 📋 JD Extraction → 🎯 Match Scoring → ✉️ Cover Letter → 📝 Interview Prep
```

Built with production-grade AI agent orchestration (CrewAI), real job portal scraping (ScrapeGraphAI), and a clean Streamlit UI. Designed to run locally — no API key juggling, no cloud dependencies.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI (app.py)               │
├──────────┬──────────┬───────────┬──────────────────┤
│ JD Agent │ Match    │ Cover     │ Interview        │
│ (Scrape) │ Agent    │ Letter    │ Agent            │
├──────────┴──────────┴───────────┴──────────────────┤
│          CrewAI Orchestrator (crew.py)              │
├─────────────────────────────────────────────────────┤
│  ScrapeGraphAI  ·  BlackBox/Kimi  ·  LinkedIn API   │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | CrewAI — parallel multi-agent orchestration |
| **LLM** | Kimi (via BlackBox API) — fast, cost-efficient |
| **Web Scraping** | ScrapeGraphAI — LLM-powered extraction from any job board |
| **LinkedIn** | Playwright (authenticated session, no API key needed) |
| **UI** | Streamlit — real-time agent status + results display |
| **Runtime** | Python 3.11+ |

---

## ✨ Features

### 🎯 Analyze Application
Paste any job description or URL — JobMind extracts requirements, scores your match %, generates tailored cover letter + interview Q&A instantly.

### 🔍 LinkedIn Job Search
Authenticated LinkedIn session searches — no API key required. Keywords + location filters, jobs ranked by relevance.

### 📋 Resume Tailoring
ATS-optimized point matching against job requirements. Shows exactly which resume bullets to emphasize.

### 📝 Cover Letter Generation
Custom cover letter written per application, not generic templates. Matches tone and keywords from the JD.

### 🎤 Interview Prep
Questions pulled from the JD + role context. Includes likely follow-ups and suggested answers.

### 📊 Application Tracker
Kanban-style pipeline: Evaluated → Applied → Interviewing → Offer / Rejected. CSV export.

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11+
python --version   # ≥ 3.11 recommended

# BlackBox API key (free tier works)
# Save to ~/.hermes/.env.local:
# BLACKBOX_API_KEY=your_key_here
```

### 1. Install Dependencies
```bash
pip install crewai streamlit scrapegraph-ai playwright python-dotenv
python -m playwright install chromium
```

### 2. Authenticate LinkedIn (one-time)
```bash
# Run once — opens browser for you to log in, session auto-saved
python scripts/linkedin_auth.py
```

### 3. Launch
```bash
PYTHONPATH=src streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) — paste a job URL and watch the agents work.

---

## 📁 Project Structure

```
jobmind-agent/
├── app.py              # Streamlit UI entrypoint
├── src/
│   ├── agents.py       # CrewAI agent definitions
│   ├── tasks.py        # Task definitions per agent
│   └── tools/          # ScrapeGraphAI + LinkedIn tools
├── config/
│   └── profile.yml     # Your resume/contact info
├── scripts/
│   └── linkedin_auth.py
├── requirements.txt
└── README.md
```

---

## 🧪 Sample Output

**Input:** LinkedIn Job URL for "Senior DevOps Engineer"
**Output:**
- ✅ Match Score: **84%**
- 📝 5 tailored resume bullets matched to JD keywords
- ✉️ Custom cover letter (250 words, ATS-optimized)
- 🎤 8 likely interview questions with suggested answers
- ⏱️ Total time: ~45 seconds

---

## 🤝 Contributing

Open to contributions — PRs welcome. Key areas to contribute:
- Additional job portal integrations (Indeed, Naukri, Greenhouse)
- More interview prep question banks
- PDF resume parsing
- Multi-language support

---

## 📬 Contact

**Achu Pradeep** · Linux DevOps Engineer & AI Developer  
🔗 [LinkedIn](https://linkedin.com/in/achu-pradeep-702667404) · 📧 achupradeep3050@gmail.com

---

*Built with CrewAI + ScrapeGraphAI · Production-ready agentic workflows*