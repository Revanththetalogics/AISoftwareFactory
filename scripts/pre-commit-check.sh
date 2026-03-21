#!/bin/bash
# Pre-commit validation for ThetaAI - Software Factory
# Runs all quality gates before allowing commits

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

exit_code=0
workspace="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo -e "${CYAN}=== ThetaAI Pre-Commit Validation ===${NC}"

# 1. Check package-lock.json exists
echo -e "\n${YELLOW}[1/7] Checking package-lock.json...${NC}"
if [ ! -f "$workspace/frontend/package-lock.json" ]; then
    echo -e "${RED}FAIL: frontend/package-lock.json missing${NC}"
    exit_code=1
else
    echo -e "${GREEN}PASS${NC}"
fi

# 2. TypeScript strict check
echo -e "\n${YELLOW}[2/7] TypeScript strict check...${NC}"
cd "$workspace/frontend"
if npx tsc --noEmit 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi
cd "$workspace"

# 3. ESLint
echo -e "\n${YELLOW}[3/7] ESLint check...${NC}"
cd "$workspace/frontend"
if npx eslint src/ --max-warnings=0 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi
cd "$workspace"

# 4. Backend ruff lint
echo -e "\n${YELLOW}[4/7] Backend ruff lint...${NC}"
cd "$workspace"
if python -m ruff check backend/ 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi

# 5. Frontend tests
echo -e "\n${YELLOW}[5/7] Frontend tests...${NC}"
cd "$workspace/frontend"
if npm test 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi
cd "$workspace"

# 6. Backend tests
echo -e "\n${YELLOW}[6/7] Backend tests...${NC}"
cd "$workspace"
if python -m pytest backend/tests/ -x -q --tb=short 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi

# 7. Backend security scan
echo -e "\n${YELLOW}[7/7] Security scan (bandit)...${NC}"
cd "$workspace"
if python -m bandit -r backend/ -ll --quiet 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit_code=1
fi

# Summary
echo -e "\n${CYAN}=== Pre-Commit Result ===${NC}"
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}ALL CHECKS PASSED${NC}"
else
    echo -e "${RED}SOME CHECKS FAILED - Commit blocked${NC}"
fi
exit $exit_code
