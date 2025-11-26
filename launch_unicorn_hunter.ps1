# PowerShell launcher for The Unicorn Hunter desktop application
# Usage examples:
#   ./launch_unicorn_hunter.ps1              # GUI only
#   ./launch_unicorn_hunter.ps1 -Api         # Start API + GUI
#   ./launch_unicorn_hunter.ps1 -Api -Port 8090 -Browser
param(
    [switch]$Api,
    [int]$Port,
    [switch]$Browser
)

$ErrorActionPreference = 'Stop'

# Resolve virtual environment python (fallback to 'python')
$venvPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $venvPython)) {
    $venvPython = 'python'
}

$launcher = Join-Path $PSScriptRoot 'scripts/launch_unicorn_hunter.py'
if (-not (Test-Path $launcher)) {
    Write-Error "Launcher script not found: $launcher"
    exit 1
}

$cmd = @($venvPython, $launcher)
if ($Api) { $cmd += '--api' }
if ($Port) { $cmd += @('--port', $Port) }
if ($Browser) { $cmd += '--browser' }

Write-Host "[PS Launcher] Running: $($cmd -join ' ')" -ForegroundColor Cyan
& $cmd
