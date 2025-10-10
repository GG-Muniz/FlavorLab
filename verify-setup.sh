#!/bin/bash

# FlavorLab Setup Verification Script
# This script checks if the project structure is correct after migration

echo "🔍 FlavorLab Setup Verification"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_exists() {
    if [ -e "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

# Project structure checks
echo "📁 Directory Structure:"
echo "----------------------"
check_dir "frontend"
check_dir "frontend/src"
check_dir "frontend/public"
check_dir "frontend/node_modules"
check_dir "backend"
check_dir "backend/app"
echo ""

# Frontend files
echo "📦 Frontend Files:"
echo "------------------"
check_exists "frontend/package.json"
check_exists "frontend/index.html"
check_exists "frontend/vite.config.js"
check_exists "frontend/.env.example"
check_exists "frontend/src/App.jsx"
echo ""

# Backend files
echo "🐍 Backend Files:"
echo "-----------------"
check_exists "backend/requirements.txt"
check_exists "backend/app/main.py"
check_exists "backend/app/config.py"
echo ""

# Root files
echo "📄 Root Configuration:"
echo "----------------------"
check_exists ".gitignore"
check_exists "README.md"
check_exists "SETUP.md"
check_exists "MIGRATION_SUMMARY.md"
echo ""

# Check API URL configuration
echo "🔗 API Configuration:"
echo "---------------------"
if grep -q "http://localhost:8000/api/v1" frontend/src/App.jsx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} API base URL configured correctly (port 8000)"
else
    echo -e "${YELLOW}⚠${NC} API base URL may need verification"
fi
echo ""

# Check node_modules
echo "📚 Dependencies:"
echo "----------------"
if [ -d "frontend/node_modules" ] && [ "$(ls -A frontend/node_modules)" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies need installation"
    echo "   Run: cd frontend && npm install"
fi

if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Backend virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC} Backend virtual environment not found"
    echo "   Run: cd backend && python -m venv venv"
fi
echo ""

# Final summary
echo "================================"
echo "📋 Next Steps:"
echo "================================"
echo ""
echo "1. If node_modules warning appeared, reinstall frontend dependencies:"
echo "   ${YELLOW}cd frontend${NC}"
echo "   ${YELLOW}rm -rf node_modules package-lock.json${NC}"
echo "   ${YELLOW}npm install${NC}"
echo ""
echo "2. Start the backend server (Terminal 1):"
echo "   ${YELLOW}cd backend${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}  # On Linux/macOS"
echo "   ${YELLOW}uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo "3. Start the frontend server (Terminal 2):"
echo "   ${YELLOW}cd frontend${NC}"
echo "   ${YELLOW}npm run dev${NC}"
echo ""
echo "4. Access the application:"
echo "   Frontend: ${GREEN}http://localhost:5173${NC}"
echo "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "For detailed setup instructions, see: ${YELLOW}SETUP.md${NC}"
echo "For migration details, see: ${YELLOW}MIGRATION_SUMMARY.md${NC}"
echo ""
