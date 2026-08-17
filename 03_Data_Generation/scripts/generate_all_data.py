"""
Project Atlas
Phase 3 — Complete Data Generation Pipeline

Workflow:

    1. Generate reference data
    2. Validate reference data
    3. Generate business data
    4. Validate business data
    5. Inject controlled quality issues

Clean baseline:

    03_Data_Generation/data/raw/

Intentionally imperfect data:

    03_Data_Generation/data/quality_issues/
"""

from pathlib import Path
import subprocess
import sys


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent


PIPELINE = [
    (
        "Reference Data Generation",
        SCRIPT_DIR / "generate_reference_data.py",
    ),
    (
        "Reference Data Validation",
        SCRIPT_DIR / "validate_reference_data.py",
    ),
    (
        "Business Data Generation",
        SCRIPT_DIR / "generate_business_data.py",
    ),
    (
        "Business Data Validation",
        SCRIPT_DIR / "validate_business_data.py",
    ),
    (
        "Controlled Quality Issue Injection",
        SCRIPT_DIR / "inject_quality_issues.py",
    ),
]


# ============================================================
# HELPERS
# ============================================================

def run_step(number, total, name, script):

    print("\n" + "=" * 70)
    print(
        f"PIPELINE STEP {number}/{total} — {name}"
    )
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(script),
        ],
        check=False,
    )

    if result.returncode != 0:

        print("\n" + "!" * 70)
        print(
            f"PIPELINE FAILED — {name}"
        )
        print("!" * 70)

        raise SystemExit(
            result.returncode
        )

    print(
        f"\n✓ Step {number}/{total} completed successfully."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Phase 3 Data Generation Pipeline")
    print("=" * 70)

    print(
        "\nPipeline:"
    )

    print(
        "  Reference Generation"
        " → Reference Validation"
        " → Business Generation"
        " → Business Validation"
        " → Quality Injection"
    )

    total_steps = len(PIPELINE)

    for number, (name, script) in enumerate(
        PIPELINE,
        start=1,
    ):

        run_step(
            number,
            total_steps,
            name,
            script,
        )

    print("\n" + "-" * 70)
    print("PHASE 3 SUMMARY")
    print("-" * 70)

    print(
        "Status                              : PASSED"
    )

    print(
        "Clean baseline                      : "
        "03_Data_Generation/data/raw/"
    )

    print(
        "Quality-issue dataset               : "
        "03_Data_Generation/data/quality_issues/"
    )

    print(
        "Next phase                          : "
        "Phase 4 — Data Quality"
    )

    print("\n" + "=" * 70)
    print("PROJECT ATLAS — PHASE 3 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()