@echo off
setlocal enabledelayedexpansion
REM Auto Capture Tool Launcher
REM This script activates the virtual environment and runs the application

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run the installation script first:
    echo   install.bat  (Command Prompt)
    echo   install.ps1  (PowerShell)
    echo.
    pause
    exit /b 1
)

REM Dynamically detect Tcl/Tk paths using Python helper script
set TCL_LIBRARY=
set TK_LIBRARY=
set LINE_COUNT=0
for /f "delims=" %%a in ('venv\Scripts\python.exe detect_tcl_tk.py 2^>nul') do (
    set /a LINE_COUNT+=1
    if !LINE_COUNT! EQU 1 set TCL_LIBRARY=%%a
    if !LINE_COUNT! EQU 2 set TK_LIBRARY=%%a
)

REM Set environment variables if paths were found (non-empty and exist)
if defined TCL_LIBRARY (
    if exist "!TCL_LIBRARY!" (
        set "TCL_LIBRARY=!TCL_LIBRARY!"
    ) else (
        set "TCL_LIBRARY="
    )
)
if defined TK_LIBRARY (
    if exist "!TK_LIBRARY!" (
        set "TK_LIBRARY=!TK_LIBRARY!"
    ) else (
        set "TK_LIBRARY="
    )
)

echo Starting Auto Capture Tool...
echo.

REM Check if selenium is installed in venv, if not install requirements
venv\Scripts\python.exe -c "import selenium" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
)

REM Run the application
echo Running application...
echo.
venv\Scripts\python.exe Auto_Capture_Tool.py
set EXIT_CODE=%ERRORLEVEL%

REM Keep window open
echo.
if %EXIT_CODE% EQU 0 (
    echo Application exited successfully.
) else (
    echo Application exited with error code: %EXIT_CODE%
)
echo.
pause
