@echo off
title ES Image Studio - Push Updates to GitHub
color 0B
cd /d "%~dp0"

echo.
echo  ===================================================
echo   Eastern Studios - Push Updates to GitHub
echo  ===================================================
echo.

:: Check git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Git not found. Install from https://git-scm.com/download/win
    pause & exit /b 1
)

:: If no .git folder, tell user to run push_to_github.bat first
if not exist ".git" (
    echo  No git repo found here.
    echo  Run push_to_github.bat first to set up the repo.
    pause & exit /b 1
)

:: Set identity
git config --global user.email "dapastino@gmail.com"
git config --global user.name "Eastern Studios"

:: Stage everything
echo  Adding all changed files...
git add -A
echo.
git status --short
echo.

:: Check if there is anything to commit
git diff --cached --quiet
if not errorlevel 1 (
    echo  Nothing has changed since the last push. All files are up to date.
    pause & exit /b 0
)

:: Commit with timestamp
set TIMESTAMP=%DATE% %TIME%
git commit -m "Update %TIMESTAMP%"
if errorlevel 1 (
    echo.
    echo  Commit failed. See error above.
    pause & exit /b 1
)

:: Push
echo.
echo  Pushing to GitHub...
git push origin main
if errorlevel 1 (
    echo.
    echo  Push failed. If you see an auth error, run:
    echo    git credential-manager github login
    echo  Then run this script again.
    pause & exit /b 1
)

echo.
echo  ===================================================
echo   Done! Your changes are now on GitHub.
echo.
echo   Next step: go to the ACTIONS tab on GitHub to
echo   watch the Windows / Mac / Linux builds run.
echo   https://github.com/BuddyCrafted/esimagestudio/actions
echo  ===================================================
echo.
pause
