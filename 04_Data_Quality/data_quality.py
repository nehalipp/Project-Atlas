"""
Project Atlas
Phase 4 - Data Quality

Reads raw synthetic data from Phase 3, checks data quality,
applies simple deterministic remediation, and creates trusted
datasets for the next phase.

Quality checks:
- Missing values
- Blank / whitespace values
- Duplicate business IDs
- Invalid foreign keys
- Invalid categorical values
- Negative quantities
- Revenue reconciliation
- Inventory reconciliation
- Production business rules
- Production outliers
- Financial transaction outliers
"""

from pathlib import Path

import pandas as pd


# ============================================================
# SETTINGS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

RAW_DIR = (
    SCRIPT_DIR.parent
    / "03_Data_Generation"
    / "data"
    / "raw"
)

TRUSTED_DIR = (
    SCRIPT_DIR
    / "data"
    / "trusted"
)

SUMMARY_FILE = (
    SCRIPT_DIR
    / "quality_summary.xlsx"
)

TRUSTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    "dim_account",
    "dim_customer",
    "dim_date",
    "dim_employee",
    "dim_location",
    "dim_machine",
    "dim_product",
    "dim_supplier",
    "fact_budget",
    "fact_emissions",
    "fact_energy",
    "fact_financial_transaction",
    "fact_inventory",
    "fact_maintenance",
    "fact_production",
    "fact_sales",
    "fact_waste"
]


# ============================================================
# REFERENCE VALUES
# ============================================================

CUSTOMER_SEGMENTS = [
    "Enterprise",
    "Mid-Market",
    "SMB"
]

SUPPLIER_CATEGORIES = [
    "Manufacturer",
    "Distributor",
    "Service Provider",
    "Raw Material Supplier"
]

LOCATION_TYPES = [
    "Plant",
    "Warehouse",
    "Distribution Center",
    "Office"
]

MACHINE_STATUSES = [
    "Operational",
    "Maintenance",
    "Inactive"
]


# ============================================================
# REFERENCE DATA
# ============================================================

print("\n========================================")
print("PROJECT ATLAS - PHASE 4" + " DATA QUALITY")
print("========================================")

print("\nLoading Reference Data...")

dim_account = pd.read_csv(
    RAW_DIR / "dim_account.csv"
)

dim_customer = pd.read_csv(
    RAW_DIR / "dim_customer.csv"
)

dim_date = pd.read_csv(
    RAW_DIR / "dim_date.csv"
)

dim_employee = pd.read_csv(
    RAW_DIR / "dim_employee.csv"
)

dim_location = pd.read_csv(
    RAW_DIR / "dim_location.csv"
)

dim_machine = pd.read_csv(
    RAW_DIR / "dim_machine.csv"
)

dim_product = pd.read_csv(
    RAW_DIR / "dim_product.csv"
)

dim_supplier = pd.read_csv(
    RAW_DIR / "dim_supplier.csv"
)


# ============================================================
# LOAD ALL RAW DATA
# ============================================================

data = {}

for dataset in DATASETS:

    file_path = RAW_DIR / f"{dataset}.csv"

    data[dataset] = pd.read_csv(
        file_path
    )


# ============================================================
# QUALITY SUMMARY
# ============================================================

summary = []

issues = []


def add_issue(
    dataset,
    issue,
    action,
    rows
):
    """
    Add one quality issue to the report.
    """

    if rows > 0:

        issues.append({
            "Dataset": dataset,
            "Issue": issue,
            "Action": action,
            "Rows Affected": rows
        })


# ============================================================
# 1. CLEAN WHITESPACE
# ============================================================

for dataset in DATASETS:

    df = data[dataset]

    for column in df.columns:

        if df[column].dtype == "object":

            original = df[column].copy()

            df[column] = df[column].str.strip()

            changed = (
                original.fillna("")
                != df[column].fillna("")
            ).sum()

            add_issue(
                dataset,
                f"Leading/trailing whitespace in {column}",
                "Trim whitespace",
                int(changed)
            )

    data[dataset] = df


