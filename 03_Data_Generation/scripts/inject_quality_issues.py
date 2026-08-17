"""
Project Atlas
Phase 3 — Controlled Data Quality Issue Injection

Creates an intentionally imperfect copy of the clean baseline.

Issue types:

    Missing values
    Duplicate records
    Invalid references
    Invalid values
    Outliers

The clean baseline in data/raw is never modified.

Output:

    03_Data_Generation/data/quality_issues/
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    DUPLICATE_RATE,
    INVALID_REFERENCE_RATE,
    INVALID_VALUE_RATE,
    MISSING_RATE,
    OUTLIER_RATE,
    RAW_DATA_DIR,
    SEED,
)


# ============================================================
# PATHS AND SETUP
# ============================================================

QUALITY_DATA_DIR = (
    RAW_DATA_DIR.parent / "quality_issues"
)

QUALITY_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

rng = np.random.default_rng(SEED)


REFERENCE_FILES = [
    "accounts.csv",
    "customers.csv",
    "suppliers.csv",
    "products.csv",
    "locations.csv",
    "employees.csv",
    "machines.csv",
]

BUSINESS_FILES = [
    "sales.csv",
    "production.csv",
    "maintenance.csv",
    "financial_transactions.csv",
    "budget.csv",
    "energy.csv",
    "emissions.csv",
    "waste.csv",
    "inventory.csv",
]


REFERENCE_COLUMNS = {
    "accounts.csv": [],
    "customers.csv": ["account_id"],
    "suppliers.csv": [],
    "products.csv": ["supplier_id"],
    "locations.csv": [],
    "employees.csv": ["location_id"],
    "machines.csv": ["location_id"],
}


BUSINESS_COLUMNS = {
    "sales.csv": [
        "account_id",
        "customer_id",
        "product_id",
        "location_id",
    ],
    "production.csv": [
        "product_id",
        "location_id",
        "machine_id",
        "employee_id",
    ],
    "maintenance.csv": [
        "location_id",
        "machine_id",
        "employee_id",
    ],
    "financial_transactions.csv": [
        "location_id",
    ],
    "budget.csv": [
        "location_id",
    ],
    "energy.csv": [
        "location_id",
    ],
    "emissions.csv": [
        "location_id",
    ],
    "waste.csv": [
        "location_id",
    ],
    "inventory.csv": [
        "product_id",
        "location_id",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def load_csv(filename):

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing clean dataset: {path}\n"
            "Run Phase 3 generation first."
        )

    return pd.read_csv(path)


def save_csv(df, filename):

    df.to_csv(
        QUALITY_DATA_DIR / filename,
        index=False,
    )


def choose_rows(df, rate):

    if rate <= 0 or len(df) == 0:
        return np.array([], dtype=int)

    count = max(
        1,
        int(len(df) * rate),
    )

    return rng.choice(
        len(df),
        size=count,
        replace=False,
    )


def inject_missing_values(df):

    protected = {
        column
        for column in df.columns
        if column.endswith("_id")
    }

    candidates = [
        column
        for column in df.columns
        if column not in protected
    ]

    rows = choose_rows(
        df,
        MISSING_RATE,
    )

    for row in rows:

        column = rng.choice(
            candidates
        )

        df.at[
            row,
            column,
        ] = np.nan

    return len(rows)


def inject_duplicates(df):

    rows = choose_rows(
        df,
        DUPLICATE_RATE,
    )

    if len(rows) == 0:
        return df, 0

    duplicates = df.iloc[rows].copy()

    result = pd.concat(
        [
            df,
            duplicates,
        ],
        ignore_index=True,
    )

    return result, len(duplicates)


def inject_invalid_references(
    df,
    columns,
):

    changes = 0

    for column in columns:

        rows = choose_rows(
            df,
            INVALID_REFERENCE_RATE,
        )

        for row in rows:

            df.at[
                row,
                column,
            ] = (
                f"INVALID-{column.upper()}-{row:08d}"
            )

        changes += len(rows)

    return changes


def inject_invalid_values(df):

    changes = 0

    numeric_columns = [
        "quantity",
        "quantity_produced",
        "quantity_on_hand",
        "reorder_point",
        "production_hours",
        "downtime_hours",
        "consumption",
        "co2_kg",
        "maintenance_cost",
        "amount",
        "budget_amount",
        "inventory_value",
    ]

    for column in numeric_columns:

        if column not in df.columns:
            continue

        rows = choose_rows(
            df,
            INVALID_VALUE_RATE,
        )

        if len(rows) == 0:
            continue

        df.loc[
            rows,
            column,
        ] = -1

        changes += len(rows)

    if "discount_rate" in df.columns:

        rows = choose_rows(
            df,
            INVALID_VALUE_RATE,
        )

        df.loc[
            rows,
            "discount_rate",
        ] = 1.50

        changes += len(rows)

    return changes


def inject_outliers(df):

    numeric_columns = [
        column
        for column in df.columns
        if pd.api.types.is_numeric_dtype(
            df[column]
        )
    ]

    changes = 0

    for column in numeric_columns:

        rows = choose_rows(
            df,
            OUTLIER_RATE,
        )

        if len(rows) == 0:
            continue

        median = df[column].median()

        if pd.isna(median):
            continue

        df.loc[
            rows,
            column,
        ] = median * 100

        changes += len(rows)

    return changes


# ============================================================
# DATASET PROCESSING
# ============================================================

def process_dataset(
    filename,
    reference_columns,
):

    df = load_csv(filename)

    original_count = len(df)

    missing = inject_missing_values(df)

    df, duplicates = inject_duplicates(df)

    invalid_references = (
        inject_invalid_references(
            df,
            reference_columns,
        )
    )

    invalid_values = (
        inject_invalid_values(df)
    )

    outliers = (
        inject_outliers(df)
    )

    save_csv(
        df,
        filename,
    )

    return {
        "dataset": filename,
        "original_records": original_count,
        "final_records": len(df),
        "missing_values": missing,
        "duplicates": duplicates,
        "invalid_references": invalid_references,
        "invalid_values": invalid_values,
        "outliers": outliers,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Quality Issue Injection")
    print("=" * 70)

    print(
        "\nCreating intentionally imperfect copies..."
    )

    results = []

    all_files = (
        REFERENCE_FILES
        + BUSINESS_FILES
    )

    all_columns = {
        **REFERENCE_COLUMNS,
        **BUSINESS_COLUMNS,
    }

    for filename in all_files:

        result = process_dataset(
            filename,
            all_columns.get(
                filename,
                [],
            ),
        )

        results.append(result)

        print(
            f"      ✓ {filename:<32}"
            f"{result['final_records']:>10,} records"
        )

    summary = pd.DataFrame(
        results
    )

    summary.to_csv(
        QUALITY_DATA_DIR
        / "quality_injection_summary.csv",
        index=False,
    )

    total_original = (
        summary["original_records"].sum()
    )

    total_final = (
        summary["final_records"].sum()
    )

    total_missing = (
        summary["missing_values"].sum()
    )

    total_duplicates = (
        summary["duplicates"].sum()
    )

    total_invalid_refs = (
        summary["invalid_references"].sum()
    )

    total_invalid_values = (
        summary["invalid_values"].sum()
    )

    total_outliers = (
        summary["outliers"].sum()
    )

    print("\n" + "-" * 70)
    print("QUALITY INJECTION SUMMARY")
    print("-" * 70)
    print(f"Datasets processed                  : {len(all_files)}")
    print(f"Original records                    : {total_original:,.0f}")
    print(f"Final records                       : {total_final:,.0f}")
    print(f"Missing values introduced            : {total_missing:,.0f}")
    print(f"Duplicate records introduced         : {total_duplicates:,.0f}")
    print(f"Invalid references introduced        : {total_invalid_refs:,.0f}")
    print(f"Invalid values introduced            : {total_invalid_values:,.0f}")
    print(f"Outliers introduced                  : {total_outliers:,.0f}")
    print(f"Output                              : {QUALITY_DATA_DIR}")

    print("\n" + "=" * 70)
    print("QUALITY ISSUE INJECTION COMPLETE")
    print("=" * 70)

    print(
        "\nIntentionally imperfect data is ready "
        "for Phase 4 — Data Quality."
    )


if __name__ == "__main__":
    main()