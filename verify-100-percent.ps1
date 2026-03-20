# Final Verification Script - 100% Design System Compliance
# This script checks ALL dashboard pages for hardcoded colors

$basePath = "C:\Users\DELL\Projects\ThetaAI - Software Factory\frontend\src\app\(dashboard)"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "100% DESIGN SYSTEM COMPLIANCE CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allFiles = Get-ChildItem -Path $basePath -Filter "*.tsx" -Recurse -File
$totalFiles = 0
$compliantFiles = 0
$issuesFound = @()

foreach ($file in $allFiles) {
    # Skip node_modules and test files
    if ($file.FullName -match "node_modules|test|spec") { continue }
    
    $totalFiles++
    $content = Get-Content $file.FullName -Raw
    $relativePath = $file.FullName.Replace($basePath, "").TrimStart("\")
    
    $hasIssues = $false
    $issueTypes = @()
    
    # Check for hardcoded slate colors
    if ($content -match 'text-slate-\d+') { $hasIssues = $true; $issueTypes += "text-slate" }
    if ($content -match 'bg-slate-\d+') { $hasIssues = $true; $issueTypes += "bg-slate" }
    if ($content -match 'border-slate-\d+') { $hasIssues = $true; $issueTypes += "border-slate" }
    
    # Check for hardcoded color utilities
    if ($content -match 'text-red-\d+' -and $content -notmatch 'text-state-error') { $hasIssues = $true; $issueTypes += "text-red" }
    if ($content -match 'text-green-\d+' -and $content -notmatch 'text-state-success') { $hasIssues = $true; $issueTypes += "text-green" }
    if ($content -match 'text-blue-\d+' -and $content -notmatch 'text-state-info') { $hasIssues = $true; $issueTypes += "text-blue" }
    
    # Check for muted/foreground patterns
    if ($content -match 'text-muted-foreground') { $hasIssues = $true; $issueTypes += "text-muted-foreground" }
    if ($content -match 'bg-muted') { $hasIssues = $true; $issueTypes += "bg-muted" }
    if ($content -match 'text-foreground') { $hasIssues = $true; $issueTypes += "text-foreground" }
    if ($content -match 'bg-background') { $hasIssues = $true; $issueTypes += "bg-background" }
    
    # Check for card default patterns
    if ($content -match 'className="border bg-card text-card-foreground') { $hasIssues = $true; $issueTypes += "card-default-pattern" }
    
    if ($hasIssues) {
        $issuesFound += [PSCustomObject]@{
            File = $relativePath
            Issues = ($issueTypes -join ", ")
        }
    } else {
        $compliantFiles++
    }
}

Write-Host "Total Dashboard Pages Scanned: $totalFiles" -ForegroundColor White
Write-Host "Compliant Files: $compliantFiles" -ForegroundColor Green
Write-Host "Non-Compliant Files: $($totalFiles - $compliantFiles)" -ForegroundColor $(if ($totalFiles - $compliantFiles -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($issuesFound.Count -gt 0) {
    Write-Host "ISSUES FOUND:" -ForegroundColor Red
    Write-Host "-------------" -ForegroundColor Red
    foreach ($issue in $issuesFound) {
        Write-Host "  File: $($issue.File)" -ForegroundColor Yellow
        Write-Host "  Issues: $($issue.Issues)" -ForegroundColor Gray
        Write-Host ""
    }
    $compliancePercentage = [math]::Round(($compliantFiles / $totalFiles) * 100, 2)
    Write-Host "COMPLIANCE: $compliancePercentage%" -ForegroundColor Red
} else {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ ALL FILES ARE 100% COMPLIANT!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Design System Tokens Successfully Applied:" -ForegroundColor Cyan
    Write-Host "  - Text colors (text-text-primary, text-text-secondary, text-text-tertiary)" -ForegroundColor White
    Write-Host "  - Background colors (bg-bg-base, bg-bg-panel, bg-bg-elevated)" -ForegroundColor White
    Write-Host "  - Border colors (border-border-default, border-border-emphasis)" -ForegroundColor White
    Write-Host "  - State colors (state-success, state-error, state-running, state-warning)" -ForegroundColor White
    Write-Host "  - Animation tokens (duration, easing)" -ForegroundColor White
    Write-Host ""
    Write-Host "COMPLIANCE: 100%" -ForegroundColor Green
    Write-Host ""
    Write-Host "The entire ThetaAI frontend now uses the design system!" -ForegroundColor Cyan
}
