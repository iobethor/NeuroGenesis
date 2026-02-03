#!/bin/bash

# NeuroGenesis - Complete Setup and Run Script
# This is the ONE SCRIPT that does everything - setup and run

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

clear

echo -e "${MAGENTA}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🧠  N E U R O G E N E S I S  🧠                ║
║                                                           ║
║          Complete Setup and Launch Script                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}This script will:${NC}"
echo "  1. Check system requirements"
echo "  2. Create virtual environment"
echo "  3. Install all dependencies"
echo "  4. Setup project structure"
echo "  5. Launch NeuroGenesis"
echo ""

# Ask for confirmation
read -p "Continue? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1/5: Checking System Requirements${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  • macOS: brew install python3"
    echo "  • Windows: Download from python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠ pip3 not found. Installing...${NC}"
    python3 -m ensurepip --upgrade
fi
echo -e "${GREEN}✓ pip3 installed${NC}"

# Check git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✓ ${GIT_VERSION}${NC}"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2/5: Creating Virtual Environment${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3/5: Installing Dependencies${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies (this may take a few minutes)..."
    echo -e "${BLUE}(Installing PyTorch, Transformers, and other ML libraries)${NC}"
    
    # Install dependencies with progress
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4/5: Setting Up Project Structure${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create directories
echo "Creating project directories..."
mkdir -p data
mkdir -p logs
mkdir -p models
mkdir -p config
mkdir -p src/core
mkdir -p src/memory
mkdir -p src/utils
mkdir -p tests

# Create __init__.py files
touch src/__init__.py
touch src/core/__init__.py
touch src/memory/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

echo -e "${GREEN}✓ Project structure created${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env configuration file..."
    cat > .env << EOF
# NeuroGenesis Configuration
DEBUG=True
LOG_LEVEL=INFO
DATA_DIR=./data
MODELS_DIR=./models
LOGS_DIR=./logs
EOF
    echo -e "${GREEN}✓ Configuration file created${NC}"
else
    echo -e "${GREEN}✓ Configuration file exists${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
.env.local
data/
logs/
models/*.pth
models/*.pt
models/*.h5
*.log

# OS
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}✓ .gitignore created${NC}"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 5/5: Launching NeuroGenesis${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}Starting NeuroGenesis...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the application
python3 src/main.py "$@"

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ NeuroGenesis completed successfully${NC}"
    echo ""
    echo -e "${BLUE}To run again, simply execute:${NC}"
    echo -e "  ${YELLOW}./start.sh${NC}"
    echo ""
    echo "Or use separate scripts:"
    echo -e "  ${YELLOW}./run.sh${NC}     - Run without setup"
    echo -e "  ${YELLOW}make run${NC}     - Run using Makefile"
else
    echo -e "${RED}❌ NeuroGenesis exited with code ${EXIT_CODE}${NC}"
fi

exit $EXIT_CODE
