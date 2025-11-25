@echo off
REM Resume Toolkit Launcher
REM This script activates the virtual environment and launches the GUI

cd /d "%~dp0"

REM Check if virtual environment exists
if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
) else (
    echo No virtual environment found. Using system Python...
)

REM Launch the GUI
python launch_gui.py

pause
