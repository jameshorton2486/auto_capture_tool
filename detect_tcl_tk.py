"""
Helper script to detect Tcl/Tk library paths for the current Python installation.
This is used by run_app.bat and run_app.ps1 to set environment variables.
"""
import sys
import os

def find_tcl_tk_paths():
    """Find Tcl/Tk library paths for the current Python installation."""
    # Get the base Python installation directory (not the venv)
    base_prefix = sys.base_prefix
    py_dir = os.path.dirname(sys.executable)
    
    # Common locations for Tcl/Tk in the base Python installation
    possible_tcl_paths = [
        # In base Python directory
        os.path.join(base_prefix, 'tcl', 'tcl8.6'),
        # One level up from base Python
        os.path.join(os.path.dirname(base_prefix), 'tcl', 'tcl8.6'),
        # In the Python executable directory (for portable installs)
        os.path.join(py_dir, 'tcl', 'tcl8.6'),
        # Parent of executable directory
        os.path.join(os.path.dirname(py_dir), 'tcl', 'tcl8.6'),
        # Legacy locations
        os.path.join(os.path.dirname(os.path.dirname(base_prefix)), 'tcl', 'tcl8.6'),
    ]
    
    # Try to find Tcl path
    for tcl_path in possible_tcl_paths:
        abs_tcl_path = os.path.abspath(tcl_path)
        if os.path.exists(abs_tcl_path):
            # Tk is usually in the same parent directory
            tk_path = os.path.join(os.path.dirname(abs_tcl_path), 'tk8.6')
            if os.path.exists(tk_path):
                print(abs_tcl_path)
                print(os.path.abspath(tk_path))
                return
    
    # If not found, print empty lines (scripts will handle it)
    print("")
    print("")

if __name__ == "__main__":
    find_tcl_tk_paths()
