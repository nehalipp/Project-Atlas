"""
Project Atlas
Phase 3 — Business Data Validation

Validates the nine approved business datasets against the
Phase 2 fact grains, relationships and business rules.
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
    END_DATE,
    N_BUDGET,
    N_EMISSIONS,
    N_ENERGY,
    N_FINANCIAL_TRANSACTIONS,
    N_INVENTORY,
    N_MAINTENANCE,
    N_PRODUCTION,
    N_SALES,
    N_WASTE,
    RAW_DATA_DIR,
    START_DATE,
)


START = pd.Timestamp(START_DATE)
END = pd.Timestamp(END_DATE)


DATASETS = {
    "sales": {
        "file": "sales.csv",
        "key": "sales_id",
        "count": N_SALES,
        "columns": [
            "sales_id",
            "date",
            "account_id",
            "customer_id",
            "product_id",
            "location_id",
            "quantity",
            "unit_price",
            "discount_rate",
            "revenue",
        ],
    },
    "production": {
        "file": "production.csv",
        "key": "production_id",
        "count": N_PRODUCTION,
        "columns": [
            "production_id",
            "date",
            "product_id",
            "location_id",
            "machine_id",
            "employee_id",
            "planned_quantity",
            "quantity_produced",
            "production_hours",
            "production_status",
        ],
    },
    "maintenance": {
        "file": "maintenance.csv",
        "key": "maintenance_id",
        "count": N_MAINTENANCE,
        "columns": [
            "maintenance_id",
            "date",
            "location_id",
            "machine_id",
            "employee_id",
            "maintenance_type",
            "downtime_hours",
            "maintenance_cost",
        ],
    },
    "financial_transactions": {
        "file": "financial_transactions.csv",
        "key": "financial_transaction_id",
        "count": N_FINANCIAL_TRANSACTIONS,
        "columns": [
            "financial_transaction_id",
            "date",
            "location_id",
            "transaction_type",
            "amount",
            "description",
        ],
    },
    "budget": {
        "file": "budget.csv",
        "key": "budget_id",
        "count": N_BUDGET,
        "columns": [
            "budget_id",
            "date",
            "location_id",
            "category",
            "budget_amount",
        ],
    },
    "energy": {
        "file": "energy.csv",
        "key": "energy_id",
        "count": N_ENERGY,
        "columns": [
            "energy_id",
            "date",
            "location_id",
            "energy_type",
            "consumption",
            "unit",
        ],
    },
    "emissions": {
        "file": "emissions.csv",
        "key": "emissions_id",
        "count": N_EMISSIONS,
        "columns": [
            "emissions_id",
            "date",
            "location_id",
            "source",
            "co2_kg",
        ],
    },
    "waste": {
        "file": "waste.csv",
        "key": "waste_id",
        "count": N_WASTE,
        "columns": [
            "waste_id",
            "date",
            "location_id",
            "waste_type",
            "quantity",
            "unit",
            "disposal_method",
        ],
    },
    "inventory": {
        "file": "inventory.csv",
        "key": "inventory_id",
        "count": N_INVENTORY,
        "columns": [
            "inventory_id",
            "date",
            "product_id",
            "location_id",
            "quantity_on_hand",
            "reorder_point",
            "inventory_value",
        ],
    },
}


REFERENCE_FILES = {
    "accounts": "accounts.csv",
    "customers": "customers.csv",
    "products": "products.csv",
    "locations": "locations.csv",
    "employees": "employees.csv",
    "machines": "machines.csv",
}


# ============================================================
# HELPERS
# ============================================================

def load_csv(filename):

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset: {path}"
        )

    return pd.read_csv(path)


def validate_columns(name, df):

    missing = [
        column
        for column in DATASETS[name]["columns"]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{name}: missing columns: {missing}"
        )


def validate_basic(name, df):

    definition = DATASETS[name]

    if len(df) != definition["count"]:
        raise ValueError(
            f"{name}: expected "
            f"{definition['count']:,} rows, "
            f"found {len(df):,}."
        )

    if df.isna().any().any():
        raise ValueError(
            f"{name}: unexpected null values."
        )

    if df[definition["key"]].duplicated().any():
        raise ValueError(
            f"{name}: primary key is not unique."
        )


def validate_ids(
    df,
    column,
    reference,
    reference_column,
    relationship,
):

    invalid = ~df[column].isin(
        set(reference[reference_column])
    )

    if invalid.any():
        raise ValueError(
            f"{relationship}: "
            f"{invalid.sum():,} invalid references."
        )


def validate_dates(name, df):

    dates = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    if dates.isna().any():
        raise ValueError(
            f"{name}: invalid dates detected."
        )

    if (dates < START).any() or (dates > END).any():
        raise ValueError(
            f"{name}: dates outside Atlas period."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Business Data Validation")
    print("=" * 70)

    print("\nLoading reference datasets...")

    references = {
        name: load_csv(filename)
        for name, filename in REFERENCE_FILES.items()
    }

    for name in REFERENCE_FILES:
        print(
            f"      ✓ {name}.csv"
        )

    print("\nValidating business datasets...")

    datasets = {}

    for name, definition in DATASETS.items():

        df = load_csv(
            definition["file"]
        )

        validate_columns(
            name,
            df,
        )

        validate_basic(
            name,
            df,
        )

        validate_dates(
            name,
            df,
        )

        datasets[name] = df

        print(
            f"      ✓ {definition['file']:<32}"
            f"{len(df):>10,} records"
        )

    print("\nRunning referential-integrity checks...")

    sales = datasets["sales"]

    validate_ids(
        sales,
        "account_id",
        references["accounts"],
        "account_id",
        "Sales → Account",
    )

    validate_ids(
        sales,
        "customer_id",
        references["customers"],
        "customer_id",
        "Sales → Customer",
    )

    validate_ids(
        sales,
        "product_id",
        references["products"],
        "product_id",
        "Sales → Product",
    )

    validate_ids(
        sales,
        "location_id",
        references["locations"],
        "location_id",
        "Sales → Location",
    )

    print("      ✓ Sales → Account")
    print("      ✓ Sales → Customer")
    print("      ✓ Sales → Product")
    print("      ✓ Sales → Location")

    production = datasets["production"]

    for column, reference, relationship in [
        (
            "product_id",
            references["products"],
            "Production → Product",
        ),
        (
            "location_id",
            references["locations"],
            "Production → Location",
        ),
        (
            "machine_id",
            references["machines"],
            "Production → Machine",
        ),
        (
            "employee_id",
            references["employees"],
            "Production → Employee",
        ),
    ]:
        validate_ids(
            production,
            column,
            reference,
            column,
            relationship,
        )

    print("      ✓ Production references")

    maintenance = datasets["maintenance"]

    for column, reference, relationship in [
        (
            "location_id",
            references["locations"],
            "Maintenance → Location",
        ),
        (
            "machine_id",
            references["machines"],
            "Maintenance → Machine",
        ),
        (
            "employee_id",
            references["employees"],
            "Maintenance → Employee",
        ),
    ]:
        validate_ids(
            maintenance,
            column,
            reference,
            column,
            relationship,
        )

    print("      ✓ Maintenance references")

    for name in [
        "financial_transactions",
        "budget",
        "energy",
        "emissions",
        "waste",
    ]:
        validate_ids(
            datasets[name],
            "location_id",
            references["locations"],
            "location_id",
            f"{name} → Location",
        )

    print("      ✓ Location references")

    inventory = datasets["inventory"]

    validate_ids(
        inventory,
        "product_id",
        references["products"],
        "product_id",
        "Inventory → Product",
    )

    validate_ids(
        inventory,
        "location_id",
        references["locations"],
        "location_id",
        "Inventory → Location",
    )

    print("      ✓ Inventory → Product")
    print("      ✓ Inventory → Location")

    print("\nRunning business-rule checks...")

    customer_accounts = (
        references["customers"]
        .set_index("customer_id")["account_id"]
    )

    if not (
        sales["account_id"]
        == sales["customer_id"].map(
            customer_accounts
        )
    ).all():
        raise ValueError(
            "Sales account does not match customer account."
        )

    print("      ✓ Sales customer/account consistency")

    if (sales["quantity"] <= 0).any():
        raise ValueError(
            "Sales contain non-positive quantities."
        )

    if (sales["unit_price"] <= 0).any():
        raise ValueError(
            "Sales contain non-positive prices."
        )

    if (
        (sales["discount_rate"] < 0)
        | (sales["discount_rate"] > 1)
    ).any():
        raise ValueError(
            "Sales contain invalid discount rates."
        )

    expected_revenue = np.round(
        sales["quantity"]
        * sales["unit_price"]
        * (1 - sales["discount_rate"]),
        2,
    )

    if not np.allclose(
        sales["revenue"],
        expected_revenue,
        atol=0.01,
    ):
        raise ValueError(
            "Sales revenue reconciliation failed."
        )

    print("      ✓ Sales revenue calculation")

    machines = references["machines"]
    employees = references["employees"]

    machine_locations = (
        machines
        .set_index("machine_id")["location_id"]
    )

    employee_locations = (
        employees
        .set_index("employee_id")["location_id"]
    )

    if not (
        production["location_id"]
        == production["machine_id"].map(
            machine_locations
        )
    ).all():
        raise ValueError(
            "Production location does not match machine location."
        )

    if not (
        production["location_id"]
        == production["employee_id"].map(
            employee_locations
        )
    ).all():
        raise ValueError(
            "Production location does not match employee location."
        )

    print("      ✓ Production machine/location consistency")
    print("      ✓ Production employee/location consistency")

    if not (
        maintenance["location_id"]
        == maintenance["machine_id"].map(
            machine_locations
        )
    ).all():
        raise ValueError(
            "Maintenance location does not match machine."
        )

    if not (
        maintenance["location_id"]
        == maintenance["employee_id"].map(
            employee_locations
        )
    ).all():
        raise ValueError(
            "Maintenance location does not match employee."
        )

    print("      ✓ Maintenance machine/location consistency")
    print("      ✓ Maintenance employee/location consistency")

    if inventory.duplicated(
        subset=[
            "date",
            "product_id",
            "location_id",
        ]
    ).any():
        raise ValueError(
            "Inventory grain violation detected."
        )

    print(
        "      ✓ Inventory Date + Product + Location grain"
    )

    total_records = sum(
        len(df)
        for df in datasets.values()
    )

    print("\n" + "-" * 70)
    print("VALIDATION SUMMARY")
    print("-" * 70)
    print(f"Datasets validated                  : 9")
    print(f"Records validated                   : {total_records:,.0f}")
    print(f"Validation status                   : PASSED")
    print(f"Output                              : {RAW_DATA_DIR}")

    print("\n" + "=" * 70)
    print("BUSINESS DATA VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()