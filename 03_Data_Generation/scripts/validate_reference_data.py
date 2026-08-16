"""
Project Atlas
Phase 3 — Reference Data Validation

Lightweight validation of the seven generated reference datasets.

This script verifies:
- Expected record counts
- Primary business-key uniqueness
- Required fields
- Referential integrity
- Customer/account country consistency
- Geographic consistency for operational locations

This is a generation sanity check, not the full Phase 4
Data Quality implementation.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# Expected Dataset Counts
# ============================================================

EXPECTED_COUNTS = {
    "accounts.csv": 1_000,
    "customers.csv": 50_000,
    "suppliers.csv": 1_000,
    "products.csv": 5_000,
    "locations.csv": 100,
    "employees.csv": 5_000,
    "machines.csv": 2_000,
}


# ============================================================
# Primary Business Keys
# ============================================================

PRIMARY_KEYS = {
    "accounts.csv": "account_id",
    "customers.csv": "customer_id",
    "suppliers.csv": "supplier_id",
    "products.csv": "product_id",
    "locations.csv": "location_id",
    "employees.csv": "employee_id",
    "machines.csv": "machine_id",
}


# ============================================================
# Required Fields
# ============================================================

REQUIRED_FIELDS = {
    "accounts.csv": [
        "account_id",
        "account_name",
        "country",
    ],
    "customers.csv": [
        "customer_id",
        "account_id",
        "customer_name",
        "country",
    ],
    "suppliers.csv": [
        "supplier_id",
        "supplier_name",
        "country",
    ],
    "products.csv": [
        "product_id",
        "supplier_id",
        "product_name",
        "category",
        "unit_cost",
        "unit_price",
    ],
    "locations.csv": [
        "location_id",
        "location_name",
        "city",
        "state_region",
        "country",
    ],
    "employees.csv": [
        "employee_id",
        "location_id",
        "employee_name",
    ],
    "machines.csv": [
        "machine_id",
        "location_id",
        "machine_name",
    ],
}


# ============================================================
# Geographic Reference Values
# ============================================================

VALID_LOCATION_PAIRS = {
    ("Pittsburgh", "Pennsylvania", "United States"),
    ("Philadelphia", "Pennsylvania", "United States"),
    ("Allentown", "Pennsylvania", "United States"),
    ("Columbus", "Ohio", "United States"),
    ("Cleveland", "Ohio", "United States"),
    ("Detroit", "Michigan", "United States"),
    ("Chicago", "Illinois", "United States"),
    ("Indianapolis", "Indiana", "United States"),
    ("New York", "New York", "United States"),
    ("Newark", "New Jersey", "United States"),
    ("Charlotte", "North Carolina", "United States"),
    ("Atlanta", "Georgia", "United States"),
    ("Dallas", "Texas", "United States"),
    ("Houston", "Texas", "United States"),
    ("Stockholm", "Stockholm County", "Sweden"),
    ("Gothenburg", "Västra Götaland County", "Sweden"),
    ("Malmö", "Skåne County", "Sweden"),
    ("Linköping", "Östergötland County", "Sweden"),
    ("Jönköping", "Jönköping County", "Sweden"),
    ("Västerås", "Västmanland County", "Sweden"),
    ("Örebro", "Örebro County", "Sweden"),
    ("Helsingborg", "Skåne County", "Sweden"),
}


# ============================================================
# Utility Functions
# ============================================================

def load_dataset(filename: str) -> pd.DataFrame:
    """Load a generated CSV file."""

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset: {path}"
        )

    return pd.read_csv(path)


def check(condition: bool, message: str) -> None:
    """Print validation result and stop on failure."""

    if condition:
        print(f"PASS  {message}")
    else:
        print(f"FAIL  {message}")
        raise AssertionError(message)


# ============================================================
# Main Validation
# ============================================================

def main() -> None:

    print("=" * 60)
    print("Project Atlas — Reference Data Validation")
    print("=" * 60)

    datasets = {}

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    print("\n1. Loading datasets")

    for filename in EXPECTED_COUNTS:
        datasets[filename] = load_dataset(filename)

        print(
            f"Loaded {filename}: "
            f"{len(datasets[filename]):,} records"
        )

    # --------------------------------------------------------
    # Record Counts
    # --------------------------------------------------------

    print("\n2. Record count validation")

    for filename, expected_count in EXPECTED_COUNTS.items():

        actual_count = len(datasets[filename])

        check(
            actual_count == expected_count,
            (
                f"{filename}: "
                f"expected {expected_count:,}, "
                f"found {actual_count:,}"
            ),
        )

    # --------------------------------------------------------
    # Required Columns
    # --------------------------------------------------------

    print("\n3. Required column validation")

    for filename, required_columns in REQUIRED_FIELDS.items():

        df = datasets[filename]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        check(
            not missing_columns,
            (
                f"{filename}: all required columns present"
                if not missing_columns
                else
                f"{filename}: missing columns "
                f"{missing_columns}"
            ),
        )

    # --------------------------------------------------------
    # Business-Key Uniqueness
    # --------------------------------------------------------

    print("\n4. Business-key uniqueness")

    for filename, key_column in PRIMARY_KEYS.items():

        df = datasets[filename]

        duplicate_count = (
            df[key_column]
            .duplicated()
            .sum()
        )

        null_count = (
            df[key_column]
            .isna()
            .sum()
        )

        check(
            null_count == 0,
            f"{filename}: {key_column} contains no nulls",
        )

        check(
            duplicate_count == 0,
            (
                f"{filename}: {key_column} "
                f"contains no duplicates"
            ),
        )

    # --------------------------------------------------------
    # Required-Field Null Checks
    # --------------------------------------------------------

    print("\n5. Required-field null validation")

    for filename, required_columns in REQUIRED_FIELDS.items():

        df = datasets[filename]

        for column in required_columns:

            null_count = df[column].isna().sum()

            check(
                null_count == 0,
                (
                    f"{filename}: {column} "
                    f"contains no nulls"
                ),
            )

    # --------------------------------------------------------
    # Customer → Account
    # --------------------------------------------------------

    print("\n6. Customer → Account relationship")

    accounts = datasets["accounts.csv"]
    customers = datasets["customers.csv"]

    valid_accounts = set(
        accounts["account_id"]
    )

    invalid_customer_accounts = (
        ~customers["account_id"].isin(
            valid_accounts
        )
    ).sum()

    check(
        invalid_customer_accounts == 0,
        (
            "Every customer references "
            "a valid account"
        ),
    )

    # Customer country must match Account country.

    account_country = (
        accounts
        .set_index("account_id")["country"]
    )

    customer_account_country = (
        customers["account_id"]
        .map(account_country)
    )

    country_mismatches = (
        customers["country"]
        != customer_account_country
    ).sum()

    check(
        country_mismatches == 0,
        (
            "Customer country matches "
            "associated account country"
        ),
    )

    # --------------------------------------------------------
    # Product → Supplier
    # --------------------------------------------------------

    print("\n7. Product → Supplier relationship")

    suppliers = datasets["suppliers.csv"]
    products = datasets["products.csv"]

    valid_suppliers = set(
        suppliers["supplier_id"]
    )

    invalid_product_suppliers = (
        ~products["supplier_id"].isin(
            valid_suppliers
        )
    ).sum()

    check(
        invalid_product_suppliers == 0,
        (
            "Every product references "
            "a valid supplier"
        ),
    )

    # --------------------------------------------------------
    # Employee → Location
    # --------------------------------------------------------

    print("\n8. Employee → Location relationship")

    locations = datasets["locations.csv"]
    employees = datasets["employees.csv"]

    valid_locations = set(
        locations["location_id"]
    )

    invalid_employee_locations = (
        ~employees["location_id"].isin(
            valid_locations
        )
    ).sum()

    check(
        invalid_employee_locations == 0,
        (
            "Every employee references "
            "a valid location"
        ),
    )

    # --------------------------------------------------------
    # Machine → Location
    # --------------------------------------------------------

    print("\n9. Machine → Location relationship")

    machines = datasets["machines.csv"]

    invalid_machine_locations = (
        ~machines["location_id"].isin(
            valid_locations
        )
    ).sum()

    check(
        invalid_machine_locations == 0,
        (
            "Every machine references "
            "a valid location"
        ),
    )

    # --------------------------------------------------------
    # Geographic Validation
    # --------------------------------------------------------

    print("\n10. Geographic consistency")

    locations = datasets["locations.csv"]

    location_pairs = set(
        zip(
            locations["city"],
            locations["state_region"],
            locations["country"],
        )
    )

    invalid_location_pairs = (
        location_pairs
        - VALID_LOCATION_PAIRS
    )

    check(
        len(invalid_location_pairs) == 0,
        (
            "All operational locations use "
            "valid city/state-region/country combinations"
        ),
    )

    valid_countries = {
        "United States",
        "Sweden",
    }

    invalid_countries = (
        ~locations["country"].isin(
            valid_countries
        )
    ).sum()

    check(
        invalid_countries == 0,
        (
            "Operational locations use only "
            "approved countries"
        ),
    )

    # --------------------------------------------------------
    # Basic Product Pricing Logic
    # --------------------------------------------------------

    print("\n11. Basic product value validation")

    products = datasets["products.csv"]

    invalid_costs = (
        products["unit_cost"] <= 0
    ).sum()

    invalid_prices = (
        products["unit_price"] <= 0
    ).sum()

    check(
        invalid_costs == 0,
        "All product unit costs are positive",
    )

    check(
        invalid_prices == 0,
        "All product unit prices are positive",
    )

    # --------------------------------------------------------
    # Final Result
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "REFERENCE DATA VALIDATION PASSED"
    )
    print("=" * 60)

    print(
        "\nThe seven reference datasets are ready "
        "for the next generation step."
    )


if __name__ == "__main__":
    main()
