#!/usr/bin/env pwsh
# Pre-commit validation for ThetaAI - Software Factory
# Runs all quality gates before allowing commits

$ErrorActionPreference = "Stop"
$exitCode = 0
$workspace = Split-Path -Parent $PSScriptRoot

Write-Host "=== ThetaAI Pre-Commit Validation ===" -ForegroundColor Cyan

# 1. Check package-lock.json exists
Write-Host "`n[1/7] Checking package-lock.json..." -ForegroundColor Yellow
if (-not (Test-Path "$workspace/frontend/package-lock.json")) {
    Write-Host "FAIL: frontend/package-lock.json missing" -ForegroundColor Red
    $exitCode = 1
} else {
    Write-Host "PASS" -ForegroundColor Green
}

# 2. TypeScript strict check
Write-Host "`n[2/7] TypeScript strict check..." -ForegroundColor Yellow
Push-Location "$workspace/frontend"
try {
    $tscOutput = npx tsc --noEmit 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $tscOutput -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 3. ESLint
Write-Host "`n[3/7] ESLint check..." -ForegroundColor Yellow
Push-Location "$workspace/frontend"
try {
    $eslintOutput = npx eslint src/ --max-warnings=0 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $eslintOutput -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 4. Backend ruff lint
Write-Host "`n[4/7] Backend ruff lint..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    $ruffOutput = python -m ruff check backend/ 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $ruffOutput -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 5. Frontend tests
Write-Host "`n[5/7] Frontend tests..." -ForegroundColor Yellow
Push-Location "$workspace/frontend"
try {
    $testOutput = npm test 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host ($testOutput | Select-Object -Last 20) -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 6. Backend tests
Write-Host "`n[6/7] Backend tests..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    $pytestOutput = python -m pytest backend/tests/ -x -q --tb=short 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host ($pytestOutput | Select-Object -Last 20) -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 7. Backend security scan
Write-Host "`n[7/7] Security scan (bandit)..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    $banditOutput = python -m bandit -r backend/ -ll --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $banditOutput -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# Summary
Write-Host "`n=== Pre-Commit Result ===" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
} else {
    Write-Host "SOME CHECKS FAILED - Commit blocked" -ForegroundColor Red
}
exit $exitCode
