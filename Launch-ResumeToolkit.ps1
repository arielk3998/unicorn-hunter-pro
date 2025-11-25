# Resume Toolkit PowerShell Launcher
# Double-click this file to launch the Resume Toolkit

Set-Location "d:\Master Folder\Ariel's\Personal Documents\Career\Ariels-Resumes\resume-toolkit"

# Activate virtual environment if it exists
$venvPath = "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
}

# Launch the GUI
python launch_gui.py
