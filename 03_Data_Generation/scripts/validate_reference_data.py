"""
Project Atlas
Phase 3 — Reference Data Validation

Validates the seven reference/master datasets.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


EXPECTED_COUNTS = {
    "accounts.csv": 500,
    "customers.csv": 50_000,
    "suppliers.csv": 500,
    "products.csv": 5_000,
    "locations.csv": 50,
    "employees.csv": 1_000,
    "machines.csv": 500,
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


KEY_COLUMNS = {
    "accounts.csv": "account_id",
    "customers.csv": "customer_id",
    "suppliers.csv": "supplier_id",
    "products.csv": "product_id",
    "locations.csv": "location_id",
    "employees.csv": "employee_id",
    "machines.csv": "machine_id",
}


# ============================================================
# HELPERS
# ============================================================

def load(filename):

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return pd.read_csv(path)


def check(condition, message):

    if condition:
        print(f"PASS  {message}")
        return True

    print(f"FAIL  {message}")
    return False


# ============================================================
# VALIDATION
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Reference Data Validation")
    print("=" * 60)

    data = {
        filename: load(filename)
        for filename in EXPECTED_COUNTS
    }

    passed = True

    # --------------------------------------------------------
    # Record counts
    # --------------------------------------------------------

    print("\n1. Record count validation")

    for filename, expected in EXPECTED_COUNTS.items():

        actual = len(data[filename])

        passed &= check(
            actual == expected,
            f"{filename}: expected {expected:,}, found {actual:,}",
        )

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

        passed &= check(
            not missing,
            f"{filename}: "
            + (
                "all required columns present"
                if not missing
                else f"missing {missing}"
            ),
        )

    # --------------------------------------------------------
    # Business keys
    # --------------------------------------------------------

    print("\n3. Business-key validation")

    for filename, key in KEY_COLUMNS.items():

        df = data[filename]

        passed &= check(
            df[key].notna().all(),
            f"{filename}: {key} contains no nulls",
        )

        passed &= check(
            df[key].is_unique,
            f"{filename}: {key} contains no duplicates",
        )

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    print("\n4. Foreign-key validation")

    customers = data["customers.csv"]
    accounts = data["accounts.csv"]

    products = data["products.csv"]
    suppliers = data["suppliers.csv"]

    employees = data["employees.csv"]
    machines = data["machines.csv"]
    locations = data["locations.csv"]

    passed &= check(
        customers["account_id"].isin(
            accounts["account_id"]
        ).all(),
        "Customers → Accounts",
    )

    passed &= check(
        products["supplier_id"].isin(
            suppliers["supplier_id"]
        ).all(),
        "Products → Suppliers",
    )

    passed &= check(
        employees["location_id"].isin(
            locations["location_id"]
        ).all(),
        "Employees → Locations",
    )

    passed &= check(
        machines["location_id"].isin(
            locations["location_id"]
        ).all(),
        "Machines → Locations",
    )

    # --------------------------------------------------------
    # Employee coverage
    # --------------------------------------------------------

    print("\n5. Location coverage validation")

    employee_locations = set(
        employees["location_id"]
    )

    machine_locations = set(
        machines["location_id"]
    )

    location_ids = set(
        locations["location_id"]
    )

    passed &= check(
        location_ids.issubset(
            employee_locations
        ),
        "Every location has at least one employee",
    )

    passed &= check(
        location_ids.issubset(
            machine_locations
        ),
        "Every location has at least one machine",
    )

    # --------------------------------------------------------
    # Product pricing
    # --------------------------------------------------------

    print("\n6. Product business rules")

    passed &= check(
        (products["unit_cost"] > 0).all(),
        "Product unit costs are positive",
    )

    passed &= check(
        (products["unit_price"] > 0).all(),
        "Product unit prices are positive",
    )

    passed &= check(
        (
            products["unit_price"]
            >= products["unit_cost"]
        ).all(),
        "Product prices are not below cost",
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    if passed:
        print("REFERENCE DATA VALIDATION PASSED")
    else:
        print("REFERENCE DATA VALIDATION FAILED")

    print("=" * 60)

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
