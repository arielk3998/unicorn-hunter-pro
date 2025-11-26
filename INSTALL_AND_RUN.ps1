<#
.SYNOPSIS
One-Click Installer and Launcher for Unicorn Hunter Pro

.DESCRIPTION
This script will:
1. Check Python installation
2. Create virtual environment
3. Install dependencies
4. Create desktop and Start Menu shortcuts
5. Launch the application

Double-click this file or run from PowerShell to start!

.EXAMPLE
Just double-click this file in Windows Explorer
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

function Write-Step {
    param([string]$Message)
    Write-Host "`n[$Message]" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

Clear-Host
Write-Host "========================================" -ForegroundColor Magenta
Write-Host " UNICORN HUNTER PRO - INSTALLER" -ForegroundColor Magenta
Write-Host " AI Job Application Tracker" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$repoRoot = $PSScriptRoot

# Step 1: Check Python
Write-Step "1/5 Checking Python installation"
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pythonVersion = & python --version 2>&1
    Write-Success "Python found: $pythonVersion"
    
    # Verify version is 3.11+
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Fail "Python 3.11+ required. You have Python $major.$minor"
            Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}
catch {
    Write-Fail "Python not found!"
    Write-Host "Please install Python 3.11+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Create virtual environment
Write-Step "2/5 Setting up virtual environment"
$venvPath = Join-Path $repoRoot ".venv"
if (-not (Test-Path "$venvPath\Scripts\python.exe")) {
    Write-Host "Creating virtual environment (first time setup)..." -ForegroundColor Yellow
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to create virtual environment"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Success "Virtual environment created"
}
else {
    Write-Success "Virtual environment exists"
}

$pythonExe = Join-Path $venvPath "Scripts\python.exe"

# Step 3: Install dependencies
Write-Step "3/5 Installing dependencies"
Write-Host "This may take a minute..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip --quiet 2>&1 | Out-Null
& $pythonExe -m pip install -r requirements.txt --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Failed to install dependencies"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Success "Dependencies installed"

# Step 4: Create shortcuts
Write-Step "4/5 Creating shortcuts"

$desktop = [Environment]::GetFolderPath('Desktop')
$startMenu = [Environment]::GetFolderPath('StartMenu')
$startMenuFolder = Join-Path $startMenu "Programs\Unicorn Hunter"

# Create Start Menu folder
if (-not (Test-Path $startMenuFolder)) {
    New-Item -ItemType Directory -Path $startMenuFolder -Force | Out-Null
}

# Function to create shortcut
function New-AppShortcut {
    param(
        [string]$Path,
        [string]$Name,
        [string]$WorkingDir,
        [string]$IconPath = $null
    )
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Path)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Join-Path $repoRoot 'RUN.ps1')`""
    $shortcut.WorkingDirectory = $WorkingDir
    $shortcut.Description = "Unicorn Hunter Pro - AI Job Application Tracker"
    if ($IconPath -and (Test-Path $IconPath)) {
        $shortcut.IconLocation = $IconPath
    }
    $shortcut.Save()
}

# Desktop shortcut
$desktopShortcut = Join-Path $desktop "Unicorn Hunter.lnk"
New-AppShortcut -Path $desktopShortcut -Name "Unicorn Hunter" -WorkingDir $repoRoot
Write-Success "Desktop shortcut created"

# Start Menu shortcut
$startMenuShortcut = Join-Path $startMenuFolder "Unicorn Hunter.lnk"
New-AppShortcut -Path $startMenuShortcut -Name "Unicorn Hunter" -WorkingDir $repoRoot
Write-Success "Start Menu shortcut created"

# Create uninstaller shortcut
$uninstallScript = Join-Path $repoRoot "UNINSTALL.ps1"
if (Test-Path $uninstallScript) {
    $uninstallShortcut = Join-Path $startMenuFolder "Uninstall.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($uninstallShortcut)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$uninstallScript`""
    $shortcut.WorkingDirectory = $repoRoot
    $shortcut.Description = "Uninstall Unicorn Hunter"
    $shortcut.Save()
}

# Step 5: Launch app
Write-Step "5/5 Launching Unicorn Hunter"
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Shortcuts created at:" -ForegroundColor Cyan
Write-Host "  • Desktop: Unicorn Hunter" -ForegroundColor White
Write-Host "  • Start Menu: Unicorn Hunter" -ForegroundColor White
Write-Host ""
Write-Host "Starting app now..." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

# Launch the app
& $pythonExe (Join-Path $repoRoot "scripts\launch_unicorn_hunter.py")

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Fail "Application exited with an error"
    Write-Host "Try running from Desktop shortcut or check logs" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
