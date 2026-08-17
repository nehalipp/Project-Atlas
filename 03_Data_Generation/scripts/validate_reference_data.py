"""
Project Atlas
Phase 3 — Reference Data Validation

Validates the seven reference/master datasets:

    accounts
    customers
    suppliers
    products
    locations
    employees
    machines

Expected record counts come directly from generation_config.py.
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_GENERATION_DIR = SCRIPT_DIR.parent
CONFIG_DIR = DATA_GENERATION_DIR / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    N_ACCOUNTS,
    N_CUSTOMERS,
    N_SUPPLIERS,
    N_PRODUCTS,
    N_LOCATIONS,
    N_EMPLOYEES,
    N_MACHINES,
    RAW_DATA_DIR,
)


# ============================================================
# EXPECTED RECORD COUNTS
# ============================================================

EXPECTED_COUNTS = {
    "accounts.csv": N_ACCOUNTS,
    "customers.csv": N_CUSTOMERS,
    "suppliers.csv": N_SUPPLIERS,
    "products.csv": N_PRODUCTS,
    "locations.csv": N_LOCATIONS,
    "employees.csv": N_EMPLOYEES,
    "machines.csv": N_MACHINES,
}


# ============================================================
# REQUIRED COLUMNS
# ============================================================

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


# ============================================================
# LOAD DATA
# ============================================================

def load_data(filename):
    """Load one reference dataset."""

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# VALIDATION HELPERS
# ============================================================

def check_record_count(filename, df):
    """Check that the record count matches configuration."""

    expected = EXPECTED_COUNTS[filename]
    actual = len(df)

    if actual == expected:
        print(
            f"PASS  {filename}: "
            f"expected {expected:,}, found {actual:,}"
        )
        return True

    print(
        f"FAIL  {filename}: "
        f"expected {expected:,}, found {actual:,}"
    )
    return False


def check_required_columns(filename, df):
    """Check that all required columns exist."""

    missing = [
        column
        for column in REQUIRED_COLUMNS[filename]
        if column not in df.columns
    ]

    if not missing:
        print(
            f"PASS  {filename}: "
            "all required columns present"
        )
        return True

    print(
        f"FAIL  {filename}: "
        f"missing columns {missing}"
    )
    return False


def check_business_key(filename, df, key):
    """Check that the business key is complete and unique."""

    if df[key].isna().any():
        print(
            f"FAIL  {filename}: "
            f"{key} contains nulls"
        )
        return False

    if df[key].duplicated().any():
        print(
            f"FAIL  {filename}: "
            f"{key} contains duplicates"
        )
        return False

    print(
        f"PASS  {filename}: "
        f"{key} contains no nulls or duplicates"
    )
    return True


def check_foreign_key(
    child_name,
    child_df,
    child_column,
    parent_name,
    parent_df,
    parent_column,
):
    """Check that child keys exist in the parent dataset."""

    valid_keys = set(
        parent_df[parent_column].dropna()
    )

    invalid = (
        child_df[child_column].notna()
        & ~child_df[child_column].isin(valid_keys)
    )

    if not invalid.any():
        print(
            f"PASS  {child_name} → {parent_name}"
        )
        return True

    print(
        f"FAIL  {child_name} → {parent_name}: "
        f"{invalid.sum():,} invalid references"
    )
    return False


# ============================================================
# LOCATION COVERAGE
# ============================================================

def check_location_coverage(
    locations,
    employees,
    machines,
):
    """Ensure every location has employees and machines."""

    employee_locations = set(
        employees["location_id"]
    )

    machine_locations = set(
        machines["location_id"]
    )

    location_ids = set(
        locations["location_id"]
    )

    missing_employees = (
        location_ids - employee_locations
    )

    missing_machines = (
        location_ids - machine_locations
    )

    passed = True

    if not missing_employees:
        print(
            "PASS  Every location has at least one employee"
        )
    else:
        print(
            "FAIL  Locations without employees: "
            f"{sorted(missing_employees)}"
        )
        passed = False

    if not missing_machines:
        print(
            "PASS  Every location has at least one machine"
        )
    else:
        print(
            "FAIL  Locations without machines: "
            f"{sorted(missing_machines)}"
        )
        passed = False

    return passed


# ============================================================
# PRODUCT BUSINESS RULES
# ============================================================

def check_product_rules(products):
    """Validate basic product pricing rules."""

    passed = True

    if (products["unit_cost"] > 0).all():
        print(
            "PASS  Product unit costs are positive"
        )
    else:
        print(
            "FAIL  Product unit costs must be positive"
        )
        passed = False

    if (products["unit_price"] > 0).all():
        print(
            "PASS  Product unit prices are positive"
        )
    else:
        print(
            "FAIL  Product unit prices must be positive"
        )
        passed = False

    if (
        products["unit_price"]
        >= products["unit_cost"]
    ).all():
        print(
            "PASS  Product prices are not below cost"
        )
    else:
        print(
            "FAIL  Product prices are below cost"
        )
        passed = False

    return passed


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Reference Data Validation")
    print("=" * 60)

    all_passed = True

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    data = {
        filename: load_data(filename)
        for filename in EXPECTED_COUNTS
    }

    accounts = data["accounts.csv"]
    customers = data["customers.csv"]
    suppliers = data["suppliers.csv"]
    products = data["products.csv"]
    locations = data["locations.csv"]
    employees = data["employees.csv"]
    machines = data["machines.csv"]

    # --------------------------------------------------------
    # 1. Record counts
    # --------------------------------------------------------

    print("\n1. Record count validation")

    for filename, df in data.items():
        all_passed &= check_record_count(
            filename,
            df,
        )

    # --------------------------------------------------------
    # 2. Required columns
    # --------------------------------------------------------

    print("\n2. Required column validation")

    for filename, df in data.items():
        all_passed &= check_required_columns(
            filename,
            df,
        )

    # --------------------------------------------------------
    # 3. Business keys
    # --------------------------------------------------------

    print("\n3. Business-key validation")

    business_keys = {
        "accounts.csv": "account_id",
        "customers.csv": "customer_id",
        "suppliers.csv": "supplier_id",
        "products.csv": "product_id",
        "locations.csv": "location_id",
        "employees.csv": "employee_id",
        "machines.csv": "machine_id",
    }

    for filename, key in business_keys.items():
        all_passed &= check_business_key(
            filename,
            data[filename],
            key,
        )

    # --------------------------------------------------------
    # 4. Foreign keys
    # --------------------------------------------------------

    print("\n4. Foreign-key validation")

    all_passed &= check_foreign_key(
        "Customers",
        customers,
        "account_id",
        "Accounts",
        accounts,
        "account_id",
    )

    all_passed &= check_foreign_key(
        "Products",
        products,
        "supplier_id",
        "Suppliers",
        suppliers,
        "supplier_id",
    )

    all_passed &= check_foreign_key(
        "Employees",
        employees,
        "location_id",
        "Locations",
        locations,
        "location_id",
    )

    all_passed &= check_foreign_key(
        "Machines",
        machines,
        "location_id",
        "Locations",
        locations,
        "location_id",
    )

    # --------------------------------------------------------
    # 5. Location coverage
    # --------------------------------------------------------

    print("\n5. Location coverage validation")

    all_passed &= check_location_coverage(
        locations,
        employees,
        machines,
    )

    # --------------------------------------------------------
    # 6. Product business rules
    # --------------------------------------------------------

    print("\n6. Product business rules")

    all_passed &= check_product_rules(
        products
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    if all_passed:
        print("REFERENCE DATA VALIDATION PASSED")
        print(
            "All seven reference datasets are valid."
        )
    else:
        print("REFERENCE DATA VALIDATION FAILED")
        print(
            "Review the failed checks above."
        )

    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()

    raise SystemExit(
        0 if success else 1
    )
