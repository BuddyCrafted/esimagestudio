@echo off
title ES Image Studio — Launcher
color 0B
cd /d "%~dp0"

echo.
echo  ================================================
echo    ES Image Studio  ^|  Eastern Studios
echo    Starting the app...
echo  ================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python is not installed.
    echo.
    echo  Please install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: On the installer, tick the box that says
    echo  "Add Python to PATH" before clicking Install.
    echo.
    pause & exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  Python found: %PY_VER%
echo.

:: ── Install / update dependencies ─────────────────────────────────────────────
echo  Installing dependencies (this takes 1-2 minutes the first time)...
echo.
pip install -r desktop_requirements.txt -q
if errorlevel 1 (
    echo.
    echo  [ERROR] Something went wrong installing dependencies.
    echo  Try running this command manually in a terminal:
    echo    pip install -r desktop_requirements.txt
    pause & exit /b 1
)

echo  Dependencies ready.
echo.

:: ── Launch the app ────────────────────────────────────────────────────────────
echo  ================================================
echo    Launching ES Image Studio...
echo.
echo    NOTE: The FIRST time you run this, it will
echo    download the AI model (~500 MB). This can take
echo    5-15 minutes depending on your internet speed.
echo    The app window will open when it's ready.
echo  ================================================
echo.

python desktop.py

if errorlevel 1 (
    echo.
    echo  [ERROR] The app crashed. Error details are above.
    echo.
    echo  Common fixes:
    echo  1. Make sure you are connected to the internet (first run downloads AI model)
    echo  2. Run: pip install pywebview --upgrade
    echo  3. Make sure Microsoft Edge is up to date (Windows Update)
    pause
)
