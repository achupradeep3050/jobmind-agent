# 🎯 JobMind — AI Job Application & Interview Prep Agent

> Intelligent multi-agent system that helps job seekers land their dream jobs — analyzes resumes against job descriptions, scores match %, prepares for interviews, and generates cover letters automatically.

Built with **Python**, **Streamlit**, and **CrewAI** multi-agent framework. Powered by **Kimi (Moonshot AI)** via Blackbox API — no OpenAI key required.

---

## 🧠 What JobMind Does

| Agent | What It Does |
|:------|:------------|
| 📄 **Resume Analyzer** | Extracts skills, experience, achievements from any resume |
| 📋 **JD Analyzer** | Decodes job requirements, keywords, priorities |
| ���� **Match Maker** | Compares resume vs JD → match score % + gap analysis |
| 💬 **Interview Coach** | Generates targeted Q&A with model answers |
| ✍️ **Cover Letter Writer** | Creates personalized, job-specific cover letters |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     JobMind Crew                             │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐                       │
│  │ Resume       │    │ JD           │                       │
│  │ Analyzer     │    │ Analyzer     │                       │
│  └──────┬───────┘    └──────┬───────┘                       │
│         │                    │                               │
│         └────────┬───────────┘                               │
│                  ▼                                            │
│        ┌──────────────┐                                      │
│        │ Match Maker  │ ◄── Compares & Scores                 │
│        └──────┬───────┘                                      │
│               │                                               │
│   ┌───────────┴───────────┐                                  │
│   ▼                       ▼                                  │
│ ┌──────────────┐  ┌──────────────┐                          │
│ │ Interview    │  │ Cover Letter │                          │
│ │ Coach        │  │ Generator    │                          │
│ └──────────────┘  └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Kimi API key via Blackbox (free tier available at [blackboxai.com](https://blackboxai.com))

### 1. Clone & Setup

```bash
git clone https://github.com/achupradeep3050/jobmind-agent.git
cd jobmind-agent

# Use Hermes venv (already has crewai + litellm)
source /Users/achu/.hermes/hermes-agent/venv/bin/activate
```

### 2. Configure

```bash
# Copy and edit env
cp .env.example .env.local
nano .env.local

# Required vars:
# BLACKBOX_API_KEY=your_key_from_blackboxai
# DEFAULT_MODEL=moonshotai/kimi-k2.6
# BLACKBOX_API_BASE=https://api.blackbox.ai/v1
```

### 3. Run

```bash
PYTHONPATH=src streamlit run app.py
```

Open **http://localhost:8501**

---

## 📖 Usage

1. **Paste your resume** in the left panel
2. **Paste the job description** in the middle panel
3. **Click "Analyze Application"** — agents work in sequence
4. **Switch tabs** to see match analysis, interview prep, and cover letter

---

## 🗂️ Project Structure

```
jobmind-agent/
├── app.py                      # Streamlit UI
├── config.py                   # Environment + model config
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── .env.example               # Env template
├── .env.local                 # Local overrides (gitignored)
└── src/
    ├── agents/
    │   ├── resume_analyzer.py     # Extract resume data
    │   ├── jd_analyzer.py         # Parse job description
    │   ├── match_maker.py         # Score match %
    │   ├── interview_coach.py     # Generate Q&A
    │   └── cover_letter_agent.py  # Write cover letter
    ├── crew/
    │   └── crew_setup.py          # Crew orchestration (importlib)
    ├── tasks.py                   # Task definitions
    └── utils/
        └── prompts.py             # Agent prompts
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|:------|:----|
| `ModuleNotFoundError` | Use `PYTHONPATH=src` when running |
| Import errors | Use Hermes venv: `/Users/achu/.hermes/hermes-agent/venv/bin/python3.11` |
| API errors | Check `BLACKBOX_API_KEY` in `.env.local` |
| Empty results | Provide more detail in resume/JD inputs |

---

## 🤝 Contributing

Contributions welcome! Areas to improve:
- PDF/DOCX resume upload (currently text paste only)
- Result caching
- Async processing
- More agent specializations

---

## 📝 License

MIT License

---

**Built with Streamlit ❤️ and CrewAI 🤖**