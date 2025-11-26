<#
.SYNOPSIS
Local build script for creating distributable executables.

.DESCRIPTION
Builds UnicornHunter executables for the current platform. Optionally fetches icon first.

.PARAMETER SkipIcon
Skip fetching the unicorn icon (assumes it already exists).

.PARAMETER SkipTests
Skip running tests before building.

.EXAMPLE
./scripts/build_release.ps1

.EXAMPLE
./scripts/build_release.ps1 -SkipIcon -SkipTests
#>
[CmdletBinding()]
param(
    [switch]$SkipIcon,
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "=== Unicorn Hunter Build Script ===" -ForegroundColor Cyan

# Step 1: Verify virtual environment
if (-not (Test-Path (Join-Path $repoRoot '.venv/Scripts/python.exe'))) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv"
    exit 1
}

$python = Join-Path $repoRoot '.venv/Scripts/python.exe'
Write-Host "[1/6] Using Python: $python" -ForegroundColor Green

# Step 2: Install dependencies
Write-Host "[2/6] Installing dependencies..." -ForegroundColor Green
& $python -m pip install --upgrade pip --quiet
& $python -m pip install -r (Join-Path $repoRoot 'requirements.txt') --quiet
& $python -m pip install pyinstaller --quiet

# Step 3: Run tests (optional)
if (-not $SkipTests) {
    Write-Host "[3/6] Running tests..." -ForegroundColor Green
    & $python -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed. Fix issues before building release."
        exit 1
    }
}
else {
    Write-Host "[3/6] Skipping tests (--SkipTests flag)" -ForegroundColor Yellow
}

# Step 4: Fetch icon (optional)
if (-not $SkipIcon) {
    Write-Host "[4/6] Fetching unicorn icon..." -ForegroundColor Green
    & (Join-Path $PSScriptRoot 'fetch_unicorn_icon.ps1')
}
else {
    Write-Host "[4/6] Skipping icon fetch (--SkipIcon flag)" -ForegroundColor Yellow
}

# Step 5: Build executable
Write-Host "[5/6] Building executable with PyInstaller..." -ForegroundColor Green
$iconPath = Join-Path $repoRoot 'assets/unicorn.ico'
$launcherScript = Join-Path $repoRoot 'scripts/launch_unicorn_hunter.py'

if (Test-Path $iconPath) {
    & $python -m PyInstaller --onefile --noconsole --icon $iconPath --name UnicornHunter $launcherScript --clean
}
else {
    Write-Warning "Icon not found, building without icon"
    & $python -m PyInstaller --onefile --noconsole --name UnicornHunter $launcherScript --clean
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
    exit 1
}

# Step 6: Package release
Write-Host "[6/6] Packaging release..." -ForegroundColor Green
$releaseDir = Join-Path $repoRoot 'release'
if (Test-Path $releaseDir) { Remove-Item $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null

$exePath = Join-Path $repoRoot 'dist/UnicornHunter.exe'
if (-not (Test-Path $exePath)) {
    $exePath = Join-Path $repoRoot 'dist/UnicornHunter'  # Unix
}

Copy-Item $exePath $releaseDir
Copy-Item (Join-Path $repoRoot 'README.md') $releaseDir
Copy-Item (Join-Path $repoRoot 'LICENSE') $releaseDir -ErrorAction SilentlyContinue

Write-Host "`n✓ Build complete!" -ForegroundColor Green
Write-Host "   Executable: $exePath" -ForegroundColor Cyan
Write-Host "   Release package: $releaseDir" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  - Test the executable: & '$exePath'" -ForegroundColor White
Write-Host "  - Create GitHub release: git tag v1.0.0 && git push origin v1.0.0" -ForegroundColor White
Write-Host "  - Or upload manually to your website" -ForegroundColor White
