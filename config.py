"""
Configuration module for JobMind App.
Holds settings and constants used across the application.

Uses Kimi (via Blackbox) as the LLM provider — no OpenAI needed!
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env.local first (project-specific),
# then fall back to .env (for CI/server deployments)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"), override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

# ============================================================================
# KIMI / BLACKBOX CONFIGURATION
# ============================================================================

def get_blackbox_api_key() -> str:
    """
    Retrieve the Blackbox API key from environment variables.
    
    Returns:
        str: The API key
        
    Raises:
        ValueError: If API key is not set or empty
    """
    api_key = os.getenv("BLACKBOX_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "❌ Missing BLACKBOX_API_KEY!\n\n"
            "Please set your Blackbox API key in the .env file:\n"
            "   BLACKBOX_API_KEY=your_key_here\n\n"
            "Get your Blackbox API key from: https://blackbox.ai\n"
            "(You may already have it set in ~/.hermes/.env)"
        )
    return api_key


# Alias for backwards compatibility
get_openai_api_key = get_blackbox_api_key


# ============================================================================
# CREWAI AGENT CONFIGURATION
# ============================================================================

# Agent behavior settings
AGENT_VERBOSE = True          # Enable verbose logging for debugging
MAX_RESEARCH_MINUTES = 5     # Max time for research tasks

# Model selection — Using Kimi K2.6 via Blackbox
DEFAULT_MODEL = "moonshotai/kimi-k2.6"
BLACKBOX_API_BASE = "https://api.blackbox.ai/v1"

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_TITLE = "JobMind — AI Job Application & Interview Prep Agent"
APP_ICON = "🎯"
APP_DESCRIPTION = """
**JobMind** helps you analyze job descriptions, match your resume against 
requirements, prepare for interviews, and generate professional cover letters.
"""

# Dark theme colors (for Streamlit)
THEME_PRIMARY = "#6366F1"     # Indigo
THEME_SECONDARY = "#8B5CF6"  # Purple
THEME_ACCENT = "#22C55E"     # Green for success states
THEME_BG_DARK = "#0F172A"     # Slate 900
THEME_TEXT = "#F1F5F9"       # Slate 100

# Match score thresholds
MATCH_EXCELLENT = 80
MATCH_GOOD = 60
MATCH_MODERATE = 40