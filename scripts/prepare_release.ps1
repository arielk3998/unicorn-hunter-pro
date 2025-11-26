<#
.SYNOPSIS
Prepare and create a new GitHub release.

.DESCRIPTION
Guides through creating a new release:
- Prompts for version number
- Generates release notes
- Creates git tag
- Builds executables locally (optional)
- Pushes tag to trigger GitHub Actions

.PARAMETER Version
Version number (e.g., 1.0.0). Will be prefixed with 'v'.

.PARAMETER SkipBuild
Skip local build verification (just create tag and push).

.EXAMPLE
./scripts/prepare_release.ps1 -Version 1.0.0

.EXAMPLE
./scripts/prepare_release.ps1 -Version 1.0.1 -SkipBuild
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Version,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "=== Unicorn Hunter Release Preparation ===" -ForegroundColor Cyan

# Step 1: Get version
if (-not $Version) {
    $Version = Read-Host "Enter version number (e.g., 1.0.0)"
}
$Version = $Version.TrimStart('v')
$tagName = "v$Version"

Write-Host "`nPreparing release: $tagName" -ForegroundColor Green

# Step 2: Verify git status
Write-Host "`n[1/6] Checking git status..." -ForegroundColor Yellow
Set-Location $repoRoot
$status = git status --porcelain
if ($status) {
    Write-Warning "Uncommitted changes detected:"
    Write-Host $status
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') {
        Write-Host "Aborted." -ForegroundColor Red
        exit 0
    }
}

# Step 3: Update version in files (optional - create VERSION file)
Write-Host "[2/6] Creating VERSION file..." -ForegroundColor Yellow
$Version | Out-File (Join-Path $repoRoot 'VERSION') -Encoding UTF8 -NoNewline

# Step 4: Generate release notes
Write-Host "[3/6] Generating release notes..." -ForegroundColor Yellow
$releaseNotes = @"
## Unicorn Hunter Pro v$Version

### What's New
- AI-powered job application tracking
- Resume optimization and ATS analysis
- Desktop GUI launcher (no browser required)
- Intelligent job matching

### Downloads
Choose the version for your operating system:

- **Windows**: [UnicornHunter-Windows.zip](https://github.com/arielk3998/unicorn-hunter-pro/releases/download/$tagName/UnicornHunter-Windows.zip)
- **macOS**: [UnicornHunter-macOS.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/download/$tagName/UnicornHunter-macOS.tar.gz)
- **Linux**: [UnicornHunter-Linux.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/download/$tagName/UnicornHunter-Linux.tar.gz)

### Installation
See [INSTALL.md](https://github.com/arielk3998/unicorn-hunter-pro/blob/main/INSTALL.md) for detailed instructions.

### Quick Start (Windows)
1. Download UnicornHunter-Windows.zip
2. Extract the ZIP file
3. Double-click UnicornHunter.exe
4. (Optional) Create desktop shortcut

### Attribution
Unicorn icon © OpenMoji – Licensed under CC BY-SA 4.0

### License
MIT License - Free for personal and commercial use

---
**Full Changelog**: https://github.com/arielk3998/unicorn-hunter-pro/compare/v$((([version]$Version).Major -eq 0 -and ([version]$Version).Minor -gt 0) ? "0.$([version]$Version).Minor - 1).0" : "$(([version]$Version).Major - 1).0.0")...$tagName
"@

$releaseNotes | Out-File (Join-Path $repoRoot "RELEASE_NOTES_$Version.md") -Encoding UTF8
Write-Host "Release notes saved to RELEASE_NOTES_$Version.md"

# Step 5: Optional local build verification
if (-not $SkipBuild) {
    Write-Host "[4/6] Building executable locally to verify..." -ForegroundColor Yellow
    $buildScript = Join-Path $PSScriptRoot 'build_release.ps1'
    & $buildScript -SkipTests
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed. Fix issues before releasing."
        exit 1
    }
    Write-Host "✓ Local build successful" -ForegroundColor Green
}
else {
    Write-Host "[4/6] Skipping local build (--SkipBuild flag)" -ForegroundColor Yellow
}

# Step 6: Create git tag
Write-Host "[5/6] Creating git tag: $tagName..." -ForegroundColor Yellow
git add VERSION
git commit -m "chore: bump version to $Version" -n
git tag -a $tagName -m "Release $tagName"

Write-Host "`n✓ Tag created: $tagName" -ForegroundColor Green

# Step 7: Prompt to push
Write-Host "`n[6/6] Ready to push and trigger release build" -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  1. Push commits to main branch"
Write-Host "  2. Push tag $tagName"
Write-Host "  3. Trigger GitHub Actions to build Windows/Mac/Linux executables"
Write-Host "  4. Create a GitHub Release with download links"
Write-Host ""

$push = Read-Host "Push now? (y/N)"
if ($push -eq 'y') {
    git push origin main
    git push origin $tagName
    Write-Host "`n✓ Release initiated!" -ForegroundColor Green
    Write-Host "`nMonitor build progress at:" -ForegroundColor Cyan
    Write-Host "https://github.com/arielk3998/unicorn-hunter-pro/actions" -ForegroundColor White
    Write-Host "`nRelease will appear at:" -ForegroundColor Cyan
    Write-Host "https://github.com/arielk3998/unicorn-hunter-pro/releases/tag/$tagName" -ForegroundColor White
}
else {
    Write-Host "`nTag created locally. Push manually when ready:" -ForegroundColor Yellow
    Write-Host "  git push origin main" -ForegroundColor White
    Write-Host "  git push origin $tagName" -ForegroundColor White
}
