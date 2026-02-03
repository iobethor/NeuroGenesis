#!/bin/bash

# NeuroGenesis Run Script
# This script runs the NeuroGenesis application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 NeuroGenesis - Growing Mind${NC}"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run setup first: ./setup.sh${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Loading environment variables${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if main.py exists
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}❌ src/main.py not found!${NC}"
    echo -e "${YELLOW}Creating a basic main.py file...${NC}"
    
    cat > src/main.py << 'EOF'
#!/usr/bin/env python3
"""
NeuroGenesis - Growing Mind with Active Semantic Memory
Main entry point
"""

import os
import sys
from pathlib import Path

def main():
    print("🧠 NeuroGenesis - Growing Mind")
    print("=" * 50)
    print()
    print("Welcome to NeuroGenesis!")
    print("This is a project for creating a 'growing mind' with active semantic memory.")
    print()
    
    # Check directories
    data_dir = Path(os.getenv('DATA_DIR', './data'))
    models_dir = Path(os.getenv('MODELS_DIR', './models'))
    logs_dir = Path(os.getenv('LOGS_DIR', './logs'))
    
    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Models directory: {models_dir}")
    print(f"📁 Logs directory: {logs_dir}")
    print()
    
    print("✅ System initialized successfully!")
    print()
    print("Next steps:")
    print("1. Implement core semantic memory system in src/memory/")
    print("2. Add neural network components in src/core/")
    print("3. Create training scripts")
    print("4. Add data processing utilities")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
    chmod +x src/main.py
fi

# Run the application
echo -e "${GREEN}✓ Starting NeuroGenesis...${NC}"
echo ""

python3 src/main.py "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ NeuroGenesis completed successfully${NC}"
else
    echo -e "${RED}❌ NeuroGenesis exited with code ${EXIT_CODE}${NC}"
fi

exit $EXIT_CODE
