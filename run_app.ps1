# Auto Capture Tool Launcher for PowerShell
# This script activates the virtual environment and runs the application

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
  Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
  Write-Host "Please run the installation script first:" -ForegroundColor Yellow
  Write-Host "  .\install.ps1  (PowerShell)" -ForegroundColor Cyan
  Write-Host "  .\install.bat  (Command Prompt)" -ForegroundColor Cyan
  Write-Host ""
  Read-Host "Press Enter to exit"
  exit 1
}

# Use venv python directly
$venvPython = Join-Path $ScriptDir "venv\Scripts\python.exe"

# Dynamically detect Tcl/Tk paths from the Python executable
Write-Host "Detecting Tcl/Tk library paths..." -ForegroundColor Gray
$tclTkOutput = & $venvPython detect_tcl_tk.py 2>&1
$paths = $tclTkOutput | Where-Object { $_ -match '^\S' } | Select-Object -First 2

$tclPath = $null
$tkPath = $null

if ($paths.Count -ge 2) {
    $tclPath = $paths[0].Trim()
    $tkPath = $paths[1].Trim()
    
    # Set Tcl/Tk environment variables if paths were found and exist
    if ($tclPath -and (Test-Path $tclPath)) {
        $env:TCL_LIBRARY = $tclPath
        Write-Host "  TCL_LIBRARY: $tclPath" -ForegroundColor Gray
    }
    if ($tkPath -and (Test-Path $tkPath)) {
        $env:TK_LIBRARY = $tkPath
        Write-Host "  TK_LIBRARY: $tkPath" -ForegroundColor Gray
    }
}

Write-Host "Starting Auto Capture Tool..." -ForegroundColor Cyan
Write-Host ""

# Check if venv is properly set up (has pip)
$hasPip = $false
try {
    $pipCheck = & $venvPython -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $hasPip = $true
    }
} catch {
    $hasPip = $false
}

if (-not $hasPip) {
    Write-Host "ERROR: Virtual environment is corrupted (pip not found)!" -ForegroundColor Red
    Write-Host "Please run the installation script to recreate it:" -ForegroundColor Yellow
    Write-Host "  .\install.ps1" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Ensure selenium is available inside the venv
$seleniumCheck = & $venvPython -c "import selenium" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        Write-Host "Please run: .\install.ps1" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
    Write-Host "";
}

# Run the application
& $venvPython Auto_Capture_Tool.py
$exitCode = $LASTEXITCODE

# Keep window open and show exit code
Write-Host "";
if ($exitCode -eq 0) {
    Write-Host "Application exited successfully." -ForegroundColor Green
} else {
    Write-Host "Application exited with code: $exitCode" -ForegroundColor Yellow
}
Write-Host "Press Enter to close..." -ForegroundColor Gray
Read-Host
