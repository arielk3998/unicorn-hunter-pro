# ========================================
# Unicorn Hunter - Quick Launcher
# ========================================
# Double-click this file to launch the app!
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " UNICORN HUNTER PRO" -ForegroundColor Cyan
Write-Host " AI Job Application Tracker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repoRoot = $PSScriptRoot

# Check if setup has been run
$venvPath = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host "First time setup required!" -ForegroundColor Yellow
    Write-Host "Running installer..." -ForegroundColor Yellow
    Write-Host ""
    
    $installer = Join-Path $repoRoot "INSTALL_AND_RUN.ps1"
    if (Test-Path $installer) {
        & $installer
        exit
    }
    else {
        Write-Host "[ERROR] Installer not found: $installer" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please run INSTALL_AND_RUN.ps1 first" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Launch the app
Write-Host "Starting Unicorn Hunter..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Close this window to exit the app" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

& $venvPath (Join-Path $repoRoot "scripts\launch_unicorn_hunter.py")

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Application exited with an error" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
