@echo off
REM Auto Capture Tool Launcher
REM This script sets up and runs the application

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created.
    
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
    echo Dependencies installed.
) else (
    call venv\Scripts\activate.bat
)

REM Dynamically set Tcl/Tk paths based on Python installation
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.base_prefix)"') do set PYTHON_HOME=%%i
if exist "%PYTHON_HOME%\tcl\tcl8.6" (
    set TCL_LIBRARY=%PYTHON_HOME%\tcl\tcl8.6
    set TK_LIBRARY=%PYTHON_HOME%\tcl\tk8.6
)

REM Run the application
python Auto_Capture_Tool.py

REM Keep window open if there was an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    pause
)
