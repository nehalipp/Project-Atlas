"""
Project Atlas
Phase 4 — Data Quality Profiling

Profiles the intentionally imperfect Phase 3 datasets.

This script does not modify source data.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent

SOURCE_DIR = (
    PHASE_DIR.parent
    / "03_Data_Generation"
    / "data"
    / "quality_issues"
)

REPORT_DIR = PHASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = [
    "accounts",
    "customers",
    "suppliers",
    "products",
    "locations",
    "employees",
    "machines",
    "sales",
    "production",
    "maintenance",
    "financial_transactions",
    "budget",
    "energy",
    "emissions",
    "waste",
    "inventory",
]


# ============================================================
# HELPERS
# ============================================================

def format_number(value):
    return f"{value:,}"


def profile_dataset(name):
    path = SOURCE_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = pd.read_csv(path)

    rows = len(df)
    columns = len(df.columns)
    missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    missing_pct = (
        round((missing / (rows * columns)) * 100, 2)
        if rows and columns
        else 0
    )

    return {
        "dataset": name,
        "records": rows,
        "columns": columns,
        "missing_values": missing,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Phase 4 Data Quality Profiling")
    print("=" * 70)

    print("\nProfiling quality-issue datasets...")

    results = []

    for name in DATASETS:

        result = profile_dataset(name)
        results.append(result)

        print(
            f"      ✓ {name + '.csv':<32}"
            f"{format_number(result['records']):>12} records"
        )

    report = pd.DataFrame(results)

    report.to_csv(
        REPORT_DIR / "data_profile_summary.csv",
        index=False,
    )

    print("\n" + "-" * 70)
    print("PROFILING SUMMARY")
    print("-" * 70)

    print(
        f"Datasets profiled                  : {len(report)}"
    )

    print(
        f"Total records                      : "
        f"{format_number(report['records'].sum())}"
    )

    print(
        f"Total missing values               : "
        f"{format_number(report['missing_values'].sum())}"
    )

    print(
        f"Total duplicate rows               : "
        f"{format_number(report['duplicate_rows'].sum())}"
    )

    print(
        f"Report                              : "
        f"{REPORT_DIR / 'data_profile_summary.csv'}"
    )

    print("\n" + "=" * 70)
    print("PHASE 4 PROFILING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()