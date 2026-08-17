"""
Project Atlas
Phase 3 — Business Data Validation

Validates the clean business datasets.

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


EXPECTED_COUNTS = {
    "sales.csv": N_SALES,
    "production.csv": N_PRODUCTION,
    "maintenance.csv": N_MAINTENANCE,
    "financial_transactions.csv": N_FINANCIAL_TRANSACTIONS,
    "budget.csv": N_BUDGET,
    "energy.csv": N_ENERGY,
    "emissions.csv": N_EMISSIONS,
    "waste.csv": N_WASTE,
    "inventory.csv": N_INVENTORY,
}


KEYS = {
    "sales.csv": "transaction_id",
    "production.csv": "production_id",
    "maintenance.csv": "maintenance_id",
    "financial_transactions.csv": "financial_transaction_id",
    "budget.csv": "budget_id",
    "energy.csv": "energy_id",
    "emissions.csv": "emissions_id",
    "waste.csv": "waste_id",
    "inventory.csv": "inventory_id",
}


REQUIRED_COLUMNS = {
    "sales.csv": [
        "transaction_id",
        "transaction_date",
        "account_id",
        "customer_id",
        "product_id",
        "location_id",
        "quantity",
        "unit_price",
        "discount_amount",
        "revenue",
    ],
    "production.csv": [
        "production_id",
        "production_date",
        "product_id",
        "location_id",
        "machine_id",
        "employee_id",
        "planned_quantity",
        "produced_quantity",
        "defect_quantity",
        "production_hours",
    ],
    "maintenance.csv": [
        "maintenance_id",
        "maintenance_date",
        "location_id",
        "machine_id",
        "employee_id",
        "maintenance_type",
        "maintenance_hours",
        "downtime_hours",
        "maintenance_cost",
    ],
    "financial_transactions.csv": [
        "financial_transaction_id",
        "transaction_date",
        "location_id",
        "category",
        "transaction_type",
        "amount",
    ],
    "budget.csv": [
        "budget_id",
        "budget_date",
        "location_id",
        "budget_category",
        "budget_amount",
    ],
    "energy.csv": [
        "energy_id",
        "measurement_date",
        "location_id",
        "energy_type",
        "consumption",
        "unit",
        "energy_cost",
    ],
    "emissions.csv": [
        "emissions_id",
        "emissions_date",
        "location_id",
        "emission_source",
        "co2e_amount",
        "unit",
    ],
    "waste.csv": [
        "waste_id",
        "waste_date",
        "location_id",
        "waste_type",
        "waste_quantity",
        "unit",
        "disposal_method",
    ],
    "inventory.csv": [
        "inventory_id",
        "inventory_date",
        "product_id",
        "location_id",
        "opening_quantity",
        "received_quantity",
        "issued_quantity",
        "closing_quantity",
        "reorder_point",
    ],
}


def load(filename):

    return pd.read_csv(
        RAW_DATA_DIR / filename
    )


def main():

    print("=" * 60)
    print("Project Atlas — Business Data Validation")
    print("Mode: CLEAN BASELINE")
    print("=" * 60)

    failed = False
    data = {}

    # --------------------------------------------------------
    # Record counts
    # --------------------------------------------------------

    print("\n1. Record count validation")

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
    # Stop if structure is invalid
    # --------------------------------------------------------

    if failed:

        print("\n" + "=" * 60)
        print("BUSINESS DATA VALIDATION FAILED")
        print("Fix the clean baseline before continuing.")
        print("=" * 60)

        raise SystemExit(1)

    # --------------------------------------------------------
    # Business keys
    # --------------------------------------------------------

    print("\n3. Business-key validation")

    for filename, key in KEYS.items():

        series = data[filename][key]

        if series.isna().any():
            print(
                f"FAIL  {filename}: {key} contains nulls"
            )
            failed = True
        elif series.duplicated().any():
            print(
                f"FAIL  {filename}: {key} contains duplicates"
            )
            failed = True
        else:
            print(
                f"PASS  {filename}: "
                f"{key} contains no nulls or duplicates"
            )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    print("\n4. Required-field null validation")

    required_fields = {
        "sales.csv": [
            "transaction_id",
            "transaction_date",
            "account_id",
            "customer_id",
            "product_id",
            "location_id",
        ],
        "production.csv": [
            "production_id",
            "production_date",
            "product_id",
            "location_id",
            "machine_id",
            "employee_id",
        ],
        "maintenance.csv": [
            "maintenance_id",
            "maintenance_date",
            "location_id",
            "machine_id",
            "employee_id",
        ],
        "financial_transactions.csv": [
            "financial_transaction_id",
            "transaction_date",
            "location_id",
            "category",
        ],
        "budget.csv": [
            "budget_id",
            "budget_date",
            "location_id",
            "budget_category",
        ],
        "energy.csv": [
            "energy_id",
            "measurement_date",
            "location_id",
            "energy_type",
        ],
        "emissions.csv": [
            "emissions_id",
            "emissions_date",
            "location_id",
            "emission_source",
        ],
        "waste.csv": [
            "waste_id",
            "waste_date",
            "location_id",
            "waste_type",
        ],
        "inventory.csv": [
            "inventory_id",
            "inventory_date",
            "product_id",
            "location_id",
        ],
    }

    for filename, columns in required_fields.items():

        for column in columns:

            if data[filename][column].isna().any():
                print(
                    f"FAIL  {filename}: "
                    f"{column} contains nulls"
                )
                failed = True
            else:
                print(
                    f"PASS  {filename}: "
                    f"{column} contains no nulls"
                )

    # --------------------------------------------------------
    # Reference data
    # --------------------------------------------------------

    references = {
        "accounts": load("accounts.csv"),
        "customers": load("customers.csv"),
        "products": load("products.csv"),
        "locations": load("locations.csv"),
        "employees": load("employees.csv"),
        "machines": load("machines.csv"),
    }

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    print("\n5. Foreign-key validation")

    fk_checks = [
        ("sales.csv", "account_id", "accounts", "account_id"),
        ("sales.csv", "customer_id", "customers", "customer_id"),
        ("sales.csv", "product_id", "products", "product_id"),
        ("sales.csv", "location_id", "locations", "location_id"),

        ("production.csv", "product_id", "products", "product_id"),
        ("production.csv", "location_id", "locations", "location_id"),
        ("production.csv", "machine_id", "machines", "machine_id"),
        ("production.csv", "employee_id", "employees", "employee_id"),

        ("maintenance.csv", "location_id", "locations", "location_id"),
        ("maintenance.csv", "machine_id", "machines", "machine_id"),
        ("maintenance.csv", "employee_id", "employees", "employee_id"),

        ("financial_transactions.csv", "location_id", "locations", "location_id"),
        ("budget.csv", "location_id", "locations", "location_id"),
        ("energy.csv", "location_id", "locations", "location_id"),
        ("emissions.csv", "location_id", "locations", "location_id"),
        ("waste.csv", "location_id", "locations", "location_id"),
        ("inventory.csv", "product_id", "products", "product_id"),
        ("inventory.csv", "location_id", "locations", "location_id"),
    ]

    for child_file, child_key, parent, parent_key in fk_checks:

        valid = data[child_file][child_key].isin(
            set(references[parent][parent_key])
        )

        if valid.all():
            print(
                f"PASS  {child_file}: "
                f"{child_key} → {parent}.{parent_key}"
            )
        else:
            print(
                f"FAIL  {child_file}: "
                f"{child_key} contains invalid references"
            )
            failed = True

    # --------------------------------------------------------
    # Business consistency
    # --------------------------------------------------------

    print("\n6. Business consistency validation")

    customer_accounts = references["customers"].set_index(
        "customer_id"
    )["account_id"]

    sales = data["sales.csv"]

    expected_accounts = sales["customer_id"].map(
        customer_accounts
    )

    if (
        sales["account_id"].to_numpy()
        == expected_accounts.to_numpy()
    ).all():

        print(
            "PASS  Sales account matches customer account"
        )
    else:
        print(
            "FAIL  Sales account does not match customer account"
        )
        failed = True

    machine_locations = references["machines"].set_index(
        "machine_id"
    )["location_id"]

    production = data["production.csv"]

    expected_locations = production["machine_id"].map(
        machine_locations
    )

    if (
        production["location_id"].to_numpy()
        == expected_locations.to_numpy()
    ).all():

        print(
            "PASS  Production machine location matches machine master"
        )
    else:
        print(
            "FAIL  Production machine location mismatch"
        )
        failed = True

    maintenance = data["maintenance.csv"]

    expected_locations = maintenance["machine_id"].map(
        machine_locations
    )

    if (
        maintenance["location_id"].to_numpy()
        == expected_locations.to_numpy()
    ).all():

        print(
            "PASS  Maintenance machine location matches machine master"
        )
    else:
        print(
            "FAIL  Maintenance machine location mismatch"
        )
        failed = True

    employee_locations = references["employees"].set_index(
        "employee_id"
    )["location_id"]

    expected_locations = production["employee_id"].map(
        employee_locations
    )

    if (
        production["location_id"].to_numpy()
        == expected_locations.to_numpy()
    ).all():

        print(
            "PASS  Production employee location matches employee master"
        )
    else:
        print(
            "FAIL  Production employee location mismatch"
        )
        failed = True

    # --------------------------------------------------------
    # Numeric rules
    # --------------------------------------------------------

    print("\n7. Numeric business-rule validation")

    checks = [
        (
            "Sales quantities are positive",
            (sales["quantity"] > 0).all(),
        ),
        (
            "Sales unit prices are positive",
            (sales["unit_price"] > 0).all(),
        ),
        (
            "Sales revenue calculation is consistent",
            (
                sales["revenue"]
                == (
                    sales["quantity"]
                    * sales["unit_price"]
                    - sales["discount_amount"]
                ).round(2)
            ).all(),
        ),
    ]

    production = data["production.csv"]

    checks += [
        (
            "Production planned quantities are non-negative",
            (production["planned_quantity"] >= 0).all(),
        ),
        (
            "Production quantities are non-negative",
            (production["produced_quantity"] >= 0).all(),
        ),
        (
            "Production defect quantity does not exceed production quantity",
            (
                production["defect_quantity"]
                <= production["produced_quantity"]
            ).all(),
        ),
    ]

    maintenance = data["maintenance.csv"]

    checks += [
        (
            "Maintenance hours are positive",
            (maintenance["maintenance_hours"] > 0).all(),
        ),
        (
            "Maintenance downtime is non-negative",
            (maintenance["downtime_hours"] >= 0).all(),
        ),
    ]

    for message, passed in checks:

        if passed:
            print(f"PASS  {message}")
        else:
            print(f"FAIL  {message}")
            failed = True

    # --------------------------------------------------------
    # Inventory grain
    # --------------------------------------------------------

    print("\n8. Inventory grain validation")

    inventory = data["inventory.csv"]

    duplicate_grain = inventory.duplicated(
        subset=[
            "inventory_date",
            "product_id",
            "location_id",
        ]
    ).any()

    if not duplicate_grain:
        print(
            "PASS  Inventory Date + Product + Location is unique"
        )
    else:
        print(
            "FAIL  Inventory Date + Product + Location contains duplicates"
        )
        failed = True

    reconciled = (
        inventory["opening_quantity"]
        + inventory["received_quantity"]
        - inventory["issued_quantity"]
        == inventory["closing_quantity"]
    ).all()

    if reconciled:
        print(
            "PASS  Inventory closing quantity reconciles"
        )
    else:
        print(
            "FAIL  Inventory closing quantity does not reconcile"
        )
        failed = True

    if (
        inventory["closing_quantity"] >= 0
    ).all():

        print(
            "PASS  Inventory closing quantity is non-negative"
        )
    else:
        print(
            "FAIL  Inventory closing quantity is negative"
        )
        failed = True

    # --------------------------------------------------------
    # Date ranges
    # --------------------------------------------------------

    print("\n9. Date-range validation")

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    date_columns = {
        "sales.csv": "transaction_date",
        "production.csv": "production_date",
        "maintenance.csv": "maintenance_date",
        "financial_transactions.csv": "transaction_date",
        "budget.csv": "budget_date",
        "energy.csv": "measurement_date",
        "emissions.csv": "emissions_date",
        "waste.csv": "waste_date",
        "inventory.csv": "inventory_date",
    }

    for filename, column in date_columns.items():

        dates = pd.to_datetime(
            data[filename][column]
        )

        if (
            dates.between(start, end)
        ).all():

            print(
                f"PASS  {filename}: dates fall within approved range"
            )
        else:
            print(
                f"FAIL  {filename}: dates outside approved range"
            )
            failed = True

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    if failed:
        print("BUSINESS DATA VALIDATION FAILED")
        print("Clean baseline must pass before injection.")
        print("=" * 60)
        raise SystemExit(1)

    print("BUSINESS DATA VALIDATION PASSED")
    print("The nine clean business datasets are ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()
