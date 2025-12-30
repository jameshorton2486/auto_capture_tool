@echo off
REM Auto Capture Tool Launcher
REM This script activates the virtual environment and runs the application

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

REM Set Tcl/Tk environment variables (fixes tkinter GUI issues)
set TCL_LIBRARY=C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tcl8.6
set TK_LIBRARY=C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tk8.6

REM Activate virtual environment and run the application
call venv\Scripts\activate.bat
python Auto_Capture_Tool.py

REM Keep window open if there was an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    pause
)
