"""
JobMind - AI Job Application & Interview Prep Agent
Main Streamlit Application

This app takes a resume and job description as input, analyzes skills match,
identifies gaps, generates interview questions with model answers, and
optionally generates cover letters.
"""

import streamlit as st
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import configuration
import config

# Import crew setup
from crew.crew_setup import JobMindCrew, create_crew


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom dark theme styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F1F5F9 !important;
    }
    
    /* Cards and containers */
    .analysis-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Match score styling */
    .match-excellent { color: #22C55E; font-weight: bold; }
    .match-good { color: #84CC16; font-weight: bold; }
    .match-moderate { color: #FBBF24; font-weight: bold; }
    .match-poor { color: #EF4444; font-weight: bold; }
    
    /* Section headers */
    .section-header {
        color: #6366F1 !important;
        border-bottom: 2px solid #6366F1;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    
    /* Success/Info boxes */
    .success-box {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22C55E;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .info-box {
        background: rgba(99, 102, 241, 0.15);
        border-left: 4px solid #6366F1;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    /* Text input styling */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.9) !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        border-radius: 8px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        color: #94A3B8;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.3) !important;
        color: #F1F5F9 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.5);
        border-radius: 4px;
    }
    
    /* Download button */
    .download-btn {
        background: rgba(34, 197, 94, 0.2) !important;
        border: 1px solid #22C55E !important;
        color: #22C55E !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_key() -> bool:
    """
    Check if OpenAI API key is configured.
    
    Returns:
        bool: True if API key is present, False otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(api_key)


def parse_match_score(match_text: str) -> int:
    """
    Try to extract a numeric match score from the match analysis text.
    
    Args:
        match_text: The match analysis text
        
    Returns:
        int: Match score percentage (0-100), or 0 if not found
    """
    import re
    
    # Look for patterns like "XX/100" or "XX%" or "XX percent"
    patterns = [
        r'(\d+)/100',
        r'(\d+)%',
        r'match[:\s]+(\d+)',
        r'score[:\s]+(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, match_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score
    
    return 0  # Default if no score found


def get_match_class(score: int) -> str:
    """
    Get CSS class for match score display.
    
    Args:
        score: Match percentage
        
    Returns:
        str: CSS class name
    """
    if score >= 80:
        return "match-excellent"
    elif score >= 60:
        return "match-good"
    elif score >= 40:
        return "match-moderate"
    else:
        return "match-poor"


def format_results_for_export(results: dict) -> str:
    """
    Format all results into a single text blob for export.
    
    Args:
        results: Dictionary containing all analysis results
        
    Returns:
        str: Formatted text ready for file export
    """
    export_text = f"""
================================================================================
                        JobMind Analysis Report
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

================================================================================
                         RESUME ANALYSIS
================================================================================
{results.get('resume_analysis', 'N/A')}

================================================================================
                      JOB DESCRIPTION ANALYSIS
================================================================================
{results.get('jd_analysis', 'N/A')}

================================================================================
                          MATCH ANALYSIS
================================================================================
{results.get('match_analysis', 'N/A')}

================================================================================
                       INTERVIEW PREPARATION
================================================================================
{results.get('interview_prep', 'N/A')}

================================================================================
                            COVER LETTER
================================================================================
{results.get('cover_letter', 'Not generated')}

================================================================================
                               END OF REPORT
================================================================================
"""
    return export_text.strip()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """
    Initialize Streamlit session state variables if they don't exist.
    Used to persist data across tab switches and reruns.
    """
    if "results" not in st.session_state:
        st.session_state.results = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "jd_text" not in st.session_state:
        st.session_state.jd_text = ""
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "error_message" not in st.session_state:
        st.session_state.error_message = None


# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

def main():
    """Main application entry point."""
    
    init_session_state()
    
    # Header section
    st.markdown(f"""
    # 🎯 {config.APP_TITLE.split('—')[0]}
    *{config.APP_TITLE.split('—')[1] if '—' in config.APP_TITLE else ''}*
    """)
    
    st.markdown(config.APP_DESCRIPTION)
    
    # API Key Warning
    if not check_api_key():
        st.error("""
        ### ⚠️ OpenAI API Key Required
        
        Please configure your `.env` file with a valid OpenAI API key:
        ```
        OPENAI_API_KEY=sk-your-key-here
        ```
        
        Get your API key at: [OpenAI Platform](https://platform.openai.com/api-keys)
        
        ⚠️ Without an API key, the analysis features will not work.
        """)
        st.stop()
    
    # ===== THREE-COLUMN INPUT LAYOUT =====
    st.markdown("---")
    st.markdown("### 📥 Input Your Information")
    
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    with col1:
        st.markdown("#### 📄 Resume")
        resume_text = st.text_area(
            label="Paste your resume",
            placeholder="Paste your resume text here...\n\nExample:\nJohn Doe\njohn@email.com\n\nSummary: Experienced software engineer...\n\nSkills: Python, JavaScript, SQL...",
            height=400,
            key="resume_input"
        )
        st.session_state.resume_text = resume_text
    
    with col2:
        st.markdown("#### 📋 Job Description")
        jd_text = st.text_area(
            label="Paste job description",
            placeholder="Paste the job description here...\n\nExample:\nSoftware Engineer\n\nRequirements:\n- 3+ years experience\n- Proficiency in Python...\n\nResponsibilities:\n- Develop web applications...",
            height=400,
            key="jd_input"
        )
        st.session_state.jd_text = jd_text
    
    with col3:
        st.markdown("#### ⚙️ Options")
        
        analysis_mode = st.radio(
            "Analysis Depth",
            options=["Quick Match", "Full Analysis"],
            index=1,
            help="Quick Match: Fast analysis of skills match only.\nFull Analysis: Complete analysis + interview prep + cover letter."
        )
        
        include_cover_letter = st.checkbox(
            "Generate Cover Letter",
            value=True,
            help="Generate a personalized cover letter based on your resume and the job"
        )
        
        candidate_name = st.text_input(
            "Your Name",
            placeholder="John Doe",
            help="Used for personalized cover letter"
        )
        
        st.markdown("---")
        
        # Analyze Button
        analyze_button = st.button(
            "🚀 Analyze Application",
            use_container_width=True,
            help="Click to start the analysis"
        )
    
    # ===== RUN ANALYSIS =====
    if analyze_button:
        if not resume_text.strip():
            st.error("📄 Please enter your resume text.")
            return
        if not jd_text.strip():
            st.error("📋 Please enter the job description.")
            return
        
        # Run analysis
        with st.spinner("🔄 Initializing analysis agents..."):
            try:
                crew = create_crew()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Run full analysis
                results = {}
                
                # Step 1: Resume Analysis
                status_text.text("🔍 Analyzing resume...")
                progress_bar.progress(20)
                results["resume_analysis"] = crew.resume_analyzer.analyze(resume_text)
                
                # Step 2: JD Analysis
                status_text.text("📋 Analyzing job description...")
                progress_bar.progress(40)
                results["jd_analysis"] = crew.jd_analyzer.analyze(jd_text)
                
                # Step 3: Match Analysis
                status_text.text("🎯 Calculating match analysis...")
                progress_bar.progress(60)
                results["match_analysis"] = crew.match_maker.analyze_match(
                    resume_analysis=results["resume_analysis"],
                    jd_analysis=results["jd_analysis"],
                    original_resume=resume_text,
                    original_jd=jd_text
                )
                
                # Step 4: Interview Prep
                status_text.text("💬 Generating interview questions...")
                progress_bar.progress(80)
                results["interview_prep"] = crew.interview_coach.generate_interview_prep(
                    resume_analysis=results["resume_analysis"],
                    jd_analysis=results["jd_analysis"],
                    match_analysis=results["match_analysis"]
                )
                
                # Step 5: Cover Letter (optional)
                if include_cover_letter:
                    status_text.text("✍️ Drafting cover letter...")
                    progress_bar.progress(90)
                    results["cover_letter"] = crew.cover_letter_agent.generate_cover_letter(
                        resume_analysis=results["resume_analysis"],
                        jd_analysis=results["jd_analysis"],
                        match_analysis=results["match_analysis"],
                        candidate_name=candidate_name or "Candidate"
                    )
                else:
                    results["cover_letter"] = None
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Store results
                st.session_state.results = results
                st.session_state.analysis_complete = True
                
                st.success("🎉 Analysis complete! Check the Results tab below.")
                
            except ValueError as e:
                st.error(str(e))
                return
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return
    
    # ===== DISPLAY RESULTS =====
    if st.session_state.analysis_complete and st.session_state.results:
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")
        
        results = st.session_state.results
        
        # Create tabs for organized display
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Match Analysis",
            "📄 Full Report",
            "💬 Interview Prep",
            "✍️ Cover Letter"
        ])
        
        with tab1:
            st.markdown("### Match Analysis")
            
            # Extract and display match score prominently
            match_score = parse_match_score(results.get("match_analysis", ""))
            if match_score > 0:
                score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                with score_col2:
                    st.metric(
                        label="Overall Match Score",
                        value=f"{match_score}%",
                        delta="Candidate fit for this role"
                    )
                    
                    # Visual progress bar for score
                    st.progress(match_score / 100, text=f"Match Score: {match_score}/100")
            
            # Display match analysis text
            st.markdown(results.get("match_analysis", "No match analysis available."))
        
        with tab2:
            st.markdown("### Complete Analysis Report")
            
            # Resume Analysis
            st.markdown("#### 📄 Resume Analysis")
            st.markdown(results.get("resume_analysis", "N/A"))
            
            st.markdown("---")
            
            # JD Analysis
            st.markdown("#### 📋 Job Description Analysis")
            st.markdown(results.get("jd_analysis", "N/A"))
            
            st.markdown("---")
            
            # Match Analysis
            st.markdown("#### 🎯 Match Analysis")
            st.markdown(results.get("match_analysis", "N/A"))
        
        with tab3:
            st.markdown("### 💬 Interview Preparation")
            st.markdown(results.get("interview_prep", "No interview preparation available."))
        
        with tab4:
            if results.get("cover_letter"):
                st.markdown("### ✍️ Cover Letter")
                
                # Copy button
                st.code(results["cover_letter"], language=None)
                
                st.download_button(
                    label="📥 Download Cover Letter",
                    data=results["cover_letter"],
                    file_name="cover_letter.txt",
                    mime="text/plain",
                    help="Download the cover letter as a text file"
                )
            else:
                st.info("ℹ️ Cover letter generation was skipped. Enable it in the options to generate one.")
        
        # Export options
        st.markdown("---")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            full_report = format_results_for_export(results)
            st.download_button(
                label="📥 Download Full Report",
                data=full_report,
                file_name=f"jobmind_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                help="Export all analysis results as a text file"
            )
        
        with export_col2:
            st.caption(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 12px;">
    Built with ❤️ using Streamlit + CrewAI<br>
    Powered by OpenAI GPT-4o
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()