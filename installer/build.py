"""
Smart Flight Deck Companion - Build Script
Creates Windows executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
BRIDGE_DIR = ROOT_DIR / "bridge"
OUTPUT_DIR = ROOT_DIR / "installer" / "output"
DIST_DIR = BRIDGE_DIR / "dist"
BUILD_DIR = BRIDGE_DIR / "build"

# Application info
APP_NAME = "SmartFlightDeck"
APP_VERSION = "0.1.0"
MAIN_SCRIPT = BRIDGE_DIR / "main.py"


def clean():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")

    for path in [DIST_DIR, BUILD_DIR, OUTPUT_DIR]:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {path}")


def build():
    """Build the executable."""
    print(f"\nBuilding {APP_NAME} v{APP_VERSION}...")

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        APP_NAME,
        "--onedir",  # Create a directory with dependencies
        "--windowed",  # No console window (use --console for debugging)
        "--icon",
        str(ROOT_DIR / "installer" / "icon.ico"),
        # Add data files
        "--add-data",
        f"{BRIDGE_DIR / 'models'};models",
        # Hidden imports (modules that PyInstaller might miss)
        "--hidden-import",
        "uvicorn.logging",
        "--hidden-import",
        "uvicorn.protocols.http",
        "--hidden-import",
        "uvicorn.protocols.websockets",
        "--hidden-import",
        "uvicorn.lifespan.on",
        "--hidden-import",
        "uvicorn.lifespan.off",
        # Exclude unnecessary modules
        "--exclude-module",
        "matplotlib",
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "PyQt5",
        # Output
        "--distpath",
        str(OUTPUT_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(BRIDGE_DIR),
        # Main script
        str(MAIN_SCRIPT),
    ]

    # Check if icon exists
    icon_path = ROOT_DIR / "installer" / "icon.ico"
    if not icon_path.exists():
        # Remove icon argument if no icon
        cmd = [arg for arg in cmd if "icon.ico" not in str(arg)]
        cmd = [arg for arg in cmd if arg != "--icon"]

    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(BRIDGE_DIR))

    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    print("\nBuild completed successfully!")
    print(f"Output: {OUTPUT_DIR / APP_NAME}")


def create_launcher():
    """Create a simple launcher batch file."""
    launcher_content = f"""@echo off
title {APP_NAME}
cd /d "%~dp0"
"{APP_NAME}\\{APP_NAME}.exe" %*
pause
"""

    launcher_path = OUTPUT_DIR / f"Start_{APP_NAME}.bat"
    launcher_path.write_text(launcher_content)
    print(f"Created launcher: {launcher_path}")


def copy_resources():
    """Copy additional resources to output."""
    print("\nCopying resources...")

    # Create models directory in output
    models_output = OUTPUT_DIR / APP_NAME / "models"
    models_output.mkdir(parents=True, exist_ok=True)

    # Copy readme
    readme_content = f"""
{APP_NAME} v{APP_VERSION}
========================

Quick Start:
1. Run Start_{APP_NAME}.bat
2. Scan the QR code with your mobile app
3. Start MSFS and enjoy!

For more information, visit:
https://github.com/EnesTunc/smart-flight-deck

Support:
- Discord: [Your Discord]
- Email: support@smartflightdeck.com
"""

    readme_path = OUTPUT_DIR / "README.txt"
    readme_path.write_text(readme_content)
    print(f"Created: {readme_path}")


def main():
    """Main build process."""
    print("=" * 50)
    print(f"Building {APP_NAME}")
    print("=" * 50)

    clean()
    build()
    create_launcher()
    copy_resources()

    print("\n" + "=" * 50)
    print("Build complete!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
