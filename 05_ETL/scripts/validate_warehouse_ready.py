import os
import pandas as pd


WAREHOUSE_READY_FOLDER = "05_ETL/data/warehouse_ready"


EXPECTED_ROW_COUNTS = {
    "dim_account.csv": 1000,
    "dim_customer.csv": 50000,
    "dim_date.csv": 2557,
    "dim_employee.csv": 5000,
    "dim_location.csv": 100,
    "dim_machine.csv": 2000,
    "dim_product.csv": 5000,
    "dim_supplier.csv": 1000,
    "fact_budget.csv": 20000,
    "fact_emissions.csv": 100000,
    "fact_energy.csv": 99800,
    "fact_financial_transaction.csv": 300000,
    "fact_inventory.csv": 499000,
    "fact_maintenance.csv": 49950,
    "fact_production.csv": 200000,
    "fact_sales.csv": 499002,
    "fact_waste.csv": 99900
}


EXPECTED_COLUMNS = {
    "dim_account.csv": [
        "account_key", "account_id", "account_name", "account_type",
        "industry", "country", "status"
    ],
    "dim_customer.csv": [
        "customer_key", "customer_id", "account_key", "customer_name",
        "customer_segment", "industry", "country", "status"
    ],
    "dim_date.csv": [
        "date_key", "full_date", "day_of_week", "day_name",
        "week_number", "month", "month_name", "quarter", "year"
    ],
    "dim_employee.csv": [
        "employee_key", "employee_id", "location_key", "employee_name",
        "department", "role", "hire_date", "status"
    ],
    "dim_location.csv": [
        "location_key", "location_id", "location_name", "location_type",
        "city", "state_region", "country", "status"
    ],
    "dim_machine.csv": [
        "machine_key", "machine_id", "location_key", "machine_name",
        "machine_type", "installation_date", "status"
    ],
    "dim_product.csv": [
        "product_key", "product_id", "supplier_key", "product_name",
        "category", "subcategory", "unit_of_measure", "unit_cost",
        "unit_price", "status"
    ],
    "dim_supplier.csv": [
        "supplier_key", "supplier_id", "supplier_name",
        "supplier_category", "country", "status"
    ],
    "fact_budget.csv": [
        "budget_key", "budget_id", "date_key", "account_key",
        "location_key", "budget_category", "budget_amount"
    ],
    "fact_emissions.csv": [
        "emissions_key", "emissions_id", "date_key", "location_key",
        "emissions_category", "co2_emissions"
    ],
    "fact_energy.csv": [
        "energy_key", "energy_id", "date_key", "location_key",
        "machine_key", "energy_source", "energy_consumption"
    ],
    "fact_financial_transaction.csv": [
        "financial_transaction_key", "transaction_id", "date_key",
        "account_key", "location_key", "transaction_type",
        "transaction_category", "transaction_amount"
    ],
    "fact_inventory.csv": [
        "inventory_key", "inventory_id", "date_key", "product_key",
        "location_key", "opening_quantity", "received_quantity",
        "issued_quantity", "closing_quantity", "reorder_point"
    ],
    "fact_maintenance.csv": [
        "maintenance_key", "maintenance_id", "date_key", "location_key",
        "machine_key", "employee_key", "maintenance_type",
        "maintenance_hours", "downtime_hours", "maintenance_cost"
    ],
    "fact_production.csv": [
        "production_key", "production_id", "date_key", "product_key",
        "location_key", "machine_key", "employee_key",
        "planned_quantity", "produced_quantity", "defect_quantity",
        "production_hours"
    ],
    "fact_sales.csv": [
        "sales_key", "transaction_id", "date_key", "customer_key",
        "product_key", "location_key", "quantity", "unit_price",
        "discount_amount", "revenue"
    ],
    "fact_waste.csv": [
        "waste_key", "waste_id", "date_key", "location_key",
        "waste_category", "disposal_method", "waste_quantity"
    ]
}


print("Starting warehouse-ready validation...\n")


# --------------------------------------------------
# 1. Check dataset count
# --------------------------------------------------

files = [
    file_name
    for file_name in os.listdir(WAREHOUSE_READY_FOLDER)
    if file_name.endswith(".csv")
]

if len(files) != 17:
    raise ValueError(
        f"Expected 17 datasets but found {len(files)}."
    )

print("Dataset count: PASS - 17 datasets found")


# --------------------------------------------------
# 2. Check each dataset
# --------------------------------------------------

