# Full Screen Shots - Auto Capture Tool

Automated screenshot capture tool for web pages with full-page scrolling support.

## Features

- ✅ Full-page screenshot capture (scrolls entire page)
- ✅ Multiple output formats: PNG, JPG, PDF
- ✅ **Persistent login sessions** - log in once, capture all protected pages
- ✅ **Server connectivity check** - warns you if dev server isn't running
- ✅ Smart login detection with configurable wait times
- ✅ Retry logic for failed captures
- ✅ Zip all captures for easy sharing
- ✅ Dark theme UI

## Quick Start for Local Development Sites

### First-Time Setup (One-Time)

**Install the application:**
- **PowerShell:** Right-click `install.ps1` → "Run with PowerShell" (or run `.\install.ps1`)
- **Command Prompt:** Double-click `install.bat` (or run `install.bat`)

This creates a virtual environment and installs all dependencies.

### Running the Application

**Easiest Way - Double-click:**
- `run_app.ps1` (PowerShell - right-click → "Run with PowerShell")
- `run_app.bat` (Command Prompt - just double-click)

**Or from command line:**
```powershell
.\run_app.ps1    # PowerShell
run_app.bat      # Command Prompt
```

The launcher scripts automatically:
- ✅ Check if virtual environment exists
- ✅ Detect Tcl/Tk paths (fixes tkinter GUI issues)
- ✅ Install missing dependencies if needed
- ✅ Run the application

### For Protected Pages (Login Required)

1. **Start your dev server first:**
   ```bash
   cd your-project-folder
   npm run dev
   # Wait for "Ready" message
   ```

2. **Run the capture tool:** Double-click `run_app.ps1` or `run_app.bat`

3. **Login workflow:**
   - Click **"Open Browser"** button
   - Log in to your website in the browser window
   - Click **"Start"** - all pages will be captured with your logged-in session

**Important:** The tool will check if your server is running before starting. If you see "Server Not Running" error, make sure `npm run dev` is running first.

### Manual Method (If You Prefer)

If you want to activate the virtual environment manually:

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
python Auto_Capture_Tool.py
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
python Auto_Capture_Tool.py
```

See `QUICK_START.md` for detailed instructions.

## Prerequisites

- Python 3.11+ (tested with 3.13.0)
- Google Chrome browser installed

## Installation (One-Time Setup)

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

## Running the Application

**Easy Way (Recommended) - Double-click one of these:**
- `run_app.bat` - For Command Prompt
- `run_app.ps1` - For PowerShell (right-click → Run with PowerShell)

These launcher scripts automatically:
- Check if the virtual environment exists
- Dynamically detect and set Tcl/Tk paths (fixes tkinter GUI issues)
- Install missing dependencies if needed
- Run the application
- Keep the window open if there's an error

## Options Explained

| Option | Description |
|--------|-------------|
| **Include domain in folder structure** | Creates subfolders by domain name |
| **Skip login pages** | Skips pages that require authentication (not recommended) |
| **Keep login sessions** | Saves Chrome profile between runs so you stay logged in |
| **Run headless** | Runs browser invisibly (no window) |

## Tips for Best Results

1. **Always use "Open Browser" for protected pages** - Log in first, then start capture
2. **Keep "Keep login sessions" checked** - Your login persists between app restarts
3. **Increase delay for slow-loading pages** - Use 3-5 seconds for JavaScript-heavy sites
4. **Use "Retry Failed"** after fixing issues - Don't re-capture everything

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```powershell
# Navigate to project directory
cd path\to\auto_capture_tool

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

### "Server Not Running" Error
Make sure your development server is running before starting capture:
```bash
npm run dev  # or whatever starts your dev server
```

### Capturing Login Pages Instead of Actual Content
This means you're not logged in. Solution:
1. Click "Open Browser" 
2. Log in to your website
3. Then click "Start"

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

Make sure Python 3.11+ is installed and in your PATH. You can check by running:
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
