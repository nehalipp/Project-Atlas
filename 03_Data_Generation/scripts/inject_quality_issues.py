"""
Project Atlas
Phase 3 — Controlled Data Quality Issue Injection

Adds deliberate, reproducible quality issues to the
clean business datasets.

This script must be run AFTER clean validation passes.
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
    INVALID_VALUE_RATE,
    MISSING_RATE,
    RAW_DATA_DIR,
    SEED,
)


rng = np.random.default_rng(SEED)


# ============================================================
# HELPERS
# ============================================================

def load(filename):

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return pd.read_csv(path)


def save(df, filename):

    df.to_csv(
        RAW_DATA_DIR / filename,
        index=False,
    )


def choose_rows(df, rate):

    count = max(
        1,
        int(len(df) * rate),
    )

    return rng.choice(
        df.index.to_numpy(),
        count,
        replace=False,
    )


def percentage_count(df, rate):

    return max(
        1,
        int(len(df) * rate),
    )


# ============================================================
# SALES
# ============================================================

def inject_sales():

    df = load("sales.csv")

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    revenue_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    duplicate_count = percentage_count(
        df,
        DUPLICATE_RATE,
    )

    df.loc[
        missing_rows,
        "product_id",
    ] = np.nan

    df.loc[
        negative_rows,
        "quantity",
    ] *= -1

    df.loc[
        revenue_rows,
        "revenue",
    ] = np.round(
        df.loc[
            revenue_rows,
            "revenue",
        ] * 1.10,
        2,
    )

    duplicates = df.sample(
        n=duplicate_count,
        random_state=SEED,
    )

    df = pd.concat(
        [df, duplicates],
        ignore_index=True,
    )

    save(df, "sales.csv")

    print(
        f"sales.csv: "
        f"{len(missing_rows):,} missing product IDs, "
        f"{len(negative_rows):,} negative quantities, "
        f"{len(revenue_rows):,} revenue mismatches, "
        f"{duplicate_count:,} duplicate rows"
    )


# ============================================================
# PRODUCTION
# ============================================================

def inject_production():

    df = load("production.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    defect_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "produced_quantity",
    ] *= -1

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

    df.loc[
        missing_rows,
        "employee_id",
    ] = np.nan

    save(df, "production.csv")

    print(
        f"production.csv: "
        f"{len(negative_rows):,} negative quantities, "
        f"{len(defect_rows):,} excessive defects, "
        f"{len(missing_rows):,} missing employees"
    )


# ============================================================
# MAINTENANCE
# ============================================================

def inject_maintenance():

    df = load("maintenance.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "maintenance_cost",
    ] *= -1

    df.loc[
        missing_rows,
        "machine_id",
    ] = np.nan

    save(df, "maintenance.csv")

    print(
        f"maintenance.csv: "
        f"{len(negative_rows):,} negative costs, "
        f"{len(missing_rows):,} missing machines"
    )


# ============================================================
# FINANCIAL TRANSACTIONS
# ============================================================

def inject_financial():

    df = load(
        "financial_transactions.csv"
    )

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "amount",
    ] *= -1

    df.loc[
        missing_rows,
        "category",
    ] = np.nan

    save(
        df,
        "financial_transactions.csv",
    )

    print(
        f"financial_transactions.csv: "
        f"{len(negative_rows):,} negative amounts, "
        f"{len(missing_rows):,} missing categories"
    )


# ============================================================
# BUDGET
# ============================================================

def inject_budget():

    df = load("budget.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "budget_amount",
    ] *= -1

    df.loc[
        missing_rows,
        "budget_category",
    ] = np.nan

    save(df, "budget.csv")

    print(
        f"budget.csv: "
        f"{len(negative_rows):,} negative budgets, "
        f"{len(missing_rows):,} missing categories"
    )


# ============================================================
# ENERGY
# ============================================================

def inject_energy():

    df = load("energy.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "consumption",
    ] *= -1

    df.loc[
        missing_rows,
        "energy_type",
    ] = np.nan

    save(df, "energy.csv")

    print(
        f"energy.csv: "
        f"{len(negative_rows):,} negative consumption values, "
        f"{len(missing_rows):,} missing energy types"
    )


# ============================================================
# EMISSIONS
# ============================================================

def inject_emissions():

    df = load("emissions.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "co2e_amount",
    ] *= -1

    df.loc[
        missing_rows,
        "emission_source",
    ] = np.nan

    save(df, "emissions.csv")

    print(
        f"emissions.csv: "
        f"{len(negative_rows):,} negative CO2e values, "
        f"{len(missing_rows):,} missing sources"
    )


# ============================================================
# WASTE
# ============================================================

def inject_waste():

    df = load("waste.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "waste_quantity",
    ] *= -1

    df.loc[
        missing_rows,
        "waste_type",
    ] = np.nan

    save(df, "waste.csv")

    print(
        f"waste.csv: "
        f"{len(negative_rows):,} negative quantities, "
        f"{len(missing_rows):,} missing waste types"
    )


# ============================================================
# INVENTORY
# ============================================================

def inject_inventory():

    df = load("inventory.csv")

    negative_rows = choose_rows(
        df,
        INVALID_VALUE_RATE,
    )

    missing_rows = choose_rows(
        df,
        MISSING_RATE,
    )

    df.loc[
        negative_rows,
        "closing_quantity",
    ] *= -1

    df.loc[
        missing_rows,
        "product_id",
    ] = np.nan

    save(df, "inventory.csv")

    print(
        f"inventory.csv: "
        f"{len(negative_rows):,} negative closing quantities, "
        f"{len(missing_rows):,} missing products"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Quality Issue Injection")
    print("=" * 60)

    print("\nInjecting controlled defects...\n")

    inject_sales()
    inject_production()
    inject_maintenance()
    inject_financial()
    inject_budget()
    inject_energy()
    inject_emissions()
    inject_waste()
    inject_inventory()

    print("\n" + "=" * 60)
    print("CONTROLLED QUALITY INJECTION COMPLETE")
    print("=" * 60)

    print("\nNext step:")
    print("Run Phase 4 Data Quality profiling and validation.")


if __name__ == "__main__":
    main()
