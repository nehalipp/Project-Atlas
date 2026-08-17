from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent


def run_stage(script_name):
    """Run a Phase 3 script and stop the pipeline if it fails."""

    script_path = SCRIPT_DIR / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print()
        print(f"ERROR: {script_name} failed.")
        print()
        print("Details:")
        print("-" * 60)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        print("-" * 60)
        print()
        print("Phase 3 stopped.")
        print("Fix the error above and run:")
        print("python3 scripts/generate_all_data.py")

        sys.exit(result.returncode)


def main():
    print("Project Atlas — Phase 3: Data Generation")
    print("=========================================")
    print()

    # ---------------------------------------------------------
    # 1. Reference data
    # ---------------------------------------------------------
    print("[1/5] Generating reference data")

    run_stage("generate_reference_data.py")

    print("      ✓ 7 datasets generated")
    print()

    # ---------------------------------------------------------
    # 2. Business data
    # ---------------------------------------------------------
    print("[2/5] Generating business data")

    run_stage("generate_business_data.py")

    print("      ✓ 9 datasets generated")
    print()

    # ---------------------------------------------------------
    # 3. Clean baseline validation
    # ---------------------------------------------------------
    print("[3/5] Validating clean baseline")

    run_stage("validate_reference_data.py")
    print("      ✓ Reference data passed")

    run_stage("validate_business_data.py")
    print("      ✓ Business data passed")
    print()

    # ---------------------------------------------------------
    # 4. Quality issue injection
    # ---------------------------------------------------------
    print("[4/5] Injecting controlled quality issues")

    run_stage("inject_quality_issues.py")

    print("      ✓ 16 datasets updated")
    print()

    # ---------------------------------------------------------
    # 5. Finalization
    # ---------------------------------------------------------
    print("[5/5] Finalizing Phase 3")

    print("      ✓ Synthetic datasets are ready for Phase 4")
    print()

    print("Phase 3 complete.")
    print()
    print("Output:")
    print("data/raw/")
    print()
    print("Next phase:")
    print("Phase 4 — Data Quality")
    print()
    print("Run:")
    print("cd ../04_Data_Quality")


if __name__ == "__main__":
    main()
