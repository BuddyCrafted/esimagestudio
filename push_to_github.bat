@echo off
title ES Image Studio - Push to GitHub
color 0B
cd /d "%~dp0"

echo.
echo  ===================================================
echo   Eastern Studios - ES Image Studio - GitHub Push
echo  ===================================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Git not found. Install from https://git-scm.com/download/win
    pause & exit /b 1
)

echo  Repo URL: https://github.com/BuddyCrafted/esimagestudio.git
echo.

:: Set identity globally so commit always works
git config --global user.email "dapastino@gmail.com"
git config --global user.name "Eastern Studios"

:: Clean slate - remove old broken git state if present
if exist ".git" (
    echo  Removing old git data and starting fresh...
    rmdir /s /q ".git"
)

:: Fresh init
git init
if errorlevel 1 ( echo  ERROR: git init failed. & pause & exit /b 1 )

:: Create .gitignore
echo dist/>         .gitignore
echo build/>>       .gitignore
echo Output/>>      .gitignore
echo __pycache__/>> .gitignore
echo uploads/>>     .gitignore
echo venv/>>        .gitignore
echo .env>>         .gitignore
echo *.pyc>>        .gitignore

:: Stage everything
echo  Adding files...
git add -A
git status --short

:: Commit
echo.
echo  Committing...
git commit -m "Initial commit - ES Image Studio v1.0"
if errorlevel 1 (
    echo.
    echo  ERROR: Nothing was committed. Make sure files exist in this folder.
    pause & exit /b 1
)

:: Rename branch to main
git branch -M main

:: Set remote
git remote add origin https://github.com/BuddyCrafted/esimagestudio.git

:: Push
echo.
echo  Pushing to GitHub - a browser window may pop up to sign in...
git push -u origin main --force

if errorlevel 1 (
    echo.
    echo  Push failed. If a browser did NOT open for sign-in, run this:
    echo  git credential-manager github login
    echo  Then run this script again.
    pause & exit /b 1
)

echo.
echo  ===================================================
echo   SUCCESS! Files are now on GitHub.
echo.
echo   NEXT STEP:
echo   1. Go to https://github.com/BuddyCrafted/esimagestudio
echo   2. Click the ACTIONS tab
echo   3. Click "Build ES Image Studio"
echo   4. Click "Run workflow" then "Run workflow" again
echo   5. Wait ~15 minutes
echo   6. Download your Windows, Mac and Linux builds
echo  ===================================================
echo.
pause
