"""
Project Atlas
Phase 3 — Generate All Clean Data

Creates the clean reference and business datasets.

Quality issues are NOT injected here.

Workflow:

    generate_all_data.py
            ↓
        clean data
            ↓
    validation scripts
            ↓
    inject_quality_issues.py
"""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "03_Data_Generation" / "scripts"


def run_script(filename):

    script = SCRIPTS_DIR / filename

    print("\n" + "=" * 60)
    print(f"Running {filename}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script)],
        check=False,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"\nERROR: {filename} failed."
        )


def main():

    print("=" * 60)
    print("Project Atlas — Clean Data Generation")
    print("=" * 60)

    run_script("generate_reference_data.py")
    run_script("generate_business_data.py")

    print("\n" + "=" * 60)
    print("CLEAN DATA GENERATION COMPLETE")
    print("=" * 60)

    print("\nNext steps:")
    print("1. validate_reference_data.py")
    print("2. validate_business_data.py")
    print("3. inject_quality_issues.py")


if __name__ == "__main__":
    main()
