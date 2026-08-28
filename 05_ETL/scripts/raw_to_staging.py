import os
from pathlib import Path

import pandas as pd


# Project Atlas repository root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "04_Data_Quality" / "data" / "trusted"

STAGING_FOLDER = PROJECT_ROOT / "05_ETL" / "data" / "staging"

# Create staging folder if it does not exist
os.makedirs(STAGING_FOLDER, exist_ok=True)


# Columns that should be treated as dates
DATE_COLUMNS = {
    "full_date",
    "hire_date",
    "installation_date"
}


# Read each raw CSV
for file_name in sorted(os.listdir(RAW_FOLDER)):

    if not file_name.endswith(".csv"):
        continue

    input_path = os.path.join(RAW_FOLDER, file_name)
    output_path = os.path.join(STAGING_FOLDER, file_name)

    print(f"Processing {file_name}...")

    # Read the raw dataset
    df = pd.read_csv(input_path)

    # Convert date columns when they exist
    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    # Convert numeric-looking columns to numeric values
    for column in df.columns:

        if column.endswith("_key"):
            df[column] = pd.to_numeric(df[column], errors="coerce")

        elif column in [
            "quantity",
            "planned_quantity",
            "produced_quantity",
            "defect_quantity",
            "production_hours",
            "maintenance_hours",
            "downtime_hours",
            "maintenance_cost",
            "budget_amount",
            "transaction_amount",
            "opening_quantity",
            "received_quantity",
            "issued_quantity",
            "closing_quantity",
            "reorder_point",
            "energy_consumption",
            "co2_emissions",
            "waste_quantity",
            "unit_cost",
            "unit_price",
            "discount_amount",
            "revenue"
        ]:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Write staging dataset
    df.to_csv(output_path, index=False)

    print(f"  Rows: {len(df):,}")
    print(f"  Saved: {output_path}")

print("\nStaging transformation completed.")