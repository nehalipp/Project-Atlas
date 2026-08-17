"""
Project Atlas
Phase 3 — Generate All Data

Runs the complete data-generation process:

1. Reference data
2. Business data
3. Quality issue injection
"""

from pathlib import Path
import subprocess
import sys


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(filename):

    script = SCRIPT_DIR / filename

    print("\n" + "=" * 60)
    print(f"Running {filename}")
    print("=" * 60)

    subprocess.run(
        [sys.executable, str(script)],
        check=True,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Complete Data Generation")
    print("=" * 60)

    run_script("generate_reference_data.py")
    run_script("generate_business_data.py")
    run_script("inject_quality_issues.py")

    print("\n" + "=" * 60)
    print("All data generation completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
