#!/usr/bin/env python3
"""
Auto Capture Tool - Setup Script
Creates virtual environment and installs dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def get_venv_python():
    """Get the path to the venv Python executable."""
    if sys.platform == "win32":
        return Path("venv") / "Scripts" / "python.exe"
    return Path("venv") / "bin" / "python"


def get_venv_pip():
    """Get the path to the venv pip executable."""
    if sys.platform == "win32":
        return Path("venv") / "Scripts" / "pip.exe"
    return Path("venv") / "bin" / "pip"


def create_venv():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("Virtual environment already exists.")
        return True
    
    print("Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✓ Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False


def install_packages():
    """Install required packages into the virtual environment."""
    pip_path = get_venv_pip()
    
    if not pip_path.exists():
        print(f"✗ pip not found at {pip_path}")
        return False
    
    packages = ["selenium", "webdriver-manager", "Pillow"]
    
    print(f"Installing packages: {', '.join(packages)}...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([str(pip_path), "install", "--upgrade", "pip"])
        
        # Install packages
        subprocess.check_call([str(pip_path), "install"] + packages)
        
        print("✓ All packages installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False


def verify_installation():
    """Verify that all required packages are installed."""
    python_path = get_venv_python()
    
    print("\nVerifying installation...")
    
    try:
        result = subprocess.run(
            [str(python_path), "-c", 
             "import selenium; import PIL; from webdriver_manager.chrome import ChromeDriverManager; print('All imports successful!')"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ All dependencies verified.")
            return True
        else:
            print(f"✗ Verification failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 50)
    print("Auto Capture Tool - Setup")
    print("=" * 50)
    print()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    print()
    
    # Step 1: Create virtual environment
    if not create_venv():
        print("\nSetup failed at virtual environment creation.")
        sys.exit(1)
    
    # Step 2: Install packages
    if not install_packages():
        print("\nSetup failed at package installation.")
        sys.exit(1)
    
    # Step 3: Verify installation
    if not verify_installation():
        print("\nSetup completed but verification failed.")
        print("Try running manually: venv\\Scripts\\pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print()
    print("To run the application:")
    if sys.platform == "win32":
        print("  Double-click run_app.bat")
        print("  OR run: .\\run_app.ps1")
    else:
        print("  Run: ./venv/bin/python Auto_Capture_Tool.py")
    print()


if __name__ == "__main__":
    main()