# ============================================================
# 2. MISSING DIMENSION VALUES
# ============================================================

df = data["dim_customer"]

count = df["country"].isna().sum()

df["country"] = df["country"].fillna(
    "Unknown"
)

add_issue(
    "dim_customer",
    "Missing country",
    "Fill with Unknown",
    int(count)
)

count = (
    df["customer_segment"]
    .isna()
    .sum()
)

df["customer_segment"] = (
    df["customer_segment"]
    .fillna("Unknown")
)

add_issue(
    "dim_customer",
    "Missing customer segment",
    "Fill with Unknown",
    int(count)
)

data["dim_customer"] = df


# ============================================================
# 3. INVALID CUSTOMER SEGMENTS
# ============================================================

df = data["dim_customer"]

invalid = ~df["customer_segment"].isin(
    CUSTOMER_SEGMENTS + ["Unknown"]
)

count = invalid.sum()

df.loc[
    invalid,
    "customer_segment"
] = "Unknown"

add_issue(
    "dim_customer",
    "Invalid customer segment",
    "Replace with Unknown",
    int(count)
)

data["dim_customer"] = df


# ============================================================
# 4. PRODUCT VALUES
# ============================================================

df = data["dim_product"]

count = df["subcategory"].isna().sum()

df["subcategory"] = (
    df["subcategory"]
    .fillna("Unknown")
)

add_issue(
    "dim_product",
    "Missing subcategory",
    "Fill with Unknown",
    int(count)
)

data["dim_product"] = df


# ============================================================
# 5. SUPPLIER VALUES
# ============================================================

df = data["dim_supplier"]

count = df["supplier_category"].isna().sum()

df["supplier_category"] = (
    df["supplier_category"]
    .fillna("Unknown")
)

add_issue(
    "dim_supplier",
    "Missing supplier category",
    "Fill with Unknown",
    int(count)
)

invalid = ~df["supplier_category"].isin(
    SUPPLIER_CATEGORIES + ["Unknown"]
)

count = invalid.sum()

df.loc[
    invalid,
    "supplier_category"
] = "Unknown"

add_issue(
    "dim_supplier",
    "Invalid supplier category",
    "Replace with Unknown",
    int(count)
)

data["dim_supplier"] = df


# ============================================================
# 6. LOCATION VALUES
# ============================================================

df = data["dim_location"]

invalid = ~df["location_type"].isin(
    LOCATION_TYPES
)

count = invalid.sum()

df.loc[
    invalid,
    "location_type"
] = "Unknown"

add_issue(
    "dim_location",
    "Invalid location type",
    "Replace with Unknown",
    int(count)
)

data["dim_location"] = df


# ============================================================
# 7. MACHINE VALUES
# ============================================================

df = data["dim_machine"]

invalid = ~df["status"].isin(
    MACHINE_STATUSES
)

count = invalid.sum()

df.loc[
    invalid,
    "status"
] = "Unknown"

add_issue(
    "dim_machine",
    "Invalid machine status",
    "Replace with Unknown",
    int(count)
)

data["dim_machine"] = df


# ============================================================
# 8. MAINTENANCE VALUES
# ============================================================

df = data["fact_maintenance"]

count = df["maintenance_type"].isna().sum()

df["maintenance_type"] = (
    df["maintenance_type"]
    .fillna("Unknown")
)

add_issue(
    "fact_maintenance",
    "Missing maintenance type",
    "Fill with Unknown",
    int(count)
)

data["fact_maintenance"] = df


# ============================================================
# 9. DUPLICATE SALES
# ============================================================

df = data["fact_sales"]

before = len(df)

