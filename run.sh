#!/bin/bash
# Quick start script for WIFIjam

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╦ ╦╦╔═╗╦ ╦┌─┐┌┬┐"
echo "║║║║╠╣ ║ ║├─┤│││"
echo "╚╩╝╩╚  ╩ ╩┴ ┴┴ ┴"
echo "WiFi Security Testing Tool v2.0"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Not running as root. Some features may not work.${NC}"
    echo -e "${YELLOW}   Run with: sudo ./run.sh${NC}"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}❌ Python 3.8+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Check if dependencies are installed
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed. Installing...${NC}"
    pip3 install -r requirements.txt
fi

# Check system dependencies
echo ""
echo "Checking system dependencies..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 not found${NC}"
        return 1
    fi
}

check_command "airmon-ng" || echo "   Install: sudo apt-get install aircrack-ng"
check_command "airodump-ng" || echo "   Install: sudo apt-get install aircrack-ng"
check_command "aireplay-ng" || echo "   Install: sudo apt-get install aircrack-ng"
check_command "iw" || echo "   Install: sudo apt-get install iw"

echo ""
echo -e "${BLUE}Starting WIFIjam...${NC}"
echo ""

# Run the application
python3 -m wifijam.cli gui "$@"

