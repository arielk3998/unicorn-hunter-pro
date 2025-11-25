<#
.SYNOPSIS
Creates a Windows Desktop shortcut for Unicorn Hunter launcher.

.DESCRIPTION
Generates a .lnk shortcut on the current user's Desktop that runs the existing
PowerShell launcher with optional flags. If PyInstaller executable exists, user can
choose that instead. Designed to be idempotent: existing shortcut will be replaced.

.PARAMETER UseExe
If supplied and a built EXE (dist/UnicornHunter.exe) exists, shortcut will target the EXE.
Otherwise it targets launch_unicorn_hunter.ps1.

.EXAMPLE
./scripts/install_desktop_shortcut.ps1

.EXAMPLE
./scripts/install_desktop_shortcut.ps1 -UseExe

.NOTES
Requires Windows. Uses WScript.Shell COM object. ExecutionPolicy may need Bypass when
running the shortcut.
#>
[CmdletBinding()]
param(
    [switch]$UseExe,
    [string]$ShortcutName = 'Unicorn Hunter',
    [switch]$Api,        # Include -Api flag in shortcut
    [switch]$Browser     # Include -Browser flag in shortcut
)

function New-DesktopShortcut {
    param(
        [string]$TargetPath,
        [string]$Arguments,
        [string]$ShortcutPath,
        [string]$IconPath = $null,
        [string]$WorkingDir = $null
    )
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $TargetPath
    if ($Arguments) { $shortcut.Arguments = $Arguments }
    if ($WorkingDir) { $shortcut.WorkingDirectory = $WorkingDir }
    if ($IconPath -and (Test-Path $IconPath)) { $shortcut.IconLocation = $IconPath }
    $shortcut.WindowStyle = 1
    $shortcut.Description = 'Launch Unicorn Hunter job application toolkit'
    $shortcut.Save()
}

$repoRoot = Split-Path $PSScriptRoot -Parent
$desktop   = [Environment]::GetFolderPath('Desktop')
$shortcut  = Join-Path $desktop ("$ShortcutName.lnk")

$exePath    = Join-Path $repoRoot 'dist/UnicornHunter.exe'
$psLauncher = Join-Path $repoRoot 'launch_unicorn_hunter.ps1'
$iconCandidate = Join-Path $repoRoot 'assets/unicorn.ico'

$flags = @()
if ($Api) { $flags += '-Api' }
if ($Browser) { $flags += '-Browser' }
$flagString = ($flags -join ' ')

if ($UseExe -and (Test-Path $exePath)) {
    Write-Host "Creating shortcut targeting EXE: $exePath"
    if (Test-Path $iconCandidate) {
        Write-Host "Using icon: $iconCandidate"
        New-DesktopShortcut -TargetPath $exePath -Arguments $flagString -ShortcutPath $shortcut -WorkingDir $repoRoot -IconPath $iconCandidate
    }
    else {
        New-DesktopShortcut -TargetPath $exePath -Arguments $flagString -ShortcutPath $shortcut -WorkingDir $repoRoot
    }
}
else {
    if (-not (Test-Path $psLauncher)) {
        Write-Error "Launcher script not found: $psLauncher"; exit 1
    }
    Write-Host "Creating shortcut targeting PowerShell launcher: $psLauncher"
    # Target powershell.exe with -File argument
    $escaped = $psLauncher.Replace('`"','"')
    $args = "-ExecutionPolicy Bypass -File `"$escaped`" $flagString".Trim()
    if (Test-Path $iconCandidate) {
        Write-Host "Using icon: $iconCandidate"
        New-DesktopShortcut -TargetPath "powershell.exe" -Arguments $args -ShortcutPath $shortcut -WorkingDir $repoRoot -IconPath $iconCandidate
    }
    else {
        New-DesktopShortcut -TargetPath "powershell.exe" -Arguments $args -ShortcutPath $shortcut -WorkingDir $repoRoot
    }
}

Write-Host "Shortcut created: $shortcut"

if (-not (Test-Path $exePath)) {
    Write-Host "(Optional) Build EXE first if desired:" -ForegroundColor Yellow
    Write-Host "pyinstaller --onefile --noconsole --name UnicornHunter scripts/launch_unicorn_hunter.py" -ForegroundColor Yellow
}
