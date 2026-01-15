#!/usr/bin/env python3
"""
Install All Dependencies for Claude Project Planner

Installs all dependencies from requirements-full-plan.txt during initial setup.
This ensures users can switch between providers without re-running setup.

Usage:
    python scripts/install-all-dependencies.py [--verbose]
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def get_requirements_file() -> Path:
    """Get path to requirements file."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "requirements-full-plan.txt"


def parse_requirements() -> List[str]:
    """Parse requirements file and extract package names."""
    requirements_file = get_requirements_file()

    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        sys.exit(1)

    packages = []
    with open(requirements_file) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Extract package name (before >=, ==, etc.)
            package = line.split('>=')[0].split('==')[0].split('<')[0].strip()
            if package:
                packages.append(package)

    return packages


def check_if_installed(package: str) -> bool:
    """Check if a package is already installed."""
    # Map package name to import name
    import_names = {
        "python-dotenv": "dotenv",
        "pyyaml": "yaml",
        "python-pptx": "pptx",
        "pillow": "PIL",
        "google-genai": "google.genai",
        "claude-agent-sdk": "claude_agent_sdk",
    }

    import_name = import_names.get(package, package.replace('-', '_'))

    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(package: str, verbose: bool = False) -> Tuple[bool, str]:
    """
    Install a package using pip.

    Returns:
        (success, error_message)
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install", package, "--quiet"]
        if not verbose:
            cmd.append("--no-warn-script-location")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per package
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr or result.stdout

    except subprocess.TimeoutExpired:
        return False, "Installation timeout (5 minutes exceeded)"
    except Exception as e:
        return False, str(e)


def main():
    """Main installation routine."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print("=" * 70)
    print("  Claude Project Planner - Dependency Installation")
    print("=" * 70)
    print()

    # Parse requirements
    print("📦 Reading requirements...")
    packages = parse_requirements()
    total = len(packages)
    print(f"   Found {total} packages to install\n")

    # Track results
    installed = []
    skipped = []
    failed = []

    # Install each package
    for i, package in enumerate(packages, 1):
        progress = f"[{i}/{total}]"

        # Check if already installed
        if check_if_installed(package):
            print(f"{progress} ✓ {package:30} (already installed)")
            skipped.append(package)
            continue

        # Install package
        print(f"{progress} ⏳ {package:30} ", end="", flush=True)
        success, error = install_package(package, verbose)

        if success:
            print("✅ installed")
            installed.append(package)
        else:
            print(f"❌ failed")
            if verbose and error:
                print(f"      Error: {error}")
            failed.append((package, error))

    # Summary
    print()
    print("=" * 70)
    print("  Installation Summary")
    print("=" * 70)
    print(f"✅ Installed:     {len(installed)}")
    print(f"⏭️  Already had:   {len(skipped)}")
    print(f"❌ Failed:        {len(failed)}")
    print()

    if failed:
        print("Failed packages:")
        for package, error in failed:
            print(f"  • {package}")
            if verbose and error:
                print(f"    └─ {error[:100]}")
        print()
        print("💡 Tip: Some packages may require system dependencies.")
        print("   Try installing manually: pip install <package-name>")
        sys.exit(1)

    print("✨ All dependencies installed successfully!")
    print()
    print("You can now use:")
    print("  • /full-plan (comprehensive project planning)")
    print("  • /tech-plan (technical planning only)")
    print("  • /research-lookup (AI-powered research)")
    print("  • /generate-report (PDF/DOCX reports)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
