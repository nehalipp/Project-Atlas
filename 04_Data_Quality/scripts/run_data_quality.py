"""
Project Atlas
Phase 4 — Data Quality Pipeline

Runs the complete Phase 4 workflow:

    Profile
        ↓
    Source Quality Validation
        ↓
    Remediation
        ↓
    Trusted Data Validation
"""

from pathlib import Path
import subprocess
import sys


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent


STEPS = [
    (
        "Data Profiling",
        "profile_data.py",
    ),
    (
        "Source Data Quality Validation",
        "validate_data_quality.py",
    ),
    (
        "Data Remediation",
        "remediate_data.py",
    ),
    (
        "Trusted Data Validation",
        "validate_trusted_data.py",
    ),
]


# ============================================================
# RUNNER
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
            str(SCRIPT_DIR / script),
        ],
        cwd=SCRIPT_DIR.parent.parent,
    )

    if result.returncode != 0:

        print("\n" + "-" * 70)
        print(
            f"✗ Step {number}/{total} failed."
        )
        print("-" * 70)

        sys.exit(
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
    print("Project Atlas — Phase 4 Data Quality Pipeline")
    print("=" * 70)

    print(
        """
Pipeline:
  Profile → Validate → Remediate → Trusted Validation
"""
    )

    total = len(STEPS)

    for number, (name, script) in enumerate(
        STEPS,
        start=1,
    ):

        run_step(
            number,
            total,
            name,
            script,
        )

    print("\n" + "-" * 70)
    print("PHASE 4 SUMMARY")
    print("-" * 70)

    print(
        "Status                              : PASSED"
    )

    print(
        "Source data                         : "
        "03_Data_Generation/data/quality_issues/"
    )

    print(
        "Trusted data                        : "
        "04_Data_Quality/data/trusted/"
    )

    print(
        "Reports                             : "
        "04_Data_Quality/reports/"
    )

    print(
        "Next phase                          : "
        "Phase 5 — ETL"
    )

    print("\n" + "=" * 70)
    print("PROJECT ATLAS — PHASE 4 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()