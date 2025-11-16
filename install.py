"""Installer script for Le Sablenda using InnoSetup.

This script assumes the executable has already been built and signed (if needed)
by the build.py script. It runs the InnoSetup compiler to create the installer.

Prerequisites:
  - Inno Setup must be installed (https://jrsoftware.org/isdl.php)
  - The sablenda.dist directory must exist with the compiled executable
  - InnoSetup compiler (ISCC.exe) must be in PATH or findable
"""

import argparse
import subprocess
import sys
from pathlib import Path


def find_iscc() -> Path | None:
    """Find the InnoSetup compiler executable.

    Searches in common installation locations on Windows.

    Returns:
        Path to ISCC.exe if found, None otherwise
    """
    common_paths = [
        Path("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"),
        Path("C:\\Program Files\\Inno Setup 6\\ISCC.exe"),
        Path("C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe"),
        Path("C:\\Program Files\\Inno Setup 5\\ISCC.exe"),
    ]

    for path in common_paths:
        if path.exists():
            return path

    # Try to find via PATH
    try:
        result = subprocess.run(
            ["where", "ISCC.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass

    return None


def validate_build() -> bool:
    """Validate that the build directory exists and contains the executable.

    Returns:
        True if build is valid, False otherwise
    """
    build_dir = Path("sablenda.dist")

    if not build_dir.exists():
        print("❌ Error: sablenda.dist directory not found")
        print("   Please run build.py first to build the executable")
        return False

    exe_path = build_dir / "sablenda.exe"
    if not exe_path.exists():
        print("❌ Error: sablenda.exe not found in sablenda.dist directory")
        print("   Please run build.py first to build the executable")
        return False

    print(f"✓ Found executable: {exe_path}")
    return True


def validate_setup_script() -> bool:
    """Validate that the setup.iss script exists.

    Returns:
        True if script exists, False otherwise
    """
    setup_script = Path("setup.iss")

    if not setup_script.exists():
        print("❌ Error: setup.iss not found")
        return False

    print(f"✓ Found setup script: {setup_script}")
    return True


def create_installer_directory() -> None:
    """Create the installer output directory if it doesn't exist."""
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    print(f"✓ Using installer directory: {installer_dir}")


def run_innosetup(iscc_path: Path) -> bool:
    """Run the InnoSetup compiler to create the installer.

    Args:
        iscc_path: Path to ISCC.exe

    Returns:
        True if successful, False otherwise
    """
    setup_script = Path("setup.iss")

    try:
        print(f"\n🔨 Running InnoSetup compiler...")
        print(f"   Command: {iscc_path} {setup_script}\n")

        result = subprocess.run(
            [str(iscc_path), str(setup_script)],
            check=False
        )

        if result.returncode == 0:
            print("\n✓ Installer created successfully!")
            installer_path = Path("installer") / "Sablenda-Setup.exe"
            if installer_path.exists():
                print(f"✓ Installer location: {installer_path}")
                return True
        else:
            print(f"\n❌ InnoSetup compiler failed with code {result.returncode}")
            return False

    except FileNotFoundError:
        print(f"❌ Error: Could not find or execute {iscc_path}")
        return False
    except Exception as e:
        print(f"❌ Error running InnoSetup: {e}")
        return False


def main():
    """Main installation builder function."""
    parser = argparse.ArgumentParser(
        description="Build the Sablenda installer using InnoSetup"
    )
    parser.add_argument(
        "--iscc-path",
        type=Path,
        help="Path to ISCC.exe (InnoSetup compiler). If not provided, will search common locations"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Le Sablenda - Installer Builder")
    print("=" * 60)

    # Validate prerequisites
    print("\n📋 Checking prerequisites...")
    if not validate_setup_script():
        sys.exit(1)

    if not validate_build():
        sys.exit(1)

    create_installer_directory()

    # Find ISCC if not provided
    iscc_path = args.iscc_path
    if iscc_path is None:
        print("\n🔍 Searching for InnoSetup compiler...")
        iscc_path = find_iscc()
        if iscc_path is None:
            print("❌ Error: Could not find InnoSetup compiler")
            print("   Please install InnoSetup from: https://jrsoftware.org/isdl.php")
            print("   Or provide the path using --iscc-path option")
            sys.exit(1)

    print(f"✓ Found InnoSetup compiler: {iscc_path}")

    # Run the installer builder
    if not run_innosetup(iscc_path):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Installation completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
