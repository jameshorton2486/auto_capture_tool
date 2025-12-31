# Full Screen Shots - Auto Capture Tool

Automated screenshot capture tool for web pages with full-page scrolling support.

## Prerequisites

- Python 3.11 or higher
- Google Chrome browser installed

## Quick Start

### Installation (One-Time Setup)

**Easy Way (Recommended) - Run the installation script:**

- **Windows PowerShell:** Right-click `install.ps1` → Run with PowerShell
- **Windows Command Prompt:** Double-click `install.bat`

Or run from command line:
```powershell
# PowerShell
.\install.ps1

# Command Prompt
install.bat
```

The installation script will:
1. Check for Python installation
2. Create a virtual environment (`venv/`)
3. Install all required dependencies
4. Verify the installation

### Running the Application

**Easy Way (Recommended) - Double-click one of these:**
- `run_app.bat` - For Command Prompt
- `run_app.ps1` - For PowerShell (right-click → Run with PowerShell)

These launcher scripts automatically:
- Check if the virtual environment exists
- Dynamically detect and set Tcl/Tk paths (fixes tkinter GUI issues)
- Install missing dependencies if needed
- Run the application
- Keep the window open if there's an error

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```powershell
# Navigate to project directory
cd C:\Users\james\auto_capture_tool

# Create virtual environment
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

You should see `(venv)` prefix in your terminal prompt.

### 3. Install Dependencies

With the virtual environment activated:

```powershell
# Install from requirements.txt
pip install -r requirements.txt
```

### 4. Run the Application Manually

```powershell
# Using venv Python directly (recommended)
.\venv\Scripts\python.exe Auto_Capture_Tool.py
```

## Updating Dependencies

If you add new packages:

```powershell
# Install the new package
pip install package-name==version

# Update requirements.txt with exact versions
pip freeze > requirements.txt
```

## Deactivating Virtual Environment

When you're done working on the project:

```powershell
deactivate
```

## Project Structure

```
auto_capture_tool/
├── venv/                      # Virtual environment (not in git, created by install script)
├── Auto_Capture_Tool.py       # Main application
├── install.bat                # 🚀 Installation script for CMD
├── install.ps1                # 🚀 Installation script for PowerShell
├── install.py                 # Legacy installer (use install.ps1/install.bat instead)
├── detect_tcl_tk.py           # Helper script to detect Tcl/Tk paths
├── run_app.bat                # 🚀 Quick launcher for CMD
├── run_app.ps1                # 🚀 Quick launcher for PowerShell
├── requirements.txt           # Pinned dependencies
├── pyproject.toml            # Modern Python project config
├── .python-version           # Python version specification
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Dependencies

- **selenium** (4.27.1) - Web automation framework
- **webdriver-manager** (4.0.2) - Automatic ChromeDriver management
- **Pillow** (11.0.0) - Image processing library

## Troubleshooting

### Virtual Environment Not Found Error

If you see "Virtual environment not found", run the installation script first:
```powershell
.\install.ps1  # PowerShell
# or
install.bat    # Command Prompt
```

### Tkinter GUI Error (`Can't find a usable init.tcl`)

The launcher scripts (`run_app.bat` or `run_app.ps1`) automatically detect and set the correct Tcl/Tk library paths. If you still encounter this error:

1. Make sure you're using the launcher scripts (not running Python directly)
2. If the error persists, the Python installation may be corrupted - try reinstalling Python

### Python Command Not Found

Make sure Python 3.11 or higher is installed and in your PATH. You can check by running:
```powershell
python --version
```

If Python is not found, install it from [python.org](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation.

### Module Not Found Errors

If you see module not found errors, the dependencies may not be installed. Run:
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Or simply run the installation script again:
```powershell
.\install.ps1
```

### Permission Errors on Windows

If you get execution policy errors in PowerShell, you may need to allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Notes

- The virtual environment (`venv/`) is excluded from git
- Always activate the virtual environment before working on the project
- Use `pip freeze > requirements.txt` to lock dependency versions after updates
