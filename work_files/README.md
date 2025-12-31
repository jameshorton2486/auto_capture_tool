# Auto Full Page Capture Tool

A Python/Tkinter application for capturing full-page screenshots from multiple URLs. Features session persistence for sites requiring login and automatic zip file creation with splitting for large collections.

## Features

- **Full Page Screenshots** - Captures entire page height, not just viewport
- **Multiple Formats** - PNG, JPG, or PDF output
- **Batch Processing** - Process multiple URLs at once
- **Session Persistence** - Saves login sessions between runs (optional)
- **Manual Login Support** - "Open Browser" button lets you login before capturing
- **Zip Files** - Creates zip archives with automatic 29MB split for large collections
- **Domain-based Organization** - Automatically organizes files by domain
- **Progress Tracking** - Real-time log output and progress bar

## Requirements

- Python 3.10 or higher
- Google Chrome browser installed
- Windows 10/11 (tested) or macOS/Linux

## Installation

### Option 1: Automatic Setup (Recommended)

```bash
python install.py
```

This creates a virtual environment and installs all dependencies.

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Windows

Double-click `run_app.bat` or run in PowerShell:

```powershell
.\run_app.ps1
```

### Manual Run

```bash
# Activate venv first, then:
python Auto_Capture_Tool.py
```

## Usage

### Basic Capture

1. Set your save folder using "Browse..."
2. Paste URLs (one per line) in the text area
3. Select output format (PNG/JPG/PDF)
4. Click "Start"

### Sites Requiring Login

1. Click "Open Browser" button
2. Navigate and login to required sites in the browser window
3. Paste your URLs
4. Click "Start" - the browser will keep your login session

The "Keep login sessions" checkbox (enabled by default) stores session cookies between runs.

### Creating Zip Files

1. Capture some screenshots first
2. Click "Zip Files"
3. Choose save location
4. If total size exceeds 29MB, multiple part files are created automatically

## Troubleshooting

### "Virtual environment not found"

Run `python install.py` or create manually:
```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### Tkinter/GUI not showing

The run scripts automatically set TCL/TK paths. If issues persist, ensure Python was installed with tkinter support (default on most installers).

### ChromeDriver issues

The app auto-downloads the correct ChromeDriver version. Ensure Chrome is installed and up to date.

### Stuck on login page

Use the "Open Browser" button to manually login before starting capture. Enable "Keep login sessions" to preserve logins between runs.

## File Structure

```
auto_capture_tool/
├── Auto_Capture_Tool.py   # Main application
├── install.py             # Setup script
├── requirements.txt       # Python dependencies
├── run_app.bat           # Windows batch launcher
├── run_app.ps1           # PowerShell launcher
└── README.md             # This file
```

## Dependencies

- `selenium` - Browser automation
- `webdriver-manager` - Automatic ChromeDriver management
- `Pillow` - Image processing
- `tkinter` - GUI (included with Python)

## License

MIT License
