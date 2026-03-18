#!/usr/bin/env pwsh
# Pre-commit check script for AI Software Factory
# Run this before committing to catch common errors early

$ErrorActionPreference = "Stop"
$hasErrors = $false

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Software Factory - Pre-Commit Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend" -PathType Container) -or -not (Test-Path "frontend" -PathType Container)) {
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
    $result = python -m py_compile $file.FullName 2>&1
    if ($LASTEXITCODE -ne 0) {
        $syntaxErrors += $file.FullName
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

# 2. Check for f-string backslashes (common Python error)
Write-Host "Checking for invalid f-string backslashes..." -NoNewline
$fstringIssues = Select-String -Path "backend\*.py" -Pattern "f[`"'].*\\.*[`"']" -ErrorAction SilentlyContinue
if ($null -eq $fstringIssues) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Found potential f-string backslash issues:" -ForegroundColor Red
    $hasErrors = $true
}

# 3. Check imports in __init__.py files
Write-Host "Checking __init__.py imports..." -NoNewline
$initFiles = Get-ChildItem -Path "backend" -Filter "__init__.py" -Recurse
$importErrors = @()
foreach ($file in $initFiles) {
    $content = Get-Content $file.FullName -Raw
    # Check for imports that might not exist
    if ($content -match "from\s+(\S+)\s+import") {
        $matches = [regex]::Matches($content, "from\s+(\S+)\s+import")
        foreach ($match in $matches) {
            $module = $match.Groups[1].Value
            # Skip standard library and known external packages
            if ($module -notmatch "^(backend|tests|typing|os|sys|json|re|datetime|pathlib|asyncio|enum|uuid|logging|collections|functools|inspect|hashlib|base64|time|random|string|math|itertools|contextlib|dataclasses|abc|types|warnings|traceback|copy|pickle|io|tempfile|shutil|subprocess|urllib|http|email|csv|xml|html|json|decimal|fractions|numbers|statistics|hashlib|hmac|secrets|bisect|heapq|queue|array|struct|codecs|unicodedata|stringprep|readline|rlcompleter|site|sysconfig|platform|errno|signal|threading|multiprocessing|concurrent|socket|selectors|ssl|asyncio|mimetypes|netrc|ftplib|poplib|imaplib|nntplib|smtplib|smtpd|telnetlib|uuid|ipaddress|macpath|cgi|cgitb|wsgiref|http|http\.server|http\.client|http\.cookies|http\.cookiejar|xmlrpc|xmlrpc\.client|xmlrpc\.server|ipaddress|webbrowser|wsgiref|wsgiref\.handlers|wsgiref\.headers|wsgiref\.simple_server|wsgiref\.util|wsgiref\.validate|xdrlib|plistlib|crypt|spwd|grp|pwd|termios|tty|pty|fcntl|pipes|posix|pwd|spwd|grp|crypt|termios|tty|pty|fcntl|resource|syslog|optparse|imp)$") {
                # Check if it's a local backend module
                if ($module -match "^backend\.") {
                    $modulePath = $module -replace "\.", "\"
                    $fullPath = Join-Path "backend" "$modulePath.py"
                    $initPath = Join-Path "backend" "$modulePath\__init__.py"
                    if (-not (Test-Path $fullPath) -and -not (Test-Path $initPath)) {
                        $importErrors += "$($file.FullName): $module"
                    }
                }
            }
        }
    }
}
if ($importErrors.Count -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    foreach ($err in $importErrors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
    $hasErrors = $true
}

# 4. Run Python tests (quick check)
Write-Host "Running Python tests..." -NoNewline
Push-Location backend
$testResult = python -m pytest tests/ -x -q --tb=no 2>&1
$testExitCode = $LASTEXITCODE
Pop-Location
if ($testExitCode -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Run 'pytest tests/' for details" -ForegroundColor Yellow
    $hasErrors = $true
}

Write-Host ""

# ==================== FRONTEND CHECKS ====================
Write-Host "FRONTEND CHECKS" -ForegroundColor Yellow
Write-Host "---------------" -ForegroundColor Yellow

Push-Location frontend

# 1. Check if node_modules exists
Write-Host "Checking node_modules..." -NoNewline
if (Test-Path "node_modules" -PathType Container) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " MISSING" -ForegroundColor Yellow
    Write-Host "  Run 'npm install' in frontend directory" -ForegroundColor Yellow
}

# 2. Check TypeScript compilation
Write-Host "Checking TypeScript compilation..." -NoNewline
$tscResult = npx tsc --noEmit 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  TypeScript errors found" -ForegroundColor Red
    $hasErrors = $true
}

# 3. Run ESLint
Write-Host "Running ESLint..." -NoNewline
$eslintResult = npm run lint 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  ESLint errors found" -ForegroundColor Red
    $hasErrors = $true
}

# 4. Check for common frontend issues
Write-Host "Checking for common frontend issues..." -NoNewline
$issues = @()

# Check for 'any' types in TypeScript
$anyTypes = Select-String -Path "src\*.ts", "src\*.tsx" -Pattern ":\s*any" -ErrorAction SilentlyContinue
if ($anyTypes) {
    $issues += "Found 'any' types in TypeScript files"
}

# Check for missing lib/utils.ts
if (-not (Test-Path "src\lib\utils.ts")) {
    $issues += "Missing src/lib/utils.ts (required for shadcn/ui)"
}

# Check for missing types
if (-not (Test-Path "src\lib\types\index.ts")) {
    $issues += "Missing src/lib/types/index.ts"
}

if ($issues.Count -eq 0) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
    $hasErrors = $true
}

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($hasErrors) {
    Write-Host "  CHECKS FAILED - Fix errors before committing" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "  ALL CHECKS PASSED - Ready to commit!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    exit 0
}
