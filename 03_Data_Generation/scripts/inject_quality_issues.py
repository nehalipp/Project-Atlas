"""
Project Atlas
Phase 3 — Controlled Data Quality Issue Injection

Adds deliberate and reproducible quality issues
to the clean business datasets.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SEED = 42
rng = np.random.default_rng(SEED)


# ============================================================
# HELPERS
# ============================================================

def load(filename):
    return pd.read_csv(RAW_DATA_DIR / filename)


def save(df, filename):
    df.to_csv(
        RAW_DATA_DIR / filename,
        index=False,
    )


def choose_rows(df, percentage):
    count = max(
        1,
        int(len(df) * percentage),
    )

    return rng.choice(
        df.index,
        size=count,
        replace=False,
    )


# ============================================================
# SALES
# ============================================================

def inject_sales_issues():

    df = load("sales.csv")

    # Missing product references
    rows = choose_rows(df, 0.02)
    df.loc[rows, "product_id"] = np.nan

    # Negative quantities
    rows = choose_rows(df, 0.01)
    df.loc[rows, "quantity"] *= -1

    # Revenue mismatches
    rows = choose_rows(df, 0.02)
    df.loc[rows, "revenue"] = np.round(
        df.loc[rows, "revenue"] * 1.10,
        2,
    )

    # Duplicate records
    duplicates = df.sample(
        n=int(len(df) * 0.02),
        random_state=SEED,
    )

    df = pd.concat(
        [df, duplicates],
        ignore_index=True,
    )

    save(df, "sales.csv")

    print("sales.csv: issues injected")


# ============================================================
# PRODUCTION
# ============================================================

def inject_production_issues():

    df = load("production.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "produced_quantity"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "defect_quantity"] = (
        df.loc[rows, "produced_quantity"].abs()
        * 1.25
    ).astype(int)

    rows = choose_rows(df, 0.01)
    df.loc[rows, "employee_id"] = np.nan

    save(df, "production.csv")

    print("production.csv: issues injected")


# ============================================================
# MAINTENANCE
# ============================================================

def inject_maintenance_issues():

    df = load("maintenance.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "maintenance_cost"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "machine_id"] = np.nan

    save(df, "maintenance.csv")

    print("maintenance.csv: issues injected")


# ============================================================
# FINANCIAL
# ============================================================

def inject_financial_issues():

    df = load("financial_transactions.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "amount"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "category"] = np.nan

    save(df, "financial_transactions.csv")

    print(
        "financial_transactions.csv: "
        "issues injected"
    )


# ============================================================
# BUDGET
# ============================================================

def inject_budget_issues():

    df = load("budget.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "budget_amount"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "budget_category"] = np.nan

    save(df, "budget.csv")

    print("budget.csv: issues injected")


# ============================================================
# ENERGY
# ============================================================

def inject_energy_issues():

    df = load("energy.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "consumption"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "energy_type"] = np.nan

    save(df, "energy.csv")

    print("energy.csv: issues injected")


# ============================================================
# EMISSIONS
# ============================================================

def inject_emissions_issues():

    df = load("emissions.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "co2e_amount"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "emission_source"] = np.nan

    save(df, "emissions.csv")

    print("emissions.csv: issues injected")


# ============================================================
# WASTE
# ============================================================

def inject_waste_issues():

    df = load("waste.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "waste_quantity"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "waste_type"] = np.nan

    save(df, "waste.csv")

    print("waste.csv: issues injected")


# ============================================================
# INVENTORY
# ============================================================

def inject_inventory_issues():

    df = load("inventory.csv")

    rows = choose_rows(df, 0.01)
    df.loc[rows, "closing_quantity"] *= -1

    rows = choose_rows(df, 0.01)
    df.loc[rows, "product_id"] = np.nan

    save(df, "inventory.csv")

    print("inventory.csv: issues injected")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Quality Issue Injection")
    print("=" * 60)

    inject_sales_issues()
    inject_production_issues()
    inject_maintenance_issues()
    inject_financial_issues()
    inject_budget_issues()
    inject_energy_issues()
    inject_emissions_issues()
    inject_waste_issues()
    inject_inventory_issues()

    print("\nQuality issue injection complete.")


if __name__ == "__main__":
    main()
