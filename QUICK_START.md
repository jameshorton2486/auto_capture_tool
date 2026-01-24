# Quick Start Guide - Auto Capture Tool

## 🚀 Easiest Way to Run (Recommended)

### Step 1: Install (One-Time Setup)

**Option A: PowerShell (Recommended)**
1. Open PowerShell in the project folder
2. Right-click `install.ps1` → "Run with PowerShell"
   - OR run: `.\install.ps1`

**Option B: Command Prompt**
1. Double-click `install.bat`
   - OR open CMD and run: `install.bat`

The installation script will:
- ✅ Detect Python 3.13 (or any Python 3.x)
- ✅ Create a virtual environment (`venv/`)
- ✅ Install all dependencies
- ✅ Verify everything works

### Step 2: Run the Application

**Option A: PowerShell**
- Double-click `run_app.ps1`
- OR right-click → "Run with PowerShell"
- OR run: `.\run_app.ps1`

**Option B: Command Prompt**
- Double-click `run_app.bat`
- OR run: `run_app.bat`

That's it! The application will open automatically.

---

## 📝 Manual Method (If You Prefer)

### Step 1: Create Virtual Environment

Open PowerShell or CMD in the project folder:

```powershell
# PowerShell - Use Python 3.13 specifically
py -3.13 -m venv venv

# OR if 3.13 not available, use any Python 3.x
py -3 -m venv venv

# OR use python command
python -m venv venv
```

### Step 2: Activate Virtual Environment

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt (CMD):**
```cmd
venv\Scripts\activate.bat
```

You should see `(venv)` in your prompt.

### Step 3: Install Dependencies

With the virtual environment activated:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Run the Application

With the virtual environment still activated:

```powershell
python Auto_Capture_Tool.py
```

---

## 🔧 Troubleshooting

### "Python not found" Error

Make sure Python 3.13 is installed:
```powershell
py -3.13 --version
```

If that doesn't work, install Python 3.13 from [python.org](https://www.python.org/downloads/)

### "Virtual environment not found" Error

Run the installation script first:
```powershell
.\install.ps1
```

### "Execution Policy" Error in PowerShell

Allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "pip pointing to old Python" Error

If you see errors about pip pointing to Python 3.12:
1. Delete the old venv: `Remove-Item -Recurse -Force venv`
2. Run install script again: `.\install.ps1`
3. The script will use Python 3.13 correctly

### Tkinter GUI Error

The launcher scripts automatically fix this. Make sure you're using:
- `run_app.ps1` (PowerShell)
- `run_app.bat` (Command Prompt)

NOT running Python directly.

---

## 📂 Project Location

Your project is at:
```
C:\Users\james\auto_capture_tool\
```

Virtual environment is created at:
```
C:\Users\james\auto_capture_tool\venv\
```

---

## ✅ Verify Installation

After installation, verify everything works:

```powershell
# Check Python version in venv
.\venv\Scripts\python.exe --version

# Test imports
.\venv\Scripts\python.exe -c "import selenium; import PIL; import tkinter; print('All OK!')"
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| **Install** | `.\install.ps1` or `install.bat` |
| **Run App** | `.\run_app.ps1` or `run_app.bat` |
| **Activate venv** | `.\venv\Scripts\Activate.ps1` (PowerShell) or `venv\Scripts\activate.bat` (CMD) |
| **Deactivate venv** | `deactivate` |
| **Check Python** | `py -3.13 --version` |
| **Reinstall** | Delete `venv` folder, then run `.\install.ps1` |

---

## 💡 Tips

1. **Always use the launcher scripts** (`run_app.ps1` or `run_app.bat`) - they handle everything automatically
2. **If you get errors**, delete the `venv` folder and run `install.ps1` again
3. **The venv is isolated** - it won't affect your system Python
4. **No need to activate manually** - the launcher scripts do it for you
