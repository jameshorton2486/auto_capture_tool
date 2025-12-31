@echo off
REM Auto Capture Tool - Installation Script for Command Prompt
REM This script creates a virtual environment and installs all dependencies

echo ========================================
echo Auto Capture Tool - Installation
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH!
    echo Please install Python 3.11 or higher from python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Check if venv exists, remove it if it does
if exist "venv" (
    echo Existing virtual environment found. Removing it...
    rmdir /s /q venv
    echo Removed old virtual environment
    echo.
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

REM Upgrade pip
echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Verify installation
echo Verifying installation...
venv\Scripts\python.exe -c "import selenium" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] selenium
) else (
    echo   [FAIL] selenium
)

venv\Scripts\python.exe -c "import PIL" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] PIL
) else (
    echo   [FAIL] PIL
)

venv\Scripts\python.exe -c "import tkinter" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] tkinter
) else (
    echo   [FAIL] tkinter
)

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo You can now run the application using:
echo   run_app.bat  (Command Prompt)
echo   run_app.ps1  (PowerShell)
echo.
pause
