#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run all pre-commit quality checks for the ThetaAI Software Factory project.

.DESCRIPTION
    Executes the following checks in order:
      Backend  (backend/)
        1. Ruff format  -- code formatting
        2. Ruff lint    -- style, imports, security (E F W I N UP S B rules)
        3. Pytest       -- full test suite

      Frontend (frontend/)
        4. TypeScript   -- tsc --noEmit type check
        5. ESLint       -- eslint lint
        6. Vitest       -- unit test suite

    Exits with code 0 only if every check passes.

.PARAMETER BackendOnly
    Skip all frontend checks.

.PARAMETER FrontendOnly
    Skip all backend checks.

.PARAMETER SkipTests
    Skip pytest and vitest (run lint/type checks only).

.EXAMPLE
    .\scripts\pre-commit-check.ps1
    .\scripts\pre-commit-check.ps1 -BackendOnly
    .\scripts\pre-commit-check.ps1 -SkipTests
#>
param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

$script:Passed  = 0
$script:Failed  = 0
$script:Skipped = 0
$script:Results = @()

function Write-Header {
    param([string]$Title)
    $line = "-" * 60
    Write-Host ""
    Write-Host $line                  -ForegroundColor DarkGray
    Write-Host "  $Title"             -ForegroundColor Cyan
    Write-Host $line                  -ForegroundColor DarkGray
}

function Invoke-Check {
    param(
        [string]   $Name,
        [string]   $WorkDir,
        [string[]] $Cmd,
        [switch]   $Skip
    )

    if ($Skip) {
        Write-Host "  [SKIP]  $Name" -ForegroundColor DarkGray
        $script:Skipped++
        $script:Results += [PSCustomObject]@{ Name = $Name; Status = "SKIP" }
        return
    }

    Write-Host ""
    Write-Host "  Running: $($Cmd -join ' ')" -ForegroundColor DarkGray

    $prevPwd = $PWD
    Set-Location $WorkDir

    $exitCode = 0
    try {
        & $Cmd[0] $Cmd[1..($Cmd.Length - 1)]
        $exitCode = $LASTEXITCODE
    }
    catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        $exitCode = 1
    }
    finally {
        Set-Location $prevPwd
    }

    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "  [PASS]  $Name" -ForegroundColor Green
        $script:Passed++
        $script:Results += [PSCustomObject]@{ Name = $Name; Status = "PASS" }
    }
    else {
        Write-Host ""
        Write-Host "  [FAIL]  $Name  (exit $exitCode)" -ForegroundColor Red
        $script:Failed++
        $script:Results += [PSCustomObject]@{ Name = $Name; Status = "FAIL" }
    }
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir  = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host ""
Write-Host "  ThetaAI Software Factory" -ForegroundColor Magenta
Write-Host "  Pre-Commit Quality Check" -ForegroundColor White
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray

# ---------------------------------------------------------------------------
# Backend checks
# ---------------------------------------------------------------------------

if (-not $FrontendOnly) {
    Write-Header "BACKEND  (Python / FastAPI)"

    Invoke-Check `
        -Name    "Ruff -- format check" `
        -WorkDir $BackendDir `
        -Cmd     @("python", "-m", "ruff", "format", "--check", ".")

    Invoke-Check `
        -Name    "Ruff -- lint" `
        -WorkDir $BackendDir `
        -Cmd     @("python", "-m", "ruff", "check", ".")

    Invoke-Check `
        -Name    "Pytest -- test suite" `
        -WorkDir $BackendDir `
        -Cmd     @("python", "-m", "pytest", "tests/", "-q", "--tb=short") `
        -Skip:$SkipTests
}

# ---------------------------------------------------------------------------
# Frontend checks
# ---------------------------------------------------------------------------

if (-not $BackendOnly) {
    Write-Header "FRONTEND  (Next.js / TypeScript)"

    Invoke-Check `
        -Name    "TypeScript -- type check" `
        -WorkDir $FrontendDir `
        -Cmd     @("npx", "tsc", "--noEmit")

    Invoke-Check `
        -Name    "ESLint -- lint" `
        -WorkDir $FrontendDir `
        -Cmd     @("npm", "run", "lint", "--", "--max-warnings=0")

    Invoke-Check `
        -Name    "Vitest -- test suite" `
        -WorkDir $FrontendDir `
        -Cmd     @("npm", "run", "test") `
        -Skip:$SkipTests
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

$total = $script:Results.Count
$line  = "=" * 60

Write-Host ""
Write-Host $line -ForegroundColor DarkGray
Write-Host "  SUMMARY  ($total checks)" -ForegroundColor White
Write-Host $line -ForegroundColor DarkGray

foreach ($r in $script:Results) {
    switch ($r.Status) {
        "PASS" { Write-Host ("  [PASS]  " + $r.Name) -ForegroundColor Green    }
        "FAIL" { Write-Host ("  [FAIL]  " + $r.Name) -ForegroundColor Red      }
        "SKIP" { Write-Host ("  [SKIP]  " + $r.Name) -ForegroundColor DarkGray }
    }
}

Write-Host ""
Write-Host ("  Passed : " + $script:Passed)  -ForegroundColor Green
if ($script:Failed -gt 0) {
    Write-Host ("  Failed : " + $script:Failed)  -ForegroundColor Red
}
else {
    Write-Host ("  Failed : " + $script:Failed)  -ForegroundColor Green
}
Write-Host ("  Skipped: " + $script:Skipped) -ForegroundColor DarkGray
Write-Host $line -ForegroundColor DarkGray

if ($script:Failed -gt 0) {
    Write-Host ""
    Write-Host "  [FAILED]  Pre-commit check FAILED -- fix the issues above before committing." -ForegroundColor Red
    Write-Host ""
    exit 1
}
else {
    Write-Host ""
    Write-Host "  [PASSED]  All checks passed -- safe to commit." -ForegroundColor Green
    Write-Host ""
    exit 0
}
