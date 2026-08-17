"""
Project Atlas
Phase 3 — Complete Data Generation

Workflow:

    1. Generate clean reference data
    2. Generate clean business data
    3. Validate clean reference data
    4. Validate clean business data
    5. Inject controlled quality issues

After this script completes, Phase 3 is complete.

Phase 4 will profile and evaluate the intentionally imperfect data.
"""

import subprocess
import sys
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "03_Data_Generation" / "scripts"


# ============================================================
# SCRIPT RUNNER
# ============================================================

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
            f"\nERROR: {filename} failed.\n"
            "Phase 3 cannot continue until the issue is resolved."
        )


# ============================================================
# MAIN WORKFLOW
# ============================================================

def main():

    print("=" * 60)
    print("PROJECT ATLAS — PHASE 3")
    print("DATA GENERATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Generate clean reference data
    # --------------------------------------------------------

    run_script("generate_reference_data.py")

    # --------------------------------------------------------
    # 2. Generate clean business data
    # --------------------------------------------------------

    run_script("generate_business_data.py")

    # --------------------------------------------------------
    # 3. Validate clean reference data
    # --------------------------------------------------------

    run_script("validate_reference_data.py")

    # --------------------------------------------------------
    # 4. Validate clean business data
    # --------------------------------------------------------

    run_script("validate_business_data.py")

    # --------------------------------------------------------
    # 5. Inject controlled quality issues
    # --------------------------------------------------------

    run_script("inject_quality_issues.py")

    # --------------------------------------------------------
    # PHASE 3 COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PHASE 3 — DATA GENERATION COMPLETE")
    print("=" * 60)

    print("""
The following has been completed:

1. Clean reference data generated
2. Clean business data generated
3. Clean reference data validated
4. Clean business data validated
5. Controlled data-quality issues injected

The raw datasets are now intentionally imperfect.

NEXT:
Proceed to Phase 4 — Data Quality.

Do NOT run the validation scripts or
inject_quality_issues.py manually.

Run this script again whenever you need
to regenerate the complete Phase 3 dataset.
""")

    print("=" * 60)


if __name__ == "__main__":
    main()
