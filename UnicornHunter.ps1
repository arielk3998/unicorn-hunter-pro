# Unicorn Hunter Pro - Launcher
# Double-click to start the app with a proper name and icon

$repoRoot = $PSScriptRoot
$venvPy = Join-Path $repoRoot ".venv/Scripts/python.exe"
$launcher = Join-Path $repoRoot "scripts/launch_unicorn_hunter.py"

if (-not (Test-Path $venvPy)) {
    Write-Host "First-time setup detected. Running installer..." -ForegroundColor Yellow
    $installer = Join-Path $repoRoot "INSTALL_AND_RUN.ps1"
    if (Test-Path $installer) { & $installer; exit }
    else { Write-Error "Installer not found: $installer"; exit 1 }
}

Write-Host "Starting Unicorn Hunter Pro..." -ForegroundColor Cyan
& $venvPy $launcher
if ($LASTEXITCODE -ne 0) {
    Write-Host "App exited with error code $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Press Enter to close"
}