for file_name, expected_rows in EXPECTED_ROW_COUNTS.items():

    file_path = os.path.join(WAREHOUSE_READY_FOLDER, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Missing dataset: {file_name}"
        )

    df = pd.read_csv(file_path)

    # Row count
    actual_rows = len(df)

    if actual_rows != expected_rows:
        raise ValueError(
            f"{file_name}: expected {expected_rows:,} rows "
            f"but found {actual_rows:,}."
        )

    # Column structure
    expected_columns = EXPECTED_COLUMNS[file_name]

    if list(df.columns) != expected_columns:
        raise ValueError(
            f"{file_name}: column structure does not match expected structure."
        )

    print(
        f"{file_name}: PASS - "
        f"{actual_rows:,} rows, columns validated"
    )


# --------------------------------------------------
# 3. Referential integrity checks
# --------------------------------------------------

dimensions = {}

dimension_files = [
    "dim_date.csv",
    "dim_account.csv",
    "dim_customer.csv",
    "dim_product.csv",
    "dim_supplier.csv",
    "dim_location.csv",
    "dim_employee.csv",
    "dim_machine.csv"
]


for file_name in dimension_files:

    file_path = os.path.join(
        WAREHOUSE_READY_FOLDER,
        file_name
    )

    dimensions[file_name] = pd.read_csv(file_path)


def check_foreign_key(
    fact_file,
    fact_column,
    dimension_file,
    dimension_column
):

    fact = pd.read_csv(
        os.path.join(WAREHOUSE_READY_FOLDER, fact_file),
        usecols=[fact_column]
    )

    dimension = dimensions[dimension_file]

    valid_keys = set(
        dimension[dimension_column]
    )

    invalid_keys = fact[
        ~fact[fact_column].isin(valid_keys)
    ]

    if len(invalid_keys) > 0:
        raise ValueError(
            f"{fact_file}.{fact_column}: "
            f"{len(invalid_keys):,} invalid foreign keys."
        )

    print(
        f"FK PASS - {fact_file}.{fact_column} → "
        f"{dimension_file}.{dimension_column}"
    )


foreign_key_checks = [

    ("fact_budget.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_budget.csv", "account_key", "dim_account.csv", "account_key"),
    ("fact_budget.csv", "location_key", "dim_location.csv", "location_key"),

    ("fact_emissions.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_emissions.csv", "location_key", "dim_location.csv", "location_key"),

    ("fact_energy.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_energy.csv", "location_key", "dim_location.csv", "location_key"),
    ("fact_energy.csv", "machine_key", "dim_machine.csv", "machine_key"),

    (
        "fact_financial_transaction.csv",
        "date_key",
        "dim_date.csv",
        "date_key"
    ),
    (
        "fact_financial_transaction.csv",
        "account_key",
        "dim_account.csv",
        "account_key"
    ),
    (
        "fact_financial_transaction.csv",
        "location_key",
        "dim_location.csv",
        "location_key"
    ),

    ("fact_inventory.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_inventory.csv", "product_key", "dim_product.csv", "product_key"),
    ("fact_inventory.csv", "location_key", "dim_location.csv", "location_key"),

    ("fact_maintenance.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_maintenance.csv", "location_key", "dim_location.csv", "location_key"),
    ("fact_maintenance.csv", "machine_key", "dim_machine.csv", "machine_key"),
    ("fact_maintenance.csv", "employee_key", "dim_employee.csv", "employee_key"),

    ("fact_production.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_production.csv", "product_key", "dim_product.csv", "product_key"),
    ("fact_production.csv", "location_key", "dim_location.csv", "location_key"),
    ("fact_production.csv", "machine_key", "dim_machine.csv", "machine_key"),
    ("fact_production.csv", "employee_key", "dim_employee.csv", "employee_key"),

    ("fact_sales.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_sales.csv", "customer_key", "dim_customer.csv", "customer_key"),
    ("fact_sales.csv", "product_key", "dim_product.csv", "product_key"),
    ("fact_sales.csv", "location_key", "dim_location.csv", "location_key"),

    ("fact_waste.csv", "date_key", "dim_date.csv", "date_key"),
    ("fact_waste.csv", "location_key", "dim_location.csv", "location_key")
]


for check in foreign_key_checks:
    check_foreign_key(*check)


# --------------------------------------------------
# 4. Nullable field validation
# --------------------------------------------------

nullable_columns = {
    "dim_product.csv": [
        "subcategory"
    ],
    "fact_waste.csv": [
        "disposal_method"
    ]
}


for file_name, allowed_columns in nullable_columns.items():

    file_path = os.path.join(
        WAREHOUSE_READY_FOLDER,
        file_name
    )

    df = pd.read_csv(file_path)

    for column in df.columns:

        null_count = df[column].isna().sum()

        if column in allowed_columns:
            print(
                f"NULL allowed - {file_name}.{column}: "
                f"{null_count:,}"
            )

        elif null_count > 0:
            raise ValueError(
                f"{file_name}.{column}: "
                f"{null_count:,} unexpected NULL values."
            )


print("\nWarehouse-ready validation completed successfully.")
