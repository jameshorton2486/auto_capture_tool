import subprocess
import sys


def install():
    """
    Install packages with pinned versions from requirements.txt.
    Note: Use install.ps1 or install.bat instead for better cross-platform support.
    """
    print("Installing packages from requirements.txt...")
    print("Note: For best results, use install.ps1 (PowerShell) or install.bat (CMD) instead.")
    
    # Install from requirements.txt to ensure version consistency
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\nSuccess! All packages are installed.")


if __name__ == "__main__":
    install()