# Auto Capture Tool Launcher for PowerShell
# This script activates the virtual environment and runs the application

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
  Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
  Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
  Write-Host "Then run: .\venv\Scripts\pip.exe install -r requirements.txt" -ForegroundColor Yellow
  pause
  exit 1
}

# Set Tcl/Tk environment variables (fixes tkinter GUI issues)
$env:TCL_LIBRARY = "C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
$env:TK_LIBRARY = "C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tk8.6"

# Activate virtual environment and run the application
& .\venv\Scripts\Activate.ps1
python Auto_Capture_Tool.py

# Keep window open if there was an error
if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "Application exited with error code: $LASTEXITCODE" -ForegroundColor Red
  pause
}
