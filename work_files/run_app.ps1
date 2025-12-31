# Auto Capture Tool Launcher for PowerShell
# This script sets up and runs the application

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if virtual environment exists, create if not
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "Virtual environment created." -ForegroundColor Green
    
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "Dependencies installed." -ForegroundColor Green
} else {
    & .\venv\Scripts\Activate.ps1
}

# Dynamically set Tcl/Tk paths based on Python installation
$pythonHome = python -c "import sys; print(sys.base_prefix)"
$tclPath = Join-Path $pythonHome "tcl\tcl8.6"
$tkPath = Join-Path $pythonHome "tcl\tk8.6"

if (Test-Path $tclPath) {
    $env:TCL_LIBRARY = $tclPath
    $env:TK_LIBRARY = $tkPath
}

# Run the application
python Auto_Capture_Tool.py

# Keep window open if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Application exited with error code: $LASTEXITCODE" -ForegroundColor Red
    pause
}
