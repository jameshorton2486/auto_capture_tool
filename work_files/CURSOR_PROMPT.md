# Cursor AI Prompt: Auto Capture Tool Fixes

## Project Context

This is a Python/Tkinter application (`Auto_Capture_Tool.py`) for capturing full-page screenshots from URLs using Selenium. The tool needs several fixes related to missing functionality, login handling, and virtual environment setup.

---

## ISSUES TO FIX

### 1. CRITICAL: Zip Functionality Was Missing (NOW FIXED)

**Problem:** The user described adding a "Zip Files" button with 29MB auto-split, but the code had NO zip functionality at all - no button, no import, no methods.

**Solution Applied:**
- Added `import zipfile` at top
- Added `MAX_ZIP_SIZE_BYTES = 29 * 1024 * 1024` class constant
- Added `is_zipping` tracker
- Added `zip_btn` button (orange) in button bar
- Added `zip_files()` method - opens save dialog, collects files, runs in thread
- Added `_create_zip_files()` method - handles splitting at 29MB boundary
- Added `_format_size()` static method for display

**Verify:** Check that the Zip Files button appears and functions correctly.

---

### 2. CRITICAL: Login Page Stuck Issue (NOW FIXED)

**Problem:** App gets stuck on login pages because Chrome opens fresh each time with no session data.

**Solution Applied:**
- Added `chrome_user_data_dir` for persistent Chrome profile storage at `~/.auto_capture_tool/chrome_profile`
- Added "Keep login sessions" checkbox (`persist_session_var`)
- Added "Open Browser" button (`login_btn`) for manual pre-authentication
- Added `open_browser_for_login()` method
- Modified `_capture_loop()` to:
  - Reuse existing browser if opened for login
  - Use persistent profile when enabled
  - Only close browser if it was created during capture

**Verify:** Test the login flow:
1. Click "Open Browser"
2. Login to a site manually
3. Click "Start" - should use same browser with session

---

### 3. CRITICAL: Virtual Environment Issues (NOW FIXED)

**Problem:** 
- TCL/TK paths hardcoded to `C:\Users\james\...`
- `install.py` didn't create/use venv
- Run scripts assumed venv exists

**Solution Applied:**

**run_app.bat:**
- Auto-creates venv if missing
- Dynamically detects Python's TCL/TK paths
- Installs requirements automatically

**run_app.ps1:**
- Same improvements as batch file
- Better error messages with colors

**install.py:**
- Creates venv properly
- Installs to venv (not system)
- Verifies installation works

---

### 4. MEDIUM: Static Method Call Bug (NOW FIXED)

**Problem:** `flatten_rgba` was `@staticmethod` but called as `self.flatten_rgba(img)`

**Solution:** Changed to `AutoCaptureTool.flatten_rgba(img)` in `_save_file()` method.

---

### 5. LOW: Hardcoded Default Directory (NOW FIXED)

**Problem:** Default save directory was hardcoded to `G:\My Drive\Kollect-It\CTBids Screen Shots`

**Solution:** Added fallback to `~/Documents/Screenshots` if the default path doesn't exist.

---

## REMAINING TASKS FOR CURSOR

If you need to make additional changes, here are areas to verify or enhance:

### A. Test the Zip Split Logic

The zip splitting logic estimates size before adding files. Verify it works correctly:

```python
# In _create_zip_files(), the logic should:
# 1. Track current_zip_size as files are added
# 2. When current_zip_size + file_size > MAX_ZIP_SIZE_BYTES:
#    - Close current zip
#    - Start new zip with _part{N}.zip suffix
# 3. Handle edge case where single file > 29MB (currently adds to zip anyway)
```

### B. Add Error Recovery for Chrome Profile

If the Chrome profile gets corrupted, users may get stuck. Consider adding:

```python
def clear_chrome_profile(self):
    """Clear stored Chrome profile if it's causing issues."""
    import shutil
    if os.path.exists(self.chrome_user_data_dir):
        shutil.rmtree(self.chrome_user_data_dir)
        self.log("Chrome profile cleared.")
```

### C. Consider Adding These Enhancements

1. **Headless Mode Toggle** - Currently browser always shows. Add checkbox for headless capture (won't work with manual login).

2. **Resume Failed Captures** - Track which URLs succeeded and allow resuming.

3. **Concurrent Captures** - Use thread pool for faster batch processing (complex due to single browser).

4. **Export URL List** - Save/load URL lists to file.

---

## FILE STRUCTURE AFTER FIXES

```
auto_capture_tool-main/
├── Auto_Capture_Tool.py   # Main app (NOW HAS: zip, login handling, fixes)
├── install.py             # Setup script (NOW: creates venv properly)
├── requirements.txt       # Dependencies (unchanged)
├── run_app.bat           # Launcher (NOW: dynamic paths, auto-setup)
├── run_app.ps1           # Launcher (NOW: dynamic paths, auto-setup)
├── pyproject.toml        # Package config
├── .gitignore
├── .python-version
└── README.md             # Updated documentation
```

---

## TESTING CHECKLIST

- [ ] App launches without errors: `python Auto_Capture_Tool.py`
- [ ] Zip Files button visible and positioned correctly
- [ ] Zip creates file(s) in chosen location
- [ ] Zip splits at ~29MB boundary with multiple files
- [ ] "Open Browser" button opens Chrome
- [ ] Manual login persists when "Start" clicked
- [ ] "Keep login sessions" checkbox saves cookies between app restarts
- [ ] run_app.bat creates venv if missing
- [ ] run_app.bat installs requirements if needed
- [ ] No hardcoded user paths in run scripts
- [ ] Default directory falls back gracefully

---

## KEY CODE LOCATIONS

| Feature | File | Lines/Methods |
|---------|------|---------------|
| Zip button | Auto_Capture_Tool.py | `_build_ui()` button section |
| Zip logic | Auto_Capture_Tool.py | `zip_files()`, `_create_zip_files()` |
| Login handling | Auto_Capture_Tool.py | `open_browser_for_login()` |
| Session persistence | Auto_Capture_Tool.py | `chrome_user_data_dir`, Chrome options |
| Venv setup | run_app.bat | Lines 12-25 |
| TCL/TK paths | run_app.bat | Lines 28-32 |
