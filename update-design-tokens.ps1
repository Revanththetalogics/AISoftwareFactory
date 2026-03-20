# Design System Token Migration Script
# This script updates all dashboard pages to use the new design tokens

$files = @(
    "frontend\src\app\(dashboard)\settings\page.tsx",
    "frontend\src\app\(dashboard)\testing\page.tsx", 
    "frontend\src\app\(dashboard)\architecture\page.tsx",
    "frontend\src\app\(dashboard)\monitoring\page.tsx",
    "frontend\src\app\(dashboard)\performance\page.tsx",
    "frontend\src\app\(dashboard)\security\page.tsx",
    "frontend\src\app\(dashboard)\knowledge\page.tsx",
    "frontend\src\app\(dashboard)\infrastructure\page.tsx",
    "frontend\src\app\(dashboard)\codegen\page.tsx",
    "frontend\src\app\(dashboard)\database\page.tsx",
    "frontend\src\app\(dashboard)\files\page.tsx",
    "frontend\src\app\(dashboard)\visual-testing\page.tsx"
)

Write-Host "Starting design system token migration..." -ForegroundColor Cyan

foreach ($file in $files) {
    $fullPath = Join-Path "C:\Users\DELL\Projects\ThetaAI - Software Factory" $file
    
    if (Test-Path $fullPath) {
        Write-Host "Processing: $file" -ForegroundColor Yellow
        
        $content = Get-Content $fullPath -Raw
        
        # Replace text colors
        $content = $content -replace 'text-slate-100', 'text-text-primary'
        $content = $content -replace 'text-slate-200', 'text-text-primary'
        $content = $content -replace 'text-slate-300', 'text-text-secondary'
        $content = $content -replace 'text-slate-400', 'text-text-secondary'
        $content = $content -replace 'text-slate-500', 'text-text-tertiary'
        
        # Replace bg colors
        $content = $content -replace 'bg-slate-800', 'bg-bg-hover'
        $content = $content -replace 'bg-slate-900', 'bg-bg-base'
        $content = $content -replace 'bg-slate-900/50', 'bg-bg-panel/50'
        $content = $content -replace 'bg-slate-800/50', 'bg-bg-elevated/50'
        $content = $content -replace 'bg-slate-800/30', 'bg-bg-elevated/30'
        
        # Replace border colors
        $content = $content -replace 'border-slate-700', 'border-border-default'
        $content = $content -replace 'border-slate-800', 'border-border-default'
        
        # Replace specific state colors with tokens
        $content = $content -replace 'bg-emerald-500/10', 'bg-state-success-dim'
        $content = $content -replace 'text-emerald-400', 'text-state-success'
        $content = $content -replace 'border-emerald-500/20', 'border-state-success'
        $content = $content -replace 'bg-red-500/10', 'bg-state-error-dim'
        $content = $content -replace 'text-red-400', 'text-state-error'
        $content = $content -replace 'border-red-500/20', 'border-state-error'
        $content = $content -replace 'bg-violet-500/10', 'bg-state-running-dim'
        $content = $content -replace 'text-violet-400', 'text-state-running'
        $content = $content -replace 'border-violet-500/20', 'border-state-running'
        $content = $content -replace 'bg-amber-500/10', 'bg-state-warning-dim'
        $content = $content -replace 'text-amber-400', 'text-state-warning'
        $content = $content -replace 'border-amber-500/20', 'border-state-warning'
        $content = $content -replace 'bg-blue-500/10', 'bg-state-info-dim'
        $content = $content -replace 'text-blue-400', 'text-state-info'
        
        Set-Content $fullPath $content -NoNewline
        Write-Host "  Updated" -ForegroundColor Green
    } else {
        Write-Host "  File not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Migration complete!" -ForegroundColor Cyan
