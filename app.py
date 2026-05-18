"""
JobMind 2.0 — Unified AI Job Application Agent
Full pipeline: LinkedIn job search → JD extraction → Match analysis → CV generation → Interview prep
Powered by Kimi (BlackBox) + CrewAI + ScrapeGraphAI + LinkedIn session
"""

import streamlit as st
import os
import sys
import asyncio
from datetime import datetime
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import config
from crew.crew_setup import create_crew, JobMindCrew
from linkedin.client import LinkedInClient

# ── Resume extraction helpers ──────────────────────────────────────────────────
def extract_resume_text(uploaded_file) -> str:
    """Extract text from uploaded PDF or DOCX file."""
    fname = uploaded_file.name.lower()
    try:
        if fname.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(uploaded_file.read()))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif fname.endswith((".docx", ".doc")):
            from docx import Document
            doc = Document(BytesIO(uploaded_file.read()))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            return uploaded_file.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Could not extract text from {fname}: {e}]"

st.set_page_config(
    page_title="JobMind 2.0 — AI Job Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark theme styles ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); }
h1, h2, h3 { color: #F1F5F9 !important; }
.analysis-card {
    background: rgba(30, 41, 59, 0.8);
    border-radius: 12px; padding: 20px; margin: 10px 0;
    border: 1px solid rgba(99, 102, 241, 0.3);
}
.match-excellent { color: #22C55E; font-weight: bold; }
.match-good { color: #84CC16; font-weight: bold; }
.match-moderate { color: #FBBF24; font-weight: bold; }
.match-poor { color: #EF4444; font-weight: bold; }
.section-header { color: #6366F1 !important; border-bottom: 2px solid #6366F1; padding-bottom: 8px; margin-bottom: 16px; }
.success-box { background: rgba(34, 197, 94, 0.15); border-left: 4px solid #22C55E; padding: 12px; border-radius: 4px; margin: 10px 0; }
.info-box { background: rgba(99, 102, 241, 0.15); border-left: 4px solid #6366F1; padding: 12px; border-radius: 4px; margin: 10px 0; }
.stTextArea textarea {
    background: rgba(15, 23, 42, 0.9) !important;
    color: #F1F5F9 !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: white !important; border: none; border-radius: 8px;
    padding: 12px 24px; font-weight: 600; transition: all 0.3s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 12px; }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px; padding: 8px 16px; color: #94A3B8; }
.stTabs [aria-selected="true"] { background: rgba(99, 102, 241, 0.3) !important; color: #F1F5F9 !important; }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.5); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def check_api_key() -> bool:
    return bool(os.getenv("BLACKBOX_API_KEY", "").strip())

def parse_match_score(text: str) -> int:
    import re
    for pat in [r"(\d+)/100", r"(\d+)%", r"match[:\s]+(\d+)", r"score[:\s]+(\d+)"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            v = int(m.group(1))
            if 0 <= v <= 100:
                return v
    return 0

def score_class(score: int) -> str:
    if score >= 80: return "match-excellent"
    elif score >= 60: return "match-good"
    elif score >= 40: return "match-moderate"
    return "match-poor"

def fmt_results(results: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
================================================================================
                    JobMind 2.0 — Analysis Report
                            {ts}
================================================================================

RESUME ANALYSIS
{results.get('resume_analysis', 'N/A')}

JOB DESCRIPTION ANALYSIS
{results.get('jd_analysis', 'N/A')}

MATCH ANALYSIS
{results.get('match_analysis', 'N/A')}

INTERVIEW PREPARATION
{results.get('interview_prep', 'N/A')}

COVER LETTER
{results.get('cover_letter', 'Not generated')}
================================================================================
"""

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "results": None,
        "resume_text": "",
        "jd_text": "",
        "linkedin_jobs": [],
        "selected_job": None,
        "analysis_complete": False,
        "job_search_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar navigation ─────────────────────────────────────────────────────────
st.sidebar.markdown("### 🎯 JobMind 2.0")
mode = st.sidebar.radio("Mode", [
    "🤖 Analyze Application",
    "🔍 LinkedIn Job Search",
    "📋 Application Tracker",
    "💼 Pipeline (URL Inbox)",
    "👤 LinkedIn Profile",
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Stack:** Kimi · CrewAI · ScrapeGraphAI · LinkedIn")

# ══════════════════════════════════════════════════════════════════════════════
# MODE 1: ANALYZE APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
if mode == "🤖 Analyze Application":
    st.markdown("# 🤖 JobMind — Analyze Application")
    st.markdown("*Paste your resume + job description to get match score, interview prep & cover letter*")

    if not check_api_key():
        st.error("⚠️ Missing `BLACKBOX_API_KEY` — set it in `.env.local`")
        st.stop()

    col1, col2, col3 = st.columns([1, 1, 1.2])

    with col1:
        st.markdown("#### 📄 Resume")
        st.markdown("**Upload your resume — PDF or Word accepted**")
        resume_file = st.file_uploader(
            "Drag & drop or browse",
            type=["pdf", "docx", "doc"],
            key="resume_upload",
            help="PDF or Word document will be automatically extracted"
        )
        if resume_file:
            with st.spinner("Extracting text..."):
                resume_text = extract_resume_text(resume_file)
                st.session_state["resume_text"] = resume_text
                st.session_state["resume_filename"] = resume_file.name
            char_count = len(resume_text)
            st.success(f"✅ Extracted {char_count:,} characters from `{resume_file.name}`")
            with st.expander("📋 Preview extracted text"):
                st.text(resume_text[:2000] + ("..." if char_count > 2000 else ""))
        else:
            resume_text = st.text_area(
                "Or paste resume text",
                placeholder="Name, Summary, Skills, Experience...",
                height=380, key="resume_paste_fallback"
            )
    with col2:
        st.markdown("#### 📋 Job Description")
        jd_options = ["Paste JD text", "Extract from URL (ScrapeGraphAI)"]
        jd_mode = st.radio("Input method", jd_options, key="jd_mode")

        if jd_mode == "Paste JD text":
            jd_text = st.text_area(
                "Paste job description",
                placeholder="Paste the full job description here...",
                height=400, key="jd_paste"
            )
        else:
            jd_url = st.text_input("Job posting URL", placeholder="https://...", key="jd_url")
            jd_text = st.text_area(
                "Or paste JD text directly",
                placeholder="Alternatively paste text here...",
                height=300, key="jd_alt"
            )
            if jd_url and not jd_text:
                with st.spinner("🔄 Extracting JD with ScrapeGraphAI..."):
                    try:
                        from linkedin.scrape_utils import extract_jd_with_scrapegraph
                        jd_text = extract_jd_with_scrapegraph(jd_url)
                        st.session_state["jd_paste"] = jd_text
                        st.success(f"✅ Extracted JD ({len(jd_text)} chars)")
                    except Exception as e:
                        st.warning(f"ScrapeGraphAI failed: {e} — paste manually")

    with col3:
        st.markdown("#### ⚙️ Options")
        include_cover = st.checkbox("Generate Cover Letter", True, key="cover_opt")
        candidate_name = st.text_input("Your Name", placeholder="Your Name", key="cname")
        st.markdown("---")
        analyze_btn = st.button("🚀 Analyze Application", use_container_width=True)

    if analyze_btn:
        if not resume_text.strip():
            st.error("📄 Please enter resume text")
            st.stop()
        effective_jd = jd_text.strip()
        if not effective_jd:
            st.error("📋 Please enter or extract a job description")
            st.stop()

        with st.spinner("Initializing crew..."):
            try:
                crew = create_crew()
                pb = st.progress(0)
                status = st.empty()
                results = {}

                steps = [
                    ("Analyzing resume...", 20),
                    ("Parsing job description...", 40),
                    ("Calculating match...", 60),
                    ("Generating interview questions...", 80),
                    ("Drafting cover letter...", 95),
                ]
                for step, pct in steps:
                    status.text(f"🔍 {step}")
                    pb.progress(pct)

                results["resume_analysis"] = crew.resume_analyzer.analyze(resume_text)
                results["jd_analysis"] = crew.jd_analyzer.analyze(effective_jd)
                results["match_analysis"] = crew.match_maker.analyze_match(
                    results["resume_analysis"], results["jd_analysis"],
                    resume_text, effective_jd
                )
                results["interview_prep"] = crew.interview_coach.generate_interview_prep(
                    results["resume_analysis"], results["jd_analysis"], results["match_analysis"]
                )
                if include_cover:
                    results["cover_letter"] = crew.cover_letter_agent.generate_cover_letter(
                        results["resume_analysis"], results["jd_analysis"], results["match_analysis"],
                        candidate_name or "Candidate"
                    )
                else:
                    results["cover_letter"] = None

                pb.progress(100)
                status.text("✅ Done!")
                st.session_state.results = results
                st.session_state.analysis_complete = True
                st.success("🎉 Analysis complete!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

    if st.session_state.analysis_complete and st.session_state.results:
        results = st.session_state.results
        score = parse_match_score(results.get("match_analysis", ""))
        sc = score_class(score)

        st.markdown("---")
        st.markdown("## 📊 Results")
        t1, t2, t3, t4 = st.tabs(["🎯 Match", "📄 Report", "💬 Interview Prep", "✍️ Cover Letter"])

        with t1:
            if score > 0:
                st.metric("Overall Match Score", f"{score}%", delta="Candidate fit")
                st.progress(score / 100, text=f"{score}/100")
                cls_col = st.columns([1, 2, 1])
                with cls_col[1]:
                    st.markdown(f'<p class="{sc}">{score}% match</p>', unsafe_allow_html=True)
            st.markdown(results.get("match_analysis", "N/A"))

        with t2:
            st.markdown(results.get("resume_analysis", ""))
            st.markdown("---")
            st.markdown(results.get("jd_analysis", ""))

        with t3:
            st.markdown(results.get("interview_prep", ""))

        with t4:
            if results.get("cover_letter"):
                st.markdown(results["cover_letter"])
                st.download_button(
                    "📥 Download Cover Letter",
                    results["cover_letter"],
                    file_name="cover_letter.txt",
                    mime="text/plain"
                )

# ══════════════════════════════════════════════════════════════════════════════
# MODE 2: LINKEDIN JOB SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "🔍 LinkedIn Job Search":
    st.markdown("# 🔍 LinkedIn Job Search")
    st.markdown("*Search LinkedIn jobs using your authenticated session*")

    if not check_api_key():
        st.error("⚠️ Missing BLACKBOX_API_KEY")
        st.stop()

    keywords = st.text_input(
        "Keywords",
        value="DevOps Engineer SRE Python",
        help="Job titles or skills to search for"
    )
    location = st.text_input("Location", value="India")

    col_kw1, col_kw2 = st.columns(2)
    with col_kw1:
        quick_searches = [
            "DevOps Engineer Python India",
            "SRE Site Reliability Engineer India",
            "Python Developer AWS Kubernetes",
            "Platform Engineer CI/CD",
            "AI ML Engineer LLM",
        ]
        for qs in quick_searches:
            if st.button(qs, key=f"qs_{qs[:15]}"):
                keywords = qs

    if st.button("🔍 Search LinkedIn Jobs", use_container_width=True):
        with st.spinner("Searching LinkedIn via browser session..."):
            try:
                jobs = asyncio.run(
                    LinkedInClient().search_jobs(keywords, location, limit=30)
                )
                st.session_state.linkedin_jobs = jobs
                st.session_state.job_search_done = True
            except Exception as e:
                st.error(f"Search failed: {e}")

    if st.session_state.job_search_done and st.session_state.linkedin_jobs:
        jobs = st.session_state.linkedin_jobs
        st.success(f"Found {len(jobs)} job listings")

        # Build table
        import pandas as pd
        rows = []
        for j in jobs:
            rows.append({
                "Title": j.get("title","")[:80],
                "Company": j.get("company","")[:50],
                "Location": j.get("location",""),
                "Posted": j.get("posted",""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("**To evaluate any job:** copy the job title + company, go to 'Analyze Application', and paste the details.")

# ══════════════════════════════════════════════════════════════════════════════
# MODE 3: APPLICATION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "📋 Application Tracker":
    st.markdown("# 📋 Applications Tracker")
    tracker_path = os.path.join(os.path.dirname(__file__), "data/applications.md")

    if os.path.exists(tracker_path):
        with open(tracker_path) as f:
            st.markdown(f.read())
    else:
        st.info("No applications tracked yet. Analyze a job to start!")

    st.markdown("---")
    st.markdown("**Add new application:**")
    nc1, nc2, nc3, nc4, nc5 = st.columns(5)
    with nc1: new_company = st.text_input("Company")
    with nc2: new_role = st.text_input("Role")
    with nc3: new_score = st.selectbox("Score", ["5/5","4/5","3/5","2/5","1/5"])
    with nc4: new_status = st.selectbox("Status", ["Evaluated","Applied","Interviewing","Offer","Rejected"])
    with nc5: st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Add to Tracker"):
        st.success("Added! (Tracker updates coming soon)")

# ══════════════════════════════════════════════════════════════════════════════
# MODE 4: PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "💼 Pipeline (URL Inbox)":
    st.markdown("# 💼 Pipeline — URL Inbox")
    st.markdown("*Add job URLs here, then run full evaluation pipeline*")
    pipeline_path = os.path.join(os.path.dirname(__file__), "data/pipeline.md")
    if os.path.exists(pipeline_path):
        with open(pipeline_path) as f:
            st.markdown(f.read())

    new_url = st.text_input("Job URL", placeholder="https://...")
    if st.button("➕ Add to Pipeline"):
        st.success("URL queued!")

# ══════════════════════════════════════════════════════════════════════════════
# MODE 5: LINKEDIN PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "👤 LinkedIn Profile":
    st.markdown("# 👤 LinkedIn Profile")
    profile_url = st.text_input(
        "Profile URL or Username",
        value="achu-pradeep-702667404",
        help="Full URL or just the username"
    )
    if st.button("🔍 Scrape Profile", use_container_width=True):
        with st.spinner("Opening LinkedIn via browser session..."):
            try:
                profile = asyncio.run(LinkedInClient().scrape_profile(profile_url))
                st.session_state.profile_data = profile
            except Exception as e:
                st.error(f"Failed: {e}")

    if "profile_data" in st.session_state:
        p = st.session_state.profile_data
        st.markdown("### Profile Data")
        st.json({
            "Name": p.get("name"),
            "Headline": p.get("headline"),
            "Location": p.get("location"),
            "Connections": p.get("connections"),
            "URL": p.get("url"),
        })
        with st.expander("📄 Raw Text (first 3000 chars)"):
            st.text(p.get("raw_text", "")[:3000])