"""
Project Atlas
Phase 3 — Controlled Data Quality Issue Injection

Introduces deliberate, reproducible quality issues into the
clean business datasets.

The clean baseline is generated first.
This script then modifies selected source files in place.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SEED = 42

rng = np.random.default_rng(SEED)


# ============================================================
# Helper
# ============================================================

def load(filename):
    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    return pd.read_csv(path)


def save(df, filename):
    path = RAW_DATA_DIR / filename

    df.to_csv(
        path,
        index=False,
    )


def choose_rows(df, percentage):
    count = max(
        1,
        int(len(df) * percentage),
    )

    return rng.choice(
        df.index.to_numpy(),
        size=count,
        replace=False,
    )


# ============================================================
# Sales Quality Issues
# ============================================================

def inject_sales_issues():

    filename = "sales.csv"

    df = load(filename)

    # Missing product references
    missing_product_rows = choose_rows(
        df,
        0.02,
    )

    df.loc[
        missing_product_rows,
        "product_id",
    ] = np.nan

    # Negative quantities
    negative_quantity_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_quantity_rows,
        "quantity",
    ] *= -1

    # Revenue mismatches
    revenue_issue_rows = choose_rows(
        df,
        0.02,
    )

    df.loc[
        revenue_issue_rows,
        "revenue",
    ] = np.round(
        df.loc[
            revenue_issue_rows,
            "revenue",
        ] * 1.10,
        2,
    )

    # Duplicate records
    duplicate_rows = df.sample(
        n=max(
            1,
            int(len(df) * 0.02),
        ),
        random_state=SEED,
    )

    df = pd.concat(
        [
            df,
            duplicate_rows,
        ],
        ignore_index=True,
    )

    save(df, filename)

    print(
        "sales.csv: quality issues injected"
    )


# ============================================================
# Production Quality Issues
# ============================================================

def inject_production_issues():

    filename = "production.csv"

    df = load(filename)

    negative_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_rows,
        "produced_quantity",
    ] *= -1

    defect_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        defect_rows,
        "defect_quantity",
    ] = (
        df.loc[
            defect_rows,
            "produced_quantity",
        ].abs()
        * 1.25
    ).astype(int)

    missing_employee_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_employee_rows,
        "employee_id",
    ] = np.nan

    save(df, filename)

    print(
        "production.csv: quality issues injected"
    )


# ============================================================
# Maintenance Quality Issues
# ============================================================

def inject_maintenance_issues():

    filename = "maintenance.csv"

    df = load(filename)

    negative_cost_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_cost_rows,
        "maintenance_cost",
    ] *= -1

    missing_machine_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_machine_rows,
        "machine_id",
    ] = np.nan

    save(df, filename)

    print(
        "maintenance.csv: quality issues injected"
    )


# ============================================================
# Financial Quality Issues
# ============================================================

def inject_financial_issues():

    filename = "financial_transactions.csv"

    df = load(filename)

    negative_amount_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_amount_rows,
        "amount",
    ] *= -1

    missing_category_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_category_rows,
        "category",
    ] = np.nan

    save(df, filename)

    print(
        "financial_transactions.csv: "
        "quality issues injected"
    )


# ============================================================
# Budget Quality Issues
# ============================================================

def inject_budget_issues():

    filename = "budget.csv"

    df = load(filename)

    negative_budget_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_budget_rows,
        "budget_amount",
    ] *= -1

    missing_category_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_category_rows,
        "budget_category",
    ] = np.nan

    save(df, filename)

    print(
        "budget.csv: quality issues injected"
    )


# ============================================================
# Energy Quality Issues
# ============================================================

def inject_energy_issues():

    filename = "energy.csv"

    df = load(filename)

    negative_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_rows,
        "consumption",
    ] *= -1

    missing_type_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_type_rows,
        "energy_type",
    ] = np.nan

    save(df, filename)

    print(
        "energy.csv: quality issues injected"
    )


# ============================================================
# Emissions Quality Issues
# ============================================================

def inject_emissions_issues():

    filename = "emissions.csv"

    df = load(filename)

    negative_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_rows,
        "co2e_amount",
    ] *= -1

    missing_source_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_source_rows,
        "emission_source",
    ] = np.nan

    save(df, filename)

    print(
        "emissions.csv: quality issues injected"
    )


# ============================================================
# Waste Quality Issues
# ============================================================

def inject_waste_issues():

    filename = "waste.csv"

    df = load(filename)

    negative_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_rows,
        "waste_quantity",
    ] *= -1

    missing_type_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_type_rows,
        "waste_type",
    ] = np.nan

    save(df, filename)

    print(
        "waste.csv: quality issues injected"
    )


# ============================================================
# Inventory Quality Issues
# ============================================================

def inject_inventory_issues():

    filename = "inventory.csv"

    df = load(filename)

    negative_closing_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        negative_closing_rows,
        "closing_quantity",
    ] *= -1

    missing_product_rows = choose_rows(
        df,
        0.01,
    )

    df.loc[
        missing_product_rows,
        "product_id",
    ] = np.nan

    save(df, filename)

    print(
        "inventory.csv: quality issues injected"
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Quality Issue Injection")
    print("=" * 60)

    print("\nInjecting controlled quality issues...\n")

    inject_sales_issues()
    inject_production_issues()
    inject_maintenance_issues()
    inject_financial_issues()
    inject_budget_issues()
    inject_energy_issues()
    inject_emissions_issues()
    inject_waste_issues()
    inject_inventory_issues()

    print("\n" + "=" * 60)
    print("Quality issue injection complete.")
    print(f"Output directory: {RAW_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
