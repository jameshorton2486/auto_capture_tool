# Auto Capture Tool - Installation Script for PowerShell
# This script creates a virtual environment and installs all dependencies

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Auto Capture Tool - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available (use py launcher to avoid alias issues)
Write-Host "Checking Python installation..." -ForegroundColor Yellow

# Try py launcher first (most reliable on Windows, avoids alias issues)
$pythonCmd = $null
$usePyLauncher = $false

try {
    $pyVersion = py -3 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "py"
        $usePyLauncher = $true
        Write-Host "Found: $pyVersion (using Python launcher)" -ForegroundColor Green
    }
} catch {
    # py launcher not available, try python command
}

# If py launcher didn't work, try direct python command
if (-not $pythonCmd) {
    try {
        # Clear any broken aliases first
        Remove-Item Alias:python -ErrorAction SilentlyContinue
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = (Get-Command python).Source
            Write-Host "Found: $pythonVersion" -ForegroundColor Green
        }
    } catch {
        Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
        Write-Host "Please install Python 3.11 or higher from python.org" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Could not find a working Python installation!" -ForegroundColor Red
    Write-Host "Please install Python 3.11 or higher from python.org" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Python command: $pythonCmd" -ForegroundColor Gray
Write-Host ""

# Check if venv exists, remove it if it does (to recreate with correct Python)
if (Test-Path "venv") {
    Write-Host "Existing virtual environment found. Removing it..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
    Write-Host "Removed old virtual environment" -ForegroundColor Green
    Write-Host ""
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if ($usePyLauncher) {
    py -3 -m venv venv
} else {
    & $pythonCmd -m venv venv
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment created successfully" -ForegroundColor Green
Write-Host ""

# Get venv Python executable
$venvPython = Join-Path $ScriptDir "venv\Scripts\python.exe"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
Write-Host "pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
$modules = @("selenium", "PIL", "tkinter")
$allOk = $true
foreach ($module in $modules) {
    & $venvPython -c "import $module" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $module" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $module - FAILED" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the application using:" -ForegroundColor Cyan
    Write-Host "  .\run_app.ps1  (PowerShell)" -ForegroundColor Yellow
    Write-Host "  .\run_app.bat  (Command Prompt)" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Installation completed with errors!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
