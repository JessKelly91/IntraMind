#!/bin/bash
# IntraMind Integration Tests - Setup Script (Bash)
# This script creates a virtual environment and installs test dependencies

set -e

echo ""
echo "====================================="
echo " IntraMind Integration Tests Setup  "
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Python is available
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

# Check if venv already exists
if [ -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
    read -p "Do you want to recreate it? (y/N): " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf venv
    else
        echo -e "${GREEN}Keeping existing virtual environment.${NC}"
        echo ""
        echo -e "${CYAN}To activate it, run:${NC}"
        echo "  source venv/bin/activate"
        exit 0
    fi
fi

# Create virtual environment
echo ""
echo -e "${YELLOW}Creating virtual environment...${NC}"
$PYTHON_CMD -m venv venv

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Failed to create virtual environment${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo ""
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo ""
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed successfully${NC}"

# Verify installation
echo ""
echo -e "${YELLOW}Verifying installation...${NC}"
packages=("pytest" "requests" "grpcio")
all_installed=true

for package in "${packages[@]}"; do
    if pip show "$package" &> /dev/null; then
        echo -e "  ${GREEN}✓ $package${NC}"
    else
        echo -e "  ${RED}✗ $package not found${NC}"
        all_installed=false
    fi
done

# Final status
echo ""
echo "====================================="
if [ "$all_installed" = true ]; then
    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo "====================================="
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. Ensure all services are running (see README.md)"
    echo "  2. Activate the virtual environment:"
    echo -e "     ${YELLOW}source venv/bin/activate${NC}"
    echo "  3. Run tests:"
    echo -e "     ${YELLOW}pytest integration/ -v${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ Setup completed with warnings${NC}"
    echo "====================================="
    echo ""
    echo -e "${YELLOW}Some packages may not have installed correctly.${NC}"
    echo "Try running: pip install -r requirements.txt"
    echo ""
fi