df = df.drop_duplicates(
    subset=["transaction_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_sales",
    "Duplicate transaction IDs",
    "Remove duplicate rows",
    removed
)

data["fact_sales"] = df


# ============================================================
# 10. DUPLICATE PRODUCTION
# ============================================================

df = data["fact_production"]

before = len(df)

df = df.drop_duplicates(
    subset=["production_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_production",
    "Duplicate production IDs",
    "Remove duplicate rows",
    removed
)

data["fact_production"] = df


# ============================================================
# 11. DUPLICATE FINANCIAL TRANSACTIONS
# ============================================================

df = data["fact_financial_transaction"]

before = len(df)

df = df.drop_duplicates(
    subset=["transaction_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_financial_transaction",
    "Duplicate transaction IDs",
    "Remove duplicate rows",
    removed
)

data["fact_financial_transaction"] = df


# ============================================================
# 12. SALES FOREIGN KEY
# ============================================================

df = data["fact_sales"]

valid_customers = set(
    data["dim_customer"]["customer_key"]
)

invalid = ~df["customer_key"].isin(
    valid_customers
)

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_sales",
    "Invalid customer reference",
    "Remove row",
    int(count)
)

data["fact_sales"] = df


# ============================================================
# 13. INVENTORY FOREIGN KEY
# ============================================================

df = data["fact_inventory"]

valid_products = set(
    data["dim_product"]["product_key"]
)

invalid = ~df["product_key"].isin(
    valid_products
)

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_inventory",
    "Invalid product reference",
    "Remove row",
    int(count)
)

data["fact_inventory"] = df


# ============================================================
# 14. ENERGY FOREIGN KEY
# ============================================================

df = data["fact_energy"]

valid_machines = set(
    data["dim_machine"]["machine_key"]
)

invalid = ~df["machine_key"].isin(
    valid_machines
)

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_energy",
    "Invalid machine reference",
    "Remove row",
    int(count)
)

data["fact_energy"] = df


# ============================================================
# 15. MAINTENANCE FOREIGN KEY
# ============================================================

df = data["fact_maintenance"]

valid_employees = set(
    data["dim_employee"]["employee_key"]
)

invalid = ~df["employee_key"].isin(
    valid_employees
)

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_maintenance",
    "Invalid employee reference",
    "Remove row",
    int(count)
)

data["fact_maintenance"] = df


# ============================================================
# 16. NEGATIVE SALES QUANTITY
# ============================================================

df = data["fact_sales"]

invalid = df["quantity"] < 0

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_sales",
    "Negative sales quantity",
    "Remove row",
    int(count)
)

data["fact_sales"] = df


# ============================================================
# 17. NEGATIVE INVENTORY ISSUED QUANTITY
# ============================================================

df = data["fact_inventory"]

invalid = df["issued_quantity"] < 0

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_inventory",
    "Negative issued quantity",
    "Remove row",
    int(count)
)

data["fact_inventory"] = df


# ============================================================
# 18. NEGATIVE ENERGY
# ============================================================

df = data["fact_energy"]

invalid = df["energy_consumption"] < 0

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_energy",
    "Negative energy consumption",
    "Remove row",
    int(count)
)

data["fact_energy"] = df


# ============================================================
# 19. NEGATIVE WASTE
# ============================================================

df = data["fact_waste"]

invalid = df["waste_quantity"] < 0

count = invalid.sum()

df = df.loc[
    ~invalid
].copy()

add_issue(
    "fact_waste",
    "Negative waste quantity",
    "Remove row",
    int(count)
)

data["fact_waste"] = df


# ============================================================
# 20. SALES REVENUE RECONCILIATION
# ============================================================

df = data["fact_sales"]

expected_revenue = (
    df["quantity"]
    * df["unit_price"]
    - df["discount_amount"]
).round(2)

invalid = (
    df["revenue"].round(2)
    != expected_revenue
)

count = invalid.sum()

df.loc[
    invalid,
    "revenue"
] = expected_revenue[invalid]

add_issue(
    "fact_sales",
    "Revenue reconciliation failure",
    "Recalculate revenue",
    int(count)
)

data["fact_sales"] = df


# ============================================================
# 21. INVENTORY RECONCILIATION
# ============================================================

df = data["fact_inventory"]

expected_closing = (
    df["opening_quantity"]
    + df["received_quantity"]
    - df["issued_quantity"]
)

invalid = (
    df["closing_quantity"]
    != expected_closing
)

count = invalid.sum()

df.loc[
    invalid,
    "closing_quantity"
] = expected_closing[invalid]

