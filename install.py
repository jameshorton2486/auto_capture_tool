import subprocess
import sys


def install():
    # List of packages to install
    packages = ["selenium", "webdriver-manager", "Pillow"]

    print(f"Installing: {', '.join(packages)}...")

    # Run the pip install command via python
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)

    print("\nSuccess! All packages are installed.")


if __name__ == "__main__":
    install()