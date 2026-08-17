"""
Project Atlas
Phase 3 — Reference Data Validation

Validates the seven reference datasets against the approved
Phase 2 data model.
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    N_ACCOUNTS,
    N_CUSTOMERS,
    N_EMPLOYEES,
    N_LOCATIONS,
    N_MACHINES,
    N_PRODUCTS,
    N_SUPPLIERS,
    RAW_DATA_DIR,
)


DATASETS = {
    "accounts": {
        "file": "accounts.csv",
        "key": "account_id",
        "count": N_ACCOUNTS,
        "columns": [
            "account_id",
            "account_name",
            "account_type",
            "industry",
            "country",
            "status",
        ],
    },
    "customers": {
        "file": "customers.csv",
        "key": "customer_id",
        "count": N_CUSTOMERS,
        "columns": [
            "customer_id",
            "account_id",
            "customer_name",
            "customer_segment",
            "industry",
            "country",
            "status",
        ],
    },
    "suppliers": {
        "file": "suppliers.csv",
        "key": "supplier_id",
        "count": N_SUPPLIERS,
        "columns": [
            "supplier_id",
            "supplier_name",
            "supplier_category",
            "country",
            "status",
        ],
    },
    "products": {
        "file": "products.csv",
        "key": "product_id",
        "count": N_PRODUCTS,
        "columns": [
            "product_id",
            "supplier_id",
            "product_name",
            "category",
            "unit_cost",
            "unit_price",
            "status",
        ],
    },
    "locations": {
        "file": "locations.csv",
        "key": "location_id",
        "count": N_LOCATIONS,
        "columns": [
            "location_id",
            "location_name",
            "location_type",
            "city",
            "state_region",
            "country",
            "status",
        ],
    },
    "employees": {
        "file": "employees.csv",
        "key": "employee_id",
        "count": N_EMPLOYEES,
        "columns": [
            "employee_id",
            "location_id",
            "employee_name",
            "department",
            "role",
            "hire_date",
            "status",
        ],
    },
    "machines": {
        "file": "machines.csv",
        "key": "machine_id",
        "count": N_MACHINES,
        "columns": [
            "machine_id",
            "location_id",
            "machine_name",
            "machine_type",
            "installation_date",
            "status",
        ],
    },
}


# ============================================================
# HELPERS
# ============================================================

def load_dataset(name):

    path = RAW_DATA_DIR / DATASETS[name]["file"]

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset: {path}"
        )

    return pd.read_csv(path)


def validate_columns(name, df):

    expected = DATASETS[name]["columns"]

    missing = [
        column
        for column in expected
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


def validate_reference_relationship(
    child,
    child_column,
    parent,
    parent_column,
    relationship,
):

    valid_values = set(
        parent[parent_column]
    )

    invalid = ~child[child_column].isin(
        valid_values
    )

    if invalid.any():
        raise ValueError(
            f"{relationship}: "
            f"{invalid.sum():,} invalid references."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Reference Data Validation")
    print("=" * 70)

    print("\nValidating reference datasets...")

    datasets = {}

    for name in DATASETS:

        df = load_dataset(name)

        validate_columns(
            name,
            df,
        )

        validate_basic(
            name,
            df,
        )

        datasets[name] = df

        print(
            f"      ✓ {DATASETS[name]['file']:<28}"
            f"{len(df):>10,} records"
        )

    print("\nRunning relationship checks...")

    validate_reference_relationship(
        datasets["customers"],
        "account_id",
        datasets["accounts"],
        "account_id",
        "Customer → Account",
    )

    print("      ✓ Customer → Account")

    validate_reference_relationship(
        datasets["products"],
        "supplier_id",
        datasets["suppliers"],
        "supplier_id",
        "Product → Supplier",
    )

    print("      ✓ Product → Supplier")

    validate_reference_relationship(
        datasets["employees"],
        "location_id",
        datasets["locations"],
        "location_id",
        "Employee → Location",
    )

    print("      ✓ Employee → Location")

    validate_reference_relationship(
        datasets["machines"],
        "location_id",
        datasets["locations"],
        "location_id",
        "Machine → Location",
    )

    print("      ✓ Machine → Location")

    print("\nRunning business-rule checks...")

    products = datasets["products"]

    if (products["unit_cost"] <= 0).any():
        raise ValueError(
            "Products contain non-positive unit costs."
        )

    if (products["unit_price"] <= 0).any():
        raise ValueError(
            "Products contain non-positive unit prices."
        )

    if (
        products["unit_price"]
        < products["unit_cost"]
    ).any():
        raise ValueError(
            "Products contain prices below unit cost."
        )

    print("      ✓ Product pricing")

    employees = datasets["employees"].copy()
    machines = datasets["machines"].copy()

    employees["hire_date"] = pd.to_datetime(
        employees["hire_date"],
        errors="coerce",
    )

    machines["installation_date"] = pd.to_datetime(
        machines["installation_date"],
        errors="coerce",
    )

    if employees["hire_date"].isna().any():
        raise ValueError(
            "Employees contain invalid hire dates."
        )

    if machines["installation_date"].isna().any():
        raise ValueError(
            "Machines contain invalid installation dates."
        )

    print("      ✓ Lifecycle dates")

    total_records = sum(
        len(df)
        for df in datasets.values()
    )

    print("\n" + "-" * 70)
    print("VALIDATION SUMMARY")
    print("-" * 70)
    print(f"Datasets validated                  : 7")
    print(f"Records validated                   : {total_records:,.0f}")
    print(f"Validation status                   : PASSED")
    print(f"Output                              : {RAW_DATA_DIR}")

    print("\n" + "=" * 70)
    print("REFERENCE DATA VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()