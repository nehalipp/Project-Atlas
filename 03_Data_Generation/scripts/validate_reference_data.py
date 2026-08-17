"""
Project Atlas
Phase 3 — Reference Data Validation

Validates the clean reference datasets.

Run this BEFORE quality issue injection.
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


EXPECTED_COUNTS = {
    "accounts.csv": N_ACCOUNTS,
    "customers.csv": N_CUSTOMERS,
    "suppliers.csv": N_SUPPLIERS,
    "products.csv": N_PRODUCTS,
    "locations.csv": N_LOCATIONS,
    "employees.csv": N_EMPLOYEES,
    "machines.csv": N_MACHINES,
}


REQUIRED_COLUMNS = {
    "accounts.csv": [
        "account_id",
        "account_name",
        "account_type",
        "industry",
        "country",
        "status",
    ],
    "customers.csv": [
        "customer_id",
        "account_id",
        "customer_name",
        "customer_segment",
        "industry",
        "country",
        "status",
    ],
    "suppliers.csv": [
        "supplier_id",
        "supplier_name",
        "supplier_category",
        "country",
        "status",
    ],
    "products.csv": [
        "product_id",
        "supplier_id",
        "product_name",
        "category",
        "unit_cost",
        "unit_price",
        "status",
    ],
    "locations.csv": [
        "location_id",
        "location_name",
        "location_type",
        "city",
        "state_region",
        "country",
        "status",
    ],
    "employees.csv": [
        "employee_id",
        "location_id",
        "employee_name",
        "department",
        "role",
        "hire_date",
        "status",
    ],
    "machines.csv": [
        "machine_id",
        "location_id",
        "machine_name",
        "machine_type",
        "installation_date",
        "status",
    ],
}


KEYS = {
    "accounts.csv": "account_id",
    "customers.csv": "customer_id",
    "suppliers.csv": "supplier_id",
    "products.csv": "product_id",
    "locations.csv": "location_id",
    "employees.csv": "employee_id",
    "machines.csv": "machine_id",
}


def load(filename):

    return pd.read_csv(
        RAW_DATA_DIR / filename
    )


def main():

    print("=" * 60)
    print("Project Atlas — Reference Data Validation")
    print("Mode: CLEAN BASELINE")
    print("=" * 60)

    failed = False

    # --------------------------------------------------------
    # Record counts
    # --------------------------------------------------------

    print("\n1. Record count validation")

    data = {}

    for filename, expected in EXPECTED_COUNTS.items():

        df = load(filename)
        data[filename] = df

        actual = len(df)

        if actual == expected:
            print(
                f"PASS  {filename}: "
                f"expected {expected:,}, found {actual:,}"
            )
        else:
            print(
                f"FAIL  {filename}: "
                f"expected {expected:,}, found {actual:,}"
            )
            failed = True

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    print("\n2. Required column validation")

    for filename, columns in REQUIRED_COLUMNS.items():

        missing = [
            column
            for column in columns
            if column not in data[filename].columns
        ]

        if not missing:
            print(
                f"PASS  {filename}: "
                "all required columns present"
            )
        else:
            print(
                f"FAIL  {filename}: "
                f"missing {missing}"
            )
            failed = True

    # --------------------------------------------------------
    # Business keys
    # --------------------------------------------------------

    print("\n3. Business-key validation")

    for filename, key in KEYS.items():

        series = data[filename][key]

        if series.isna().any():
            print(
                f"FAIL  {filename}: "
                f"{key} contains nulls"
            )
            failed = True
        elif series.duplicated().any():
            print(
                f"FAIL  {filename}: "
                f"{key} contains duplicates"
            )
            failed = True
        else:
            print(
                f"PASS  {filename}: "
                f"{key} is complete and unique"
            )

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    print("\n4. Foreign-key validation")

    checks = [
        ("customers.csv", "account_id", "accounts.csv", "account_id"),
        ("products.csv", "supplier_id", "suppliers.csv", "supplier_id"),
        ("employees.csv", "location_id", "locations.csv", "location_id"),
        ("machines.csv", "location_id", "locations.csv", "location_id"),
    ]

    for child_file, child_key, parent_file, parent_key in checks:

        valid = data[child_file][child_key].isin(
            set(data[parent_file][parent_key])
        )

        name = (
            f"{child_file.replace('.csv', '').title()} "
            f"→ {parent_file.replace('.csv', '').title()}"
        )

        if valid.all():
            print(f"PASS  {name}")
        else:
            print(f"FAIL  {name}")
            failed = True

    # --------------------------------------------------------
    # Location coverage
    # --------------------------------------------------------

    print("\n5. Location coverage validation")

    locations = set(
        data["locations.csv"]["location_id"]
    )

    employee_locations = set(
        data["employees.csv"]["location_id"]
    )

    machine_locations = set(
        data["machines.csv"]["location_id"]
    )

    if locations.issubset(employee_locations):
        print(
            "PASS  Every location has at least one employee"
        )
    else:
        print(
            "FAIL  Some locations have no employees"
        )
        failed = True

    if locations.issubset(machine_locations):
        print(
            "PASS  Every location has at least one machine"
        )
    else:
        print(
            "FAIL  Some locations have no machines"
        )
        failed = True

    # --------------------------------------------------------
    # Product rules
    # --------------------------------------------------------

    print("\n6. Product business rules")

    products = data["products.csv"]

    checks = [
        (
            "Product unit costs are positive",
            (products["unit_cost"] > 0).all(),
        ),
        (
            "Product unit prices are positive",
            (products["unit_price"] > 0).all(),
        ),
        (
            "Product prices are not below cost",
            (
                products["unit_price"]
                >= products["unit_cost"]
            ).all(),
        ),
    ]

    for message, passed in checks:

        if passed:
            print(f"PASS  {message}")
        else:
            print(f"FAIL  {message}")
            failed = True

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    if failed:
        print("REFERENCE DATA VALIDATION FAILED")
        print("=" * 60)
        raise SystemExit(1)

    print("REFERENCE DATA VALIDATION PASSED")
    print("Clean reference datasets are ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()