add_issue(
    "fact_inventory",
    "Closing quantity reconciliation failure",
    "Recalculate closing quantity",
    int(count)
)

data["fact_inventory"] = df


# ============================================================
# 22. PRODUCTION BUSINESS RULE
# ============================================================

df = data["fact_production"]

invalid = (
    df["defect_quantity"]
    > df["produced_quantity"]
)

count = invalid.sum()

df.loc[
    invalid,
    "defect_quantity"
] = df.loc[
    invalid,
    "produced_quantity"
]

add_issue(
    "fact_production",
    "Defect quantity greater than produced quantity",
    "Cap defects at produced quantity",
    int(count)
)

data["fact_production"] = df


# ============================================================
# 23. PRODUCTION OUTLIERS
# ============================================================

df = data["fact_production"]

outlier = (
    df["produced_quantity"]
    > df["planned_quantity"] * 2
)

count = outlier.sum()

add_issue(
    "fact_production",
    "Production outlier",
    "Retain for investigation",
    int(count)
)


# ============================================================
# 24. FINANCIAL OUTLIERS
# ============================================================

df = data["fact_financial_transaction"]

outlier = (
    df["transaction_amount"]
    > 100_000
)

count = outlier.sum()

add_issue(
    "fact_financial_transaction",
    "Financial transaction outlier",
    "Retain for investigation",
    int(count)
)


# ============================================================
# 25. FINAL DATA VALIDATION
# ============================================================

print("\nValidating Trusted Data")

validation_results = []


for dataset in DATASETS:

    df = data[dataset]

    null_count = int(
        df.isna().sum().sum()
    )

    duplicate_count = int(
        df.duplicated().sum()
    )

    validation_results.append({
        "Dataset": dataset,
        "Null Values": null_count,
        "Duplicate Rows": duplicate_count
    })


validation_df = pd.DataFrame(
    validation_results
)


# ============================================================
# SAVE TRUSTED DATA
# ============================================================

print("\Saving Trusted Data")

for dataset in DATASETS:

    df = data[dataset]

    df.to_csv(
        TRUSTED_DIR / f"{dataset}.csv",
        index=False
    )

    print(
        f"{dataset}: {len(df):,} rows"
    )


# ============================================================
# CREATE QUALITY SUMMARY
# ============================================================

print("\nGenerating Data Quality Summary")


for dataset in DATASETS:

    raw_file = RAW_DIR / f"{dataset}.csv"

    raw_rows = len(
        pd.read_csv(raw_file)
    )

    trusted_rows = len(
        data[dataset]
    )

    rows_removed = (
        raw_rows
        - trusted_rows
    )

    retained_percent = round(
        trusted_rows
        / raw_rows
        * 100,
        1
    )

    summary.append({
        "Dataset": dataset,
        "Raw Rows": raw_rows,
        "Trusted Rows": trusted_rows,
        "Rows Removed": rows_removed,
        "Rows Retained %": retained_percent
    })


summary_df = pd.DataFrame(
    summary
)

issues_df = pd.DataFrame(
    issues
)


# ============================================================
# SAVE EXCEL SUMMARY
# ============================================================

with pd.ExcelWriter(
    SUMMARY_FILE,
    engine="openpyxl"
) as writer:

    summary_df.to_excel(
        writer,
        sheet_name="Dataset Summary",
        index=False
    )

    issues_df.to_excel(
        writer,
        sheet_name="Quality Issues",
        index=False
    )

    validation_df.to_excel(
        writer,
        sheet_name="Trusted Validation",
        index=False
    )


# ============================================================
# FINAL OUTPUT
# ============================================================
print(
    "\nTrusted datasets saved to:"
)

print(TRUSTED_DIR)

print(
    "\nQuality summary saved to:"
)

print(SUMMARY_FILE)

print(
    "\nTrusted dataset summary:"
)

print(
    summary_df.to_string(
        index=False
    )
)

print(
    "\nQuality issues addressed:"
)

if len(issues_df) > 0:

    print(
        issues_df.to_string(
            index=False
        )
    )

else:

    print("No quality issues detected.")
