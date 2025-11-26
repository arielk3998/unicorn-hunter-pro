@echo off
REM ========================================
REM Unicorn Hunter - Quick Launcher (Windows)
REM ========================================
REM Double-click this file to launch the app!
REM ========================================

echo.
echo ========================================
echo  UNICORN HUNTER PRO
echo  AI Job Application Tracker
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Setting up virtual environment (first time only)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment found.
)
echo.

REM Install/update dependencies
echo [3/4] Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Launch the app
echo [4/4] Launching Unicorn Hunter...
echo.
echo ========================================
echo  App is starting...
echo  Close this window to exit the app.
echo ========================================
echo.

".venv\Scripts\python.exe" scripts\launch_unicorn_hunter.py

REM If app exits, pause to show any errors
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with an error.
    pause
)
