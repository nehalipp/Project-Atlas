"""
Project Atlas
Phase 3 — Business Data Validation

Validates the nine transactional/business datasets.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

START_DATE = pd.Timestamp("2019-01-01")
END_DATE = pd.Timestamp("2025-12-31")


EXPECTED_COUNTS = {
    "sales.csv": 500_000,
    "production.csv": 200_000,
    "maintenance.csv": 50_000,
    "financial_transactions.csv": 300_000,
    "budget.csv": 20_000,
    "energy.csv": 100_000,
    "emissions.csv": 100_000,
    "waste.csv": 100_000,
    "inventory.csv": 500_000,
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


KEY_COLUMNS = {
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


def foreign_key_check(
    child,
    child_column,
    parent,
    parent_column,
):
    return child[child_column].isin(
        parent[parent_column]
    ).all()


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Business Data Validation")
    print("Mode: CLEAN BASELINE")
    print("=" * 60)

    data = {
        filename: load(filename)
        for filename in EXPECTED_COUNTS
    }

    passed = True

    accounts = load("accounts.csv")
    customers = load("customers.csv")
    products = load("products.csv")
    locations = load("locations.csv")
    employees = load("employees.csv")
    machines = load("machines.csv")

    # ========================================================
    # 1. RECORD COUNTS
    # ========================================================

    print("\n1. Record count validation")

    for filename, expected in EXPECTED_COUNTS.items():

        actual = len(data[filename])

        passed &= check(
            actual == expected,
            f"{filename}: expected "
            f"{expected:,}, found {actual:,}",
        )

    # ========================================================
    # 2. REQUIRED COLUMNS
    # ========================================================

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
                else f"missing columns {missing}"
            ),
        )

    # Stop before later checks if columns are missing.
    if not passed:
        print("\nValidation stopped because required columns are missing.")
        raise SystemExit(1)

    # ========================================================
    # 3. BUSINESS KEYS
    # ========================================================

    print("\n3. Business-key uniqueness")

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

    # ========================================================
    # 4. REQUIRED FIELDS
    # ========================================================

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

            passed &= check(
                data[filename][column].notna().all(),
                f"{filename}: "
                f"{column} contains no nulls",
            )

    # ========================================================
    # 5. FOREIGN KEYS
    # ========================================================

    print("\n5. Foreign-key validation")

    sales = data["sales.csv"]
    production = data["production.csv"]
    maintenance = data["maintenance.csv"]
    financial = data["financial_transactions.csv"]
    budget = data["budget.csv"]
    energy = data["energy.csv"]
    emissions = data["emissions.csv"]
    waste = data["waste.csv"]
    inventory = data["inventory.csv"]

    checks = [
        (
            sales,
            "account_id",
            accounts,
            "account_id",
            "Sales → Account",
        ),
        (
            sales,
            "customer_id",
            customers,
            "customer_id",
            "Sales → Customer",
        ),
        (
            sales,
            "product_id",
            products,
            "product_id",
            "Sales → Product",
        ),
        (
            sales,
            "location_id",
            locations,
            "location_id",
            "Sales → Location",
        ),
        (
            production,
            "product_id",
            products,
            "product_id",
            "Production → Product",
        ),
        (
            production,
            "location_id",
            locations,
            "location_id",
            "Production → Location",
        ),
        (
            production,
            "machine_id",
            machines,
            "machine_id",
            "Production → Machine",
        ),
        (
            production,
            "employee_id",
            employees,
            "employee_id",
            "Production → Employee",
        ),
        (
            maintenance,
            "location_id",
            locations,
            "location_id",
            "Maintenance → Location",
        ),
        (
            maintenance,
            "machine_id",
            machines,
            "machine_id",
            "Maintenance → Machine",
        ),
        (
            maintenance,
            "employee_id",
            employees,
            "employee_id",
            "Maintenance → Employee",
        ),
        (
            financial,
            "location_id",
            locations,
            "location_id",
            "Financial → Location",
        ),
        (
            budget,
            "location_id",
            locations,
            "location_id",
            "Budget → Location",
        ),
        (
            energy,
            "location_id",
            locations,
            "location_id",
            "Energy → Location",
        ),
        (
            emissions,
            "location_id",
            locations,
            "location_id",
            "Emissions → Location",
        ),
        (
            waste,
            "location_id",
            locations,
            "location_id",
            "Waste → Location",
        ),
        (
            inventory,
            "product_id",
            products,
            "product_id",
            "Inventory → Product",
        ),
        (
            inventory,
            "location_id",
            locations,
            "location_id",
            "Inventory → Location",
        ),
    ]

    for child, child_col, parent, parent_col, message in checks:

        passed &= check(
            foreign_key_check(
                child,
                child_col,
                parent,
                parent_col,
            ),
            message,
        )

    # ========================================================
    # 6. BUSINESS CONSISTENCY
    # ========================================================

    print("\n6. Business consistency validation")

    customer_accounts = customers.set_index(
        "customer_id"
    )["account_id"]

    passed &= check(
        sales["account_id"].eq(
            sales["customer_id"].map(
                customer_accounts
            )
        ).all(),
        "Sales account matches customer account",
    )

    machine_locations = machines.set_index(
        "machine_id"
    )["location_id"]

    passed &= check(
        production["location_id"].eq(
            production["machine_id"].map(
                machine_locations
            )
        ).all(),
        "Production machine location matches machine master",
    )

    passed &= check(
        maintenance["location_id"].eq(
            maintenance["machine_id"].map(
                machine_locations
            )
        ).all(),
        "Maintenance machine location matches machine master",
    )

    employee_locations = employees.set_index(
        "employee_id"
    )["location_id"]

    passed &= check(
        production["location_id"].eq(
            production["employee_id"].map(
                employee_locations
            )
        ).all(),
        "Production employee location matches employee master",
    )

    # ========================================================
    # 7. NUMERIC BUSINESS RULES
    # ========================================================

    print("\n7. Numeric business-rule validation")

    sales_expected_revenue = (
        sales["quantity"]
        * sales["unit_price"]
        - sales["discount_amount"]
    )

    passed &= check(
        sales["revenue"].round(2).eq(
            sales_expected_revenue.round(2)
        ).all(),
        "Sales revenue calculation is consistent",
    )

    passed &= check(
        (sales["quantity"] > 0).all(),
        "Sales quantities are positive",
    )

    passed &= check(
        (sales["unit_price"] > 0).all(),
        "Sales unit prices are positive",
    )

    passed &= check(
        (production["planned_quantity"] >= 0).all(),
        "Production planned quantities are non-negative",
    )

    passed &= check(
        (production["produced_quantity"] >= 0).all(),
        "Production quantities are non-negative",
    )

    passed &= check(
        (
            production["defect_quantity"]
            <= production["produced_quantity"]
        ).all(),
        "Production defect quantity does not exceed production quantity",
    )

    passed &= check(
        (maintenance["maintenance_hours"] > 0).all(),
        "Maintenance hours are positive",
    )

    passed &= check(
        (maintenance["downtime_hours"] >= 0).all(),
        "Maintenance downtime is non-negative",
    )

    # ========================================================
    # 8. INVENTORY
    # ========================================================

    print("\n8. Inventory grain validation")

    grain = [
        "inventory_date",
        "product_id",
        "location_id",
    ]

    passed &= check(
        not inventory.duplicated(grain).any(),
        "Inventory grain Date + Product + Location is unique",
    )

    expected_closing = (
        inventory["opening_quantity"]
        + inventory["received_quantity"]
        - inventory["issued_quantity"]
    )

    passed &= check(
        inventory["closing_quantity"].eq(
            expected_closing
        ).all(),
        "Inventory closing quantity reconciles",
    )

    passed &= check(
        (inventory["closing_quantity"] >= 0).all(),
        "Inventory closing quantity is non-negative",
    )

    # ========================================================
    # 9. DATE RANGE
    # ========================================================

    print("\n9. Date-range validation")

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

        passed &= check(
            dates.between(
                START_DATE,
                END_DATE,
            ).all(),
            f"{filename}: dates fall within approved range",
        )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 60)

    if passed:
        print("BUSINESS DATA VALIDATION PASSED")
        print(
            "The nine clean business datasets are ready."
        )
    else:
        print("BUSINESS DATA VALIDATION FAILED")

    print("=" * 60)

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
