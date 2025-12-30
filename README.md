# Full Screen Shots - Auto Capture Tool

Automated screenshot capture tool for web pages with full-page scrolling support.

## Prerequisites

- Python 3.13.0 or higher
- Google Chrome browser installed

## Setup Instructions

### 1. Create Virtual Environment

Each project gets its own isolated environment to avoid dependency conflicts:

```powershell
# Navigate to project directory
cd C:\Users\james\full_screen_shots_

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

Or use the modern approach with pyproject.toml:

```powershell
pip install -e .
```

### 4. Run the Application

**Easy Way (Recommended) - Double-click one of these:**
- `run_app.bat` - For Command Prompt
- `run_app.ps1` - For PowerShell (right-click → Run with PowerShell)

These launchers automatically:
- Activate the virtual environment
- Set required Tcl/Tk paths for GUI
- Run the application
- Keep the window open if there's an error

**Manual Way:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Set Tcl/Tk paths (fixes GUI issues)
$env:TCL_LIBRARY = "C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
$env:TK_LIBRARY = "C:\Users\james\AppData\Local\Programs\Python\Python313\tcl\tk8.6"

# Run application
python Auto_Capture_Tool.py
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
full_screen_shots_/
├── venv/                      # Virtual environment (not in git)
├── Auto_Capture_Tool.py       # Main application
├── install.py                 # Legacy installer (use requirements.txt instead)
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

### Tkinter GUI Error (`Can't find a usable init.tcl`)

If you see this error, use the provided launcher scripts (`run_app.bat` or `run_app.ps1`) which automatically fix this issue. They set the correct Tcl/Tk library paths.

### Python Command Not Found

Make sure Python 3.13 is installed and in your PATH, or use the full path:
```powershell
C:\Users\james\AppData\Local\Programs\Python\Python313\python.exe -m venv venv
```

### Module Not Found Errors

Make sure you've activated the virtual environment and installed dependencies:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Notes

- The virtual environment (`venv/`) is excluded from git
- Always activate the virtual environment before working on the project
- Use `pip freeze > requirements.txt` to lock dependency versions after updates
