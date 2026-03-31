#!/usr/bin/env pwsh
# Quick Pre-Commit Check for ThetaAI - Critical Issues Only
# Use this for fast feedback before actual commits

$ErrorActionPreference = "Continue"
$exitCode = 0
$workspace = Split-Path -Parent $PSScriptRoot

Write-Host "=== ThetaAI Quick Pre-Commit Check ===" -ForegroundColor Cyan

# 1. Backend critical lint only
Write-Host "`n[1/3] Backend critical lint..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    # Only check for actual Python errors (E,F,I rules)
    $ruffOutput = python -m ruff check backend/ --select E,F,I --ignore E501,E722,B008,UP042,S105,S603,N806,B007 2>&1
    if ($LASTEXITCODE -ne 0 -and $ruffOutput -match 'error:') {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $ruffOutput | Select-Object -First 10 -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# 2. Security scan (critical)
Write-Host "`n[2/3] Security scan (bandit)..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    $banditCheck = python -m bandit --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        # Run bandit and check for HIGH severity issues only
        $banditOutput = python -m bandit -r backend/ --skip B101,B105 -ll 2>&1
        # Check if there are any actual high severity findings (not just confidence)
        if ($banditOutput -match 'Severity: High') {
            $exitCode = 1
            Write-Host "FAIL - High severity security issues found" -ForegroundColor Red
            Write-Host $banditOutput | Select-String -Pattern "Severity: High" | Select-Object -First 3 -ForegroundColor Red
        } else {
            Write-Host "PASS" -ForegroundColor Green
        }
    } else {
        Write-Host "SKIP - bandit not installed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "SKIP - bandit not available" -ForegroundColor Yellow
}
Pop-Location

# 3. Quick backend smoke test
Write-Host "`n[3/3] Backend smoke test..." -ForegroundColor Yellow
Push-Location "$workspace"
try {
    # Run just a few critical tests
    $testOutput = python -m pytest backend/tests/test_exceptions.py -q --tb=no 2>&1
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host $testOutput | Select-Object -Last 5 -ForegroundColor Red
    } else {
        Write-Host "PASS" -ForegroundColor Green
    }
} catch {
    $exitCode = 1
    Write-Host "FAIL: $_" -ForegroundColor Red
}
Pop-Location

# Summary
Write-Host "`n=== Result ===" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "ALL CRITICAL CHECKS PASSED" -ForegroundColor Green
    Write-Host "Ready to commit!" -ForegroundColor Cyan
} else {
    Write-Host "CRITICAL ISSUES FOUND" -ForegroundColor Red
    Write-Host "Fix issues before committing" -ForegroundColor Yellow
}
exit $exitCode
