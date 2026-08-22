import os
import pandas as pd


STAGING_FOLDER = "05_ETL/data/staging"
WAREHOUSE_READY_FOLDER = "05_ETL/data/warehouse_ready"

os.makedirs(WAREHOUSE_READY_FOLDER, exist_ok=True)


# Expected columns for each warehouse table
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


# Actual date fields that need standard formatting
DATE_COLUMNS = [
    "full_date",
    "hire_date",
    "installation_date"
]


for file_name in sorted(EXPECTED_COLUMNS):

    input_path = os.path.join(STAGING_FOLDER, file_name)
    output_path = os.path.join(WAREHOUSE_READY_FOLDER, file_name)

    print(f"Processing {file_name}...")

    # Read staging data
    df = pd.read_csv(input_path)

    original_row_count = len(df)

    # Check that all expected columns exist
    expected_columns = EXPECTED_COLUMNS[file_name]

    if list(df.columns) != expected_columns:
        raise ValueError(
            f"Column structure does not match expected structure: {file_name}"
        )

    # Standardize actual date fields
    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="raise"
            ).dt.strftime("%Y-%m-%d")

    # Write warehouse-ready data
    df.to_csv(output_path, index=False)

    # Confirm row count was preserved
    if len(df) != original_row_count:
        raise ValueError(
            f"Row count changed during transformation: {file_name}"
        )

    print(f"  Rows: {len(df):,}")
    print(f"  Saved: {output_path}")


print("\nWarehouse-ready transformation completed successfully.")