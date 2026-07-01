@echo off
title ES Image Studio — Windows Build
color 0B
setlocal EnableDelayedExpansion

echo.
echo  =====================================================
echo   Eastern Studios ^|  ES Image Studio  ^|  Windows Build
echo  =====================================================
echo.

:: ── 1. Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo         Install Python 3.10-3.13 from https://python.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Python: %%v

:: ── 2. Install dependencies ───────────────────────────────────────────────────
echo.
echo  [1/5] Installing Python dependencies...
pip install -r desktop_requirements.txt -q
if errorlevel 1 (
    echo  [ERROR] pip install failed. See output above for details.
    pause & exit /b 1
)
echo        Done.

:: ── 3. Pre-download BiRefNet model ────────────────────────────────────────────
echo.
echo  [2/5] Downloading BiRefNet AI model (first time only, ~500 MB)...
python -c "from rembg import new_session; new_session('birefnet-general'); print('       Model cached.')"
if errorlevel 1 (
    echo  [ERROR] Model download failed. Check your internet connection.
    pause & exit /b 1
)

:: ── 4. PyInstaller — bundle app ───────────────────────────────────────────────
echo.
echo  [3/5] Bundling app with PyInstaller...
pyinstaller es_image_studio.spec --noconfirm
if errorlevel 1 (
    echo  [ERROR] PyInstaller failed. See output above.
    pause & exit /b 1
)
echo        Bundle created: dist\ES Image Studios\

:: ── 5. Inno Setup — create installer ─────────────────────────────────────────
echo.
echo  [4/5] Building Windows Setup installer...

set "ISCC="
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    "C:\Program Files\Inno Setup 5\ISCC.exe"
) do ( if exist %%p if not defined ISCC set "ISCC=%%~p" )

if not defined ISCC (
    echo.
    echo  [!] Inno Setup not found — skipping installer creation.
    echo      To create a Setup.exe, install Inno Setup 6 from:
    echo      https://jrsoftware.org/isdl.php
    echo      Then re-run this build.bat.
    echo.
    echo  Your portable app is ready at:
    echo  dist\ES Image Studios\ES Image Studios.exe
    echo.
    pause & exit /b 0
)

"%ISCC%" installer.iss
if errorlevel 1 (
    echo  [ERROR] Inno Setup failed. See output above.
    pause & exit /b 1
)

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo  [5/5] All done!
echo.
echo  +----------------------------------------------------------+
echo  ^|  Installer :  Output\ES_Image_Studio_Setup.exe           ^|
echo  ^|  Portable  :  dist\ES Image Studios\ES Image Studios.exe ^|
echo  +----------------------------------------------------------+
echo.
echo  Share the Setup.exe — recipients need NO Python installed.
echo  First launch downloads the AI model (~500 MB, one time only).
echo.
pause
