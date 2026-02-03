#!/bin/bash

# NeuroGenesis Setup Script
# This script sets up the entire project environment

set -e

echo "🧠 NeuroGenesis Setup Script"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2 | cut -d"." -f1,2)
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠ pip3 not found. Installing pip...${NC}"
    python3 -m ensurepip --upgrade
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ No requirements.txt found, skipping dependency installation${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating project directories...${NC}"
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

echo -e "${GREEN}✓ Project directories created${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << EOF
# NeuroGenesis Configuration
DEBUG=True
LOG_LEVEL=INFO
DATA_DIR=./data
MODELS_DIR=./models
LOGS_DIR=./logs
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}📝 Creating .gitignore...${NC}"
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
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo "To start the project, run:"
echo -e "${YELLOW}  ./run.sh${NC}"
echo ""
echo "Or activate the virtual environment manually:"
echo -e "${YELLOW}  source venv/bin/activate${NC}"
