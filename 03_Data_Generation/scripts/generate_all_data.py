"""
Project Atlas
Phase 3 — Complete Data Generation Pipeline

Runs the complete reproducible source-data generation process:

1. Reference data
2. Reference validation
3. Clean business data
4. Clean business-data validation
5. Controlled quality-issue injection
6. Final raw-data validation
"""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "03_Data_Generation" / "scripts"


def run_script(script_name, arguments=None):

    if arguments is None:
        arguments = []

    script_path = SCRIPTS_DIR / script_name

    command = [
        sys.executable,
        str(script_path),
        *arguments,
    ]

    print("\n" + "=" * 60)
    print(f"Running: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:

        print(
            f"\nPIPELINE STOPPED: {script_name} failed."
        )

        sys.exit(
            result.returncode
        )


def main():

    print("=" * 60)
    print("Project Atlas — Complete Data Generation")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Reference Data
    # --------------------------------------------------------

    run_script(
        "generate_reference_data.py"
    )

    # --------------------------------------------------------
    # 2. Reference Validation
    # --------------------------------------------------------

    run_script(
        "validate_reference_data.py"
    )

    # --------------------------------------------------------
    # 3. Clean Business Data
    # --------------------------------------------------------

    run_script(
        "generate_business_data.py"
    )

    # --------------------------------------------------------
    # 4. Clean Business Data Validation
    # --------------------------------------------------------

    run_script(
        "validate_business_data.py"
    )

    # --------------------------------------------------------
    # 5. Controlled Quality Issues
    # --------------------------------------------------------

    run_script(
        "inject_quality_issues.py"
    )

    # --------------------------------------------------------
    # 6. Final Raw Data Validation
    # --------------------------------------------------------

    run_script(
        "validate_business_data.py",
        ["--final"],
    )

    print("\n" + "=" * 60)
    print("COMPLETE DATA GENERATION PIPELINE PASSED")
    print("=" * 60)

    print(
        "\nFinal source datasets are available under:"
    )

    print(
        PROJECT_ROOT / "data" / "raw"
    )


if __name__ == "__main__":
    main()
