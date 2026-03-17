#!/usr/bin/env pwsh
# Pre-commit check script for AI Software Factory

$ErrorActionPreference = "Stop"
$hasErrors = $false

Write-Host "========================================"
Write-Host "  AI Software Factory - Pre-Commit Check"
Write-Host "========================================"
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "ERROR: Must run from project root directory" -ForegroundColor Red
    exit 1
}

# ==================== BACKEND CHECKS ====================
Write-Host "BACKEND CHECKS" -ForegroundColor Yellow
Write-Host "--------------" -ForegroundColor Yellow

# 1. Check Python syntax
Write-Host "Checking Python syntax..." -NoNewline
$pyFiles = Get-ChildItem -Path "backend" -Filter "*.py" -Recurse | Where-Object { $_.FullName -notmatch "__pycache__" }
$syntaxErrors = @()
foreach ($file in $pyFiles) {
    try {
        $null = python -m py_compile $file.FullName 2>&1
    } catch {
        $syntaxErrors += $file.Name
    }
}
if ($syntaxErrors.Count -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    foreach ($err in $syntaxErrors) {
        Write-Host "  - Syntax error in: $err" -ForegroundColor Red
    }
    $hasErrors = $true
}

# 2. Run Python tests
Write-Host "Running Python tests..." -NoNewline
Push-Location backend
$testResult = python -m pytest tests/ -x -q --tb=no 2>&1
$testExitCode = $LASTEXITCODE
Pop-Location
if ($testExitCode -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# ==================== FRONTEND CHECKS ====================
Write-Host "FRONTEND CHECKS" -ForegroundColor Yellow
Write-Host "---------------" -ForegroundColor Yellow

Push-Location frontend

# 1. Check TypeScript compilation
Write-Host "Checking TypeScript compilation..." -NoNewline
$npxResult = npx tsc --noEmit 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $hasErrors = $true
}

# 2. Run ESLint
Write-Host "Running ESLint..." -NoNewline
$eslintResult = npm run lint -- --max-warnings=999 2>&1
$eslintExitCode = $LASTEXITCODE
# Check if there are actual errors (not just warnings)
$hasErrorsOnly = $eslintResult | Select-String "error" | Where-Object { $_ -notmatch "warning" }
if ($eslintExitCode -eq 0 -or $null -eq $hasErrorsOnly) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $hasErrors = $true
}

Pop-Location

Write-Host ""
Write-Host "========================================"

if ($hasErrors) {
    Write-Host "  CHECKS FAILED - Fix errors before committing" -ForegroundColor Red
    Write-Host "========================================"
    exit 1
} else {
    Write-Host "  ALL CHECKS PASSED - Ready to commit!" -ForegroundColor Green
    Write-Host "========================================"
    exit 0
}
