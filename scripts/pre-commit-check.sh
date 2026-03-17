#!/bin/bash
# Pre-commit check script for AI Software Factory
# Run this before committing to catch common errors early

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

has_errors=false

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  AI Software Factory - Pre-Commit Check${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}ERROR: Must run from project root directory${NC}"
    exit 1
fi

# ==================== BACKEND CHECKS ====================
echo -e "${YELLOW}BACKEND CHECKS${NC}"
echo -e "${YELLOW}--------------${NC}"

# 1. Check Python syntax
echo -n "Checking Python syntax..."
syntax_errors=()
while IFS= read -r file; do
    if ! python -m py_compile "$file" 2>/dev/null; then
        syntax_errors+=("$file")
    fi
done < <(find backend -name "*.py" -not -path "*/__pycache__/*")

if [ ${#syntax_errors[@]} -eq 0 ]; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${RED} FAIL${NC}"
    for err in "${syntax_errors[@]}"; do
        echo -e "${RED}  - Syntax error in: $err${NC}"
    done
    has_errors=true
fi

# 2. Check for f-string backslashes
echo -n "Checking for invalid f-string backslashes..."
if grep -r 'f".*\\.*"' backend --include="*.py" 2>/dev/null | grep -v '\\n\|\\t\|\\\\' | head -1 > /dev/null; then
    echo -e "${RED} FAIL${NC}"
    echo -e "${RED}  Found potential f-string backslash issues${NC}"
    has_errors=true
else
    echo -e "${GREEN} PASS${NC}"
fi

# 3. Run Python tests (quick check)
echo -n "Running Python tests..."
cd backend
if python -m pytest tests/ -x -q --tb=no 2>/dev/null; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${RED} FAIL${NC}"
    echo -e "${YELLOW}  Run 'pytest tests/' for details${NC}"
    has_errors=true
fi
cd ..

echo ""

# ==================== FRONTEND CHECKS ====================
echo -e "${YELLOW}FRONTEND CHECKS${NC}"
echo -e "${YELLOW}---------------${NC}"

cd frontend

# 1. Check if node_modules exists
echo -n "Checking node_modules..."
if [ -d "node_modules" ]; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${YELLOW} MISSING${NC}"
    echo -e "${YELLOW}  Run 'npm install' in frontend directory${NC}"
fi

# 2. Check TypeScript compilation
echo -n "Checking TypeScript compilation..."
if npx tsc --noEmit 2>/dev/null; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${RED} FAIL${NC}"
    echo -e "${RED}  TypeScript errors found${NC}"
    has_errors=true
fi

# 3. Run ESLint
echo -n "Running ESLint..."
if npm run lint 2>/dev/null; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${RED} FAIL${NC}"
    echo -e "${RED}  ESLint errors found${NC}"
    has_errors=true
fi

# 4. Check for common frontend issues
echo -n "Checking for common frontend issues..."
issues=()

# Check for 'any' types
if grep -r ":\s*any" src --include="*.ts" --include="*.tsx" 2>/dev/null | head -1 > /dev/null; then
    issues+=("Found 'any' types in TypeScript files")
fi

# Check for missing lib/utils.ts
if [ ! -f "src/lib/utils.ts" ]; then
    issues+=("Missing src/lib/utils.ts (required for shadcn/ui)")
fi

# Check for missing types
if [ ! -f "src/lib/types/index.ts" ]; then
    issues+=("Missing src/lib/types/index.ts")
fi

if [ ${#issues[@]} -eq 0 ]; then
    echo -e "${GREEN} PASS${NC}"
else
    echo -e "${RED} FAIL${NC}"
    for issue in "${issues[@]}"; do
        echo -e "${RED}  - $issue${NC}"
    done
    has_errors=true
fi

cd ..

echo ""
echo -e "${CYAN}========================================${NC}"

if [ "$has_errors" = true ]; then
    echo -e "${RED}  CHECKS FAILED - Fix errors before committing${NC}"
    echo -e "${CYAN}========================================${NC}"
    exit 1
else
    echo -e "${GREEN}  ALL CHECKS PASSED - Ready to commit!${NC}"
    echo -e "${CYAN}========================================${NC}"
    exit 0
fi
