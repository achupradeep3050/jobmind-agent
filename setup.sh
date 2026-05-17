#!/bin/bash
# =============================================================================
# JobMind Setup Script
# Automated installation and setup for JobMind application
# Uses Python 3.11 from Hermes venv + Blackbox/Kimi integration
# =============================================================================

set -e

echo "🎯 JobMind Setup Script"
echo "======================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect Python 3.11
if [ -f "/Users/achu/.hermes/hermes-agent/venv/bin/python3.11" ]; then
    PYTHON="/Users/achu/.hermes/hermes-agent/venv/bin/python3.11"
    PIP="/Users/achu/.hermes/hermes-agent/venv/bin/python3.11 -m pip"
elif command -v python3.11 &> /dev/null; then
    PYTHON="python3.11"
    PIP="python3.11 -m pip"
else
    echo -e "${RED}ERROR: Python 3.11 not found!${NC}"
    echo "JobMind requires Python 3.10+ (recommended: Python 3.11)"
    exit 1
fi

echo -e "${GREEN}✓ Using Python: ${PYTHON}${NC}"

# Step 1: Create virtual environment
echo -e "${YELLOW}Step 1:${NC} Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi
$PYTHON -m venv venv
source venv/bin/activate

echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Step 2: Upgrade pip
echo -e "${YELLOW}Step 2:${NC} Upgrading pip..."
pip install --upgrade pip --quiet

echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${YELLOW}Step 3:${NC} Installing dependencies..."
pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Setup environment file
echo -e "${YELLOW}Step 4:${NC} Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env from template${NC}"
    echo ""
    echo -e "${YELLOW}NOTE:${NC} Your Blackbox API key should already be configured in:"
    echo "   ~/.hermes/.env (BLACKBOX_API_KEY)"
    echo ""
    echo "To use it, either:"
    echo "   1. Symlink: ln -sf ~/.hermes/.env .env"
    echo "   2. Or manually add BLACKBOX_API_KEY to ~/projects/job-application-agent/.env"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Link your Blackbox API key:"
echo "   ln -sf ~/.hermes/.env .env"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run app.py"
echo ""
echo "Or use this one-liner:"
echo "   ln -sf ~/.hermes/.env .env && source venv/bin/activate && streamlit run app.py"
echo ""