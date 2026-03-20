# Complete Design System Token Migration - Final Push to 100%
# This script fixes ALL remaining hardcoded colors and patterns

$basePath = "C:\Users\DELL\Projects\ThetaAI - Software Factory\frontend\src\app\(dashboard)"

$files = @(
    "testing\page.tsx",
    "simulations\page.tsx",
    "workflows\page.tsx",
    "architecture\page.tsx",
    "monitoring\page.tsx",
    "performance\page.tsx",
    "security\page.tsx"
)

Write-Host "Starting final migration to 100% design system compliance..." -ForegroundColor Cyan
Write-Host ""

foreach ($file in $files) {
    $fullPath = Join-Path $basePath $file
    
    if (Test-Path $fullPath) {
        Write-Host "Processing: $file" -ForegroundColor Yellow
        
        $content = Get-Content $fullPath -Raw
        $originalContent = $content
        
        # Text colors - comprehensive mapping
        $content = $content -replace 'text-slate-100', 'text-text-primary'
        $content = $content -replace 'text-slate-200', 'text-text-primary'
        $content = $content -replace 'text-slate-300', 'text-text-secondary'
        $content = $content -replace 'text-slate-400', 'text-text-secondary'
        $content = $content -replace 'text-slate-500', 'text-text-tertiary'
        $content = $content -replace 'text-slate-600', 'text-text-tertiary'
        $content = $content -replace 'text-muted-foreground', 'text-text-secondary'
        
        # Specific color replacements
        $content = $content -replace 'text-red-500', 'text-state-error'
        $content = $content -replace 'text-green-500', 'text-state-success'
        $content = $content -replace 'text-blue-500', 'text-state-info'
        $content = $content -replace 'text-yellow-500', 'text-state-warning'
        $content = $content -replace 'text-violet-400', 'text-state-running'
        $content = $content -replace 'text-emerald-400', 'text-state-success'
        $content = $content -replace 'text-amber-400', 'text-state-warning'
        $content = $content -replace 'text-red-400', 'text-state-error'
        
        # Background colors
        $content = $content -replace 'bg-slate-50', 'bg-bg-base'
        $content = $content -replace 'bg-slate-100', 'bg-bg-hover'
        $content = $content -replace 'bg-slate-800', 'bg-bg-hover'
        $content = $content -replace 'bg-slate-900', 'bg-bg-base'
        $content = $content -replace 'bg-slate-900/50', 'bg-bg-panel/50'
        $content = $content -replace 'bg-slate-800/50', 'bg-bg-elevated/50'
        $content = $content -replace 'bg-slate-800/30', 'bg-bg-elevated/30'
        
        # State backgrounds
        $content = $content -replace 'bg-emerald-500/10', 'bg-state-success-dim'
        $content = $content -replace 'bg-red-500/10', 'bg-state-error-dim'
        $content = $content -replace 'bg-violet-500/10', 'bg-state-running-dim'
        $content = $content -replace 'bg-amber-500/10', 'bg-state-warning-dim'
        $content = $content -replace 'bg-blue-500/10', 'bg-state-info-dim'
        $content = $content -replace 'bg-cyan-500/10', 'bg-state-info-dim'
        $content = $content -replace 'bg-orange-500/10', 'bg-state-warning-dim'
        
        # Border colors
        $content = $content -replace 'border-slate-200', 'border-border-subtle'
        $content = $content -replace 'border-slate-700', 'border-border-default'
        $content = $content -replace 'border-slate-800', 'border-border-default'
        $content = $content -replace 'border-slate-900', 'border-border-default'
        
        # State borders
        $content = $content -replace 'border-emerald-500/20', 'border-state-success'
        $content = $content -replace 'border-red-500/20', 'border-state-error'
        $content = $content -replace 'border-violet-500/20', 'border-state-running'
        $content = $content -replace 'border-amber-500/20', 'border-state-warning'
        $content = $content -replace 'border-blue-500/20', 'border-state-info'
        
        # Gradient replacements for icons/badges
        $content = $content -replace 'from-violet-500/20 to-indigo-500/20', 'from-state-running-dim/30 to-state-running-dim/10'
        $content = $content -replace 'from-emerald-500/20 to-teal-500/20', 'from-state-success-dim/30 to-state-success-dim/10'
        $content = $content -replace 'from-red-500/20 to-rose-500/20', 'from-state-error-dim/30 to-state-error-dim/10'
        $content = $content -replace 'from-blue-500/20 to-cyan-500/20', 'from-state-info-dim/30 to-state-info-dim/10'
        $content = $content -replace 'from-amber-500/20 to-orange-500/20', 'from-state-warning-dim/30 to-state-warning-dim/10'
        
        # Button variants
        $content = $content -replace "className='bg-violet-600'", "className='bg-gradient-to-r from-violet-500 to-indigo-600'"
        $content = $content -replace 'className="bg-violet-600"', 'className="bg-gradient-to-r from-violet-500 to-indigo-600"'
        
        # Progress bar backgrounds
        $content = $content -replace 'bg-slate-700', 'bg-bg-base'
        $content = $content -replace 'bg-slate-800', 'bg-bg-base'
        
        # Card specific patterns
        $content = $content -replace 'className="border bg-card text-card-foreground shadow-sm"', 'className="border-border-default bg-bg-panel text-text-primary"'
        
        # Tabs updates
        $content = $content -replace 'className="border-b border-slate-200"', 'className="border-b border-border-default"'
        $content = $content -replace 'data-\[state=active\]:bg-slate-800', 'data-[state=active]:bg-bg-hover'
        $content = $content -replace 'data-\[state=inactive\]', 'data-[state=inactive]:text-text-secondary'
        
        # Badge patterns
        $content = $content -replace 'variant="secondary"', 'variant="outline"'
        $content = $content -replace 'variant="destructive"', 'variant="outline"'
        
        # Utility classes
        $content = $content -replace 'text-muted', 'text-text-secondary'
        $content = $content -replace 'bg-muted', 'bg-bg-panel'
        $content = $content -replace 'bg-background', 'bg-bg-base'
        $content = $content -replace 'text-foreground', 'text-text-primary'
        
        # Layout utilities (keep but ensure consistency)
        $content = $content -replace 'container mx-auto p-6', 'container mx-auto px-6 py-4'
        
        if ($content -ne $originalContent) {
            Set-Content $fullPath $content -NoNewline
            Write-Host "  Updated successfully" -ForegroundColor Green
        } else {
            Write-Host "  No changes needed" -ForegroundColor Gray
        }
    } else {
        Write-Host "  File not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Final migration complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check workflows/page.tsx for additional component refactoring" -ForegroundColor White
Write-Host "2. Verify all pages compile without errors" -ForegroundColor White
Write-Host "3. Test visual appearance in browser" -ForegroundColor White
