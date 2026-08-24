"""
Project Atlas
Phase 4 - Data Quality

Reads raw synthetic data from Phase 3, checks data quality,
applies simple deterministic remediation, and creates trusted
datasets for the next phase.

Quality checks:
- Missing values
- Blank / whitespace values
- Duplicate rows
- Duplicate primary keys
- Duplicate business IDs
- Invalid foreign keys
- Invalid categorical values
- Invalid dates
- Negative quantities and measures
- Revenue reconciliation
- Inventory reconciliation
- Production business rules
- Production outliers
- Financial transaction outliers

Trusted-data principle:
- Required descriptive text fields -> Unknown
- Missing keys / IDs -> Remove row
- Missing numeric measures -> Remove row
- Missing required dates -> Remove row
- Invalid foreign keys -> Remove row
- Invalid categorical values -> Unknown
- Business-rule inconsistencies -> Correct where deterministic
- Outliers -> Retain and report for investigation
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


DIMENSIONS = [
    "dim_date",
    "dim_account",
    "dim_customer",
    "dim_product",
    "dim_supplier",
    "dim_location",
    "dim_employee",
    "dim_machine"
]


FACTS = [
    "fact_sales",
    "fact_production",
    "fact_maintenance",
    "fact_financial_transaction",
    "fact_budget",
    "fact_energy",
    "fact_emissions",
    "fact_waste",
    "fact_inventory"
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
# PRIMARY KEYS
# ============================================================

PRIMARY_KEYS = {
    "dim_date": "date_key",
    "dim_account": "account_key",
    "dim_customer": "customer_key",
    "dim_product": "product_key",
    "dim_supplier": "supplier_key",
    "dim_location": "location_key",
    "dim_employee": "employee_key",
    "dim_machine": "machine_key",
    "fact_sales": "sales_key",
    "fact_production": "production_key",
    "fact_maintenance": "maintenance_key",
    "fact_financial_transaction": "financial_transaction_key",
    "fact_budget": "budget_key",
    "fact_energy": "energy_key",
    "fact_emissions": "emissions_key",
    "fact_waste": "waste_key",
    "fact_inventory": "inventory_key"
}


# ============================================================
# BUSINESS / UNIQUE IDS
# ============================================================

BUSINESS_IDS = {
    "dim_date": "full_date",
    "dim_account": "account_id",
    "dim_customer": "customer_id",
    "dim_product": "product_id",
    "dim_supplier": "supplier_id",
    "dim_location": "location_id",
    "dim_employee": "employee_id",
    "dim_machine": "machine_id",
    "fact_sales": "transaction_id",
    "fact_production": "production_id",
    "fact_maintenance": "maintenance_id",
    "fact_financial_transaction": "transaction_id",
    "fact_budget": "budget_id",
    "fact_energy": "energy_id",
    "fact_emissions": "emissions_id",
    "fact_waste": "waste_id",
    "fact_inventory": "inventory_id"
}


# ============================================================
# REQUIRED TEXT COLUMNS
# ============================================================

REQUIRED_TEXT_COLUMNS = {

    "dim_account": [
        "account_id",
        "account_name",
        "account_type",
        "industry",
        "country",
        "status"
    ],

    "dim_customer": [
        "customer_id",
        "customer_name",
        "customer_segment",
        "industry",
        "country",
        "status"
    ],

    "dim_product": [
        "product_id",
        "product_name",
        "category",
        "unit_of_measure",
        "status"
    ],

    "dim_supplier": [
        "supplier_id",
        "supplier_name",
        "supplier_category",
        "country",
        "status"
    ],

    "dim_location": [
        "location_id",
        "location_name",
        "location_type",
        "city",
        "state_region",
        "country",
        "status"
    ],

    "dim_employee": [
        "employee_id",
        "employee_name",
        "department",
        "role",
        "status"
    ],

    "dim_machine": [
        "machine_id",
        "machine_name",
        "machine_type",
        "status"
    ],

    "fact_sales": [
        "transaction_id"
    ],

    "fact_production": [
        "production_id"
    ],

    "fact_maintenance": [
        "maintenance_id",
        "maintenance_type"
    ],

    "fact_financial_transaction": [
        "transaction_id",
        "transaction_type",
        "transaction_category"
    ],

    "fact_budget": [
        "budget_id",
        "budget_category"
    ],

    "fact_energy": [
        "energy_id",
        "energy_source"
    ],

    "fact_emissions": [
        "emissions_id",
        "emissions_category"
    ],

    "fact_waste": [
        "waste_id",
        "waste_category"
    ],

    "fact_inventory": [
        "inventory_id"
    ]
}


# ============================================================
# REQUIRED NUMERIC COLUMNS
# ============================================================

REQUIRED_NUMERIC_COLUMNS = {

    "dim_date": [
        "date_key",
        "day_of_week",
        "week_number",
        "month",
        "quarter",
        "year"
    ],

    "dim_account": [
        "account_key"
    ],

    "dim_customer": [
        "customer_key",
        "account_key"
    ],

    "dim_product": [
        "product_key",
        "supplier_key",
        "unit_cost",
        "unit_price"
    ],

    "dim_supplier": [
        "supplier_key"
    ],

    "dim_location": [
        "location_key"
    ],

    "dim_employee": [
        "employee_key",
        "location_key"
    ],

    "dim_machine": [
        "machine_key",
        "location_key"
    ],

    "fact_sales": [
        "sales_key",
        "date_key",
        "customer_key",
        "product_key",
        "location_key",
        "quantity",
        "unit_price",
        "discount_amount",
        "revenue"
    ],

    "fact_production": [
        "production_key",
        "date_key",
        "product_key",
        "location_key",
        "machine_key",
        "employee_key",
        "planned_quantity",
        "produced_quantity",
        "defect_quantity",
        "production_hours"
    ],

    "fact_maintenance": [
        "maintenance_key",
        "date_key",
        "location_key",
        "machine_key",
        "employee_key",
        "maintenance_hours",
        "downtime_hours",
        "maintenance_cost"
    ],

    "fact_financial_transaction": [
        "financial_transaction_key",
        "date_key",
        "account_key",
        "location_key",
        "transaction_amount"
    ],

    "fact_budget": [
        "budget_key",
        "date_key",
        "account_key",
        "location_key",
        "budget_amount"
    ],

    "fact_energy": [
        "energy_key",
        "date_key",
        "location_key",
        "machine_key",
        "energy_consumption"
    ],

    "fact_emissions": [
        "emissions_key",
        "date_key",
        "location_key",
        "co2_emissions"
    ],

    "fact_waste": [
        "waste_key",
        "date_key",
        "location_key",
        "waste_quantity"
    ],

    "fact_inventory": [
        "inventory_key",
        "date_key",
        "product_key",
        "location_key",
        "opening_quantity",
        "received_quantity",
        "issued_quantity",
        "closing_quantity",
        "reorder_point"
    ]
}


# ============================================================
# REQUIRED DATE COLUMNS
# ============================================================

REQUIRED_DATE_COLUMNS = {

    "dim_date": [
        "full_date"
    ],

    "dim_employee": [
        "hire_date"
    ],

    "dim_machine": [
        "installation_date"
    ]
}


# ============================================================
# NON-NEGATIVE NUMERIC RULES
# ============================================================

NON_NEGATIVE_COLUMNS = {

    "dim_product": [
        "unit_cost",
        "unit_price"
    ],

    "fact_sales": [
        "quantity",
        "unit_price",
        "discount_amount",
        "revenue"
    ],

    "fact_production": [
        "planned_quantity",
        "produced_quantity",
        "defect_quantity",
        "production_hours"
    ],

    "fact_maintenance": [
        "maintenance_hours",
        "downtime_hours",
        "maintenance_cost"
    ],

    "fact_budget": [
        "budget_amount"
    ],

    "fact_energy": [
        "energy_consumption"
    ],

    "fact_emissions": [
        "co2_emissions"
    ],

    "fact_waste": [
        "waste_quantity"
    ],

    "fact_inventory": [
        "opening_quantity",
        "received_quantity",
        "issued_quantity",
        "closing_quantity",
        "reorder_point"
    ]
}


# ============================================================
# EXPECTED NULLABLE COLUMNS
# ============================================================

# These are the nullable fields explicitly documented in
# the Atlas data dictionary.

EXPECTED_NULLABLE_COLUMNS = {
    "dim_product": [
        "subcategory"
    ],

    "fact_waste": [
        "disposal_method"
    ]
}


# ============================================================
# FOREIGN KEY RELATIONSHIPS
# ============================================================

FOREIGN_KEYS = [

    ("dim_customer", "account_key", "dim_account", "account_key"),

    ("dim_product", "supplier_key", "dim_supplier", "supplier_key"),

    ("dim_employee", "location_key", "dim_location", "location_key"),

    ("dim_machine", "location_key", "dim_location", "location_key"),

    ("fact_sales", "date_key", "dim_date", "date_key"),
    ("fact_sales", "customer_key", "dim_customer", "customer_key"),
    ("fact_sales", "product_key", "dim_product", "product_key"),
    ("fact_sales", "location_key", "dim_location", "location_key"),

    ("fact_production", "date_key", "dim_date", "date_key"),
    ("fact_production", "product_key", "dim_product", "product_key"),
    ("fact_production", "location_key", "dim_location", "location_key"),
    ("fact_production", "machine_key", "dim_machine", "machine_key"),
    ("fact_production", "employee_key", "dim_employee", "employee_key"),

    ("fact_maintenance", "date_key", "dim_date", "date_key"),
    ("fact_maintenance", "location_key", "dim_location", "location_key"),
    ("fact_maintenance", "machine_key", "dim_machine", "machine_key"),
    ("fact_maintenance", "employee_key", "dim_employee", "employee_key"),

    (
        "fact_financial_transaction",
        "date_key",
        "dim_date",
        "date_key"
    ),

    (
        "fact_financial_transaction",
        "account_key",
        "dim_account",
        "account_key"
    ),

    (
        "fact_financial_transaction",
        "location_key",
        "dim_location",
        "location_key"
    ),

    ("fact_budget", "date_key", "dim_date", "date_key"),
    ("fact_budget", "account_key", "dim_account", "account_key"),
    ("fact_budget", "location_key", "dim_location", "location_key"),

    ("fact_energy", "date_key", "dim_date", "date_key"),
    ("fact_energy", "location_key", "dim_location", "location_key"),
    ("fact_energy", "machine_key", "dim_machine", "machine_key"),

    ("fact_emissions", "date_key", "dim_date", "date_key"),
    ("fact_emissions", "location_key", "dim_location", "location_key"),

    ("fact_waste", "date_key", "dim_date", "date_key"),
    ("fact_waste", "location_key", "dim_location", "location_key"),

    ("fact_inventory", "date_key", "dim_date", "date_key"),
    ("fact_inventory", "product_key", "dim_product", "product_key"),
    ("fact_inventory", "location_key", "dim_location", "location_key")
]


# ============================================================
# START
# ============================================================

print("\n========================================")
print("PROJECT ATLAS - PHASE 4 DATA QUALITY")
print("========================================")


# ============================================================
# LOAD ALL RAW DATA
# ============================================================

print("\nLoading raw data...")

data = {}

for dataset in DATASETS:

    file_path = RAW_DIR / f"{dataset}.csv"

    data[dataset] = pd.read_csv(
        file_path
    )

    print(
        f"{dataset}: "
        f"{len(data[dataset]):,} rows"
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
# 1. CLEAN WHITESPACE AND BLANK TEXT
# ============================================================

print("\nCleaning text fields...")

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

            blank_count = (
                df[column]
                .fillna("")
                .eq("")
                .sum()
            )

            if blank_count > 0:

                df[column] = df[column].replace(
                    "",
                    pd.NA
                )

                add_issue(
                    dataset,
                    f"Blank value in {column}",
                    "Convert blank to NULL before remediation",
                    int(blank_count)
                )

    data[dataset] = df


# ============================================================
# 2. REQUIRED TEXT VALUES
# ============================================================

print("\nChecking required text fields...")

for dataset, columns in REQUIRED_TEXT_COLUMNS.items():

    df = data[dataset]

    for column in columns:

        count = df[column].isna().sum()

        if count > 0:

            # Business IDs are handled separately.
            if column == BUSINESS_IDS.get(dataset):

                continue

            df[column] = df[column].fillna(
                "Unknown"
            )

            add_issue(
                dataset,
                f"Missing required text value in {column}",
                "Fill with Unknown",
                int(count)
            )

    data[dataset] = df


# ============================================================
# 3. REQUIRED PRIMARY KEYS
# ============================================================

print("\nChecking primary keys...")

for dataset, column in PRIMARY_KEYS.items():

    df = data[dataset]

    missing = df[column].isna()

    count = missing.sum()

    if count > 0:

        df = df.loc[
            ~missing
        ].copy()

        add_issue(
            dataset,
            f"Missing primary key in {column}",
            "Remove row",
            int(count)
        )

    duplicate_count = (
        df[column]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:

        duplicate_rows = df[column].duplicated(
            keep="first"
        )

        df = df.loc[
            ~duplicate_rows
        ].copy()

        add_issue(
            dataset,
            f"Duplicate primary key in {column}",
            "Remove duplicate row",
            int(duplicate_count)
        )

    data[dataset] = df


# ============================================================
# 4. BUSINESS / UNIQUE IDS
# ============================================================

print("\nChecking business identifiers...")

for dataset, column in BUSINESS_IDS.items():

    df = data[dataset]

    missing = df[column].isna()

    count = missing.sum()

    if count > 0:

        df = df.loc[
            ~missing
        ].copy()

        add_issue(
            dataset,
            f"Missing business identifier in {column}",
            "Remove row",
            int(count)
        )

    duplicate_rows = df[column].duplicated(
        keep="first"
    )

    duplicate_count = duplicate_rows.sum()

    if duplicate_count > 0:

        df = df.loc[
            ~duplicate_rows
        ].copy()

        add_issue(
            dataset,
            f"Duplicate business identifier in {column}",
            "Remove duplicate row",
            int(duplicate_count)
        )

    data[dataset] = df


# ============================================================
# 5. REQUIRED NUMERIC VALUES
# ============================================================

print("\nChecking required numeric fields...")

for dataset, columns in REQUIRED_NUMERIC_COLUMNS.items():

    df = data[dataset]

    for column in columns:

        count = df[column].isna().sum()

        if count > 0:

            df = df.loc[
                df[column].notna()
            ].copy()

            add_issue(
                dataset,
                f"Missing required numeric value in {column}",
                "Remove row",
                int(count)
            )

    data[dataset] = df


# ============================================================
# 6. REQUIRED DATE VALUES
# ============================================================

print("\nChecking date fields...")

for dataset, columns in REQUIRED_DATE_COLUMNS.items():

    df = data[dataset]

    for column in columns:

        original_missing = df[column].isna().sum()

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_date_count = (
            df[column].isna().sum()
            - original_missing
        )

        if invalid_date_count > 0:

            add_issue(
                dataset,
                f"Invalid date in {column}",
                "Convert invalid date to NULL before validation",
                int(invalid_date_count)
            )

        missing_count = df[column].isna().sum()

        if missing_count > 0:

            df = df.loc[
                df[column].notna()
            ].copy()

            add_issue(
                dataset,
                f"Missing required date in {column}",
                "Remove row",
                int(missing_count)
            )

    data[dataset] = df


# ============================================================
# 7. CATEGORICAL VALIDATION
# ============================================================

print("\nChecking categorical values...")


# CUSTOMER SEGMENT

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


# SUPPLIER CATEGORY

df = data["dim_supplier"]

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


# LOCATION TYPE

df = data["dim_location"]

invalid = ~df["location_type"].isin(
    LOCATION_TYPES + ["Unknown"]
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


# MACHINE STATUS

df = data["dim_machine"]

invalid = ~df["status"].isin(
    MACHINE_STATUSES + ["Unknown"]
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
# 8. NON-NEGATIVE VALUES
# ============================================================

print("\nChecking non-negative numeric values...")

for dataset, columns in NON_NEGATIVE_COLUMNS.items():

    df = data[dataset]

    for column in columns:

        invalid = df[column] < 0

        count = invalid.sum()

        if count > 0:

            df = df.loc[
                ~invalid
            ].copy()

            add_issue(
                dataset,
                f"Negative value in {column}",
                "Remove row",
                int(count)
            )

    data[dataset] = df


# ============================================================
# 9. FOREIGN KEY VALIDATION
# ============================================================

print("\nChecking foreign keys...")

for (
    child_dataset,
    child_column,
    parent_dataset,
    parent_column
) in FOREIGN_KEYS:

    child_df = data[child_dataset]

    parent_df = data[parent_dataset]

    valid_values = set(
        parent_df[parent_column]
    )

    invalid = ~child_df[
        child_column
    ].isin(valid_values)

    count = invalid.sum()

    if count > 0:

        child_df = child_df.loc[
            ~invalid
        ].copy()

        add_issue(
            child_dataset,
            (
                f"Invalid foreign key: "
                f"{child_column} -> "
                f"{parent_dataset}.{parent_column}"
            ),
            "Remove row",
            int(count)
        )

    data[child_dataset] = child_df


# ============================================================
# 10. SALES DUPLICATE TRANSACTIONS
# ============================================================

print("\nChecking sales transactions...")

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
# 11. PRODUCTION DUPLICATE ACTIVITIES
# ============================================================

print("\nChecking production activities...")

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
# 12. MAINTENANCE DUPLICATE EVENTS
# ============================================================

df = data["fact_maintenance"]

before = len(df)

df = df.drop_duplicates(
    subset=["maintenance_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_maintenance",
    "Duplicate maintenance IDs",
    "Remove duplicate rows",
    removed
)

data["fact_maintenance"] = df


# ============================================================
# 13. FINANCIAL TRANSACTION DUPLICATES
# ============================================================

print("\nChecking financial transactions...")

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
# 14. BUDGET DUPLICATES
# ============================================================

df = data["fact_budget"]

before = len(df)

df = df.drop_duplicates(
    subset=["budget_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_budget",
    "Duplicate budget IDs",
    "Remove duplicate rows",
    removed
)

data["fact_budget"] = df


# ============================================================
# 15. ENERGY DUPLICATES
# ============================================================

df = data["fact_energy"]

before = len(df)

df = df.drop_duplicates(
    subset=["energy_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_energy",
    "Duplicate energy IDs",
    "Remove duplicate rows",
    removed
)

data["fact_energy"] = df


# ============================================================
# 16. EMISSIONS DUPLICATES
# ============================================================

df = data["fact_emissions"]

before = len(df)

df = df.drop_duplicates(
    subset=["emissions_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_emissions",
    "Duplicate emissions IDs",
    "Remove duplicate rows",
    removed
)

data["fact_emissions"] = df


# ============================================================
# 17. WASTE DUPLICATES
# ============================================================

df = data["fact_waste"]

before = len(df)

df = df.drop_duplicates(
    subset=["waste_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_waste",
    "Duplicate waste IDs",
    "Remove duplicate rows",
    removed
)

data["fact_waste"] = df


# ============================================================
# 18. INVENTORY DUPLICATES
# ============================================================

df = data["fact_inventory"]

before = len(df)

df = df.drop_duplicates(
    subset=["inventory_id"],
    keep="first"
)

removed = before - len(df)

add_issue(
    "fact_inventory",
    "Duplicate inventory IDs",
    "Remove duplicate rows",
    removed
)

data["fact_inventory"] = df


# ============================================================
# 19. SALES REVENUE RECONCILIATION
# ============================================================

print("\nChecking sales revenue reconciliation...")

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
# 20. SALES DISCOUNT VALIDATION
# ============================================================

df = data["fact_sales"]

gross_sales = (
    df["quantity"]
    * df["unit_price"]
)

invalid = (
    df["discount_amount"]
    > gross_sales
)

count = invalid.sum()

if count > 0:

    df.loc[
        invalid,
        "discount_amount"
    ] = gross_sales[invalid]

    df.loc[
        invalid,
        "revenue"
    ] = 0

add_issue(
    "fact_sales",
    "Discount greater than gross sales",
    "Cap discount at gross sales and recalculate revenue",
    int(count)
)

data["fact_sales"] = df


# ============================================================
# 21. INVENTORY RECONCILIATION
# ============================================================

print("\nChecking inventory reconciliation...")

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
# 22. INVENTORY NEGATIVE CLOSING
# ============================================================

df = data["fact_inventory"]

invalid = (
    df["closing_quantity"] < 0
)

count = invalid.sum()

if count > 0:

    df = df.loc[
        ~invalid
    ].copy()

    add_issue(
        "fact_inventory",
        "Negative closing inventory",
        "Remove row",
        int(count)
    )

data["fact_inventory"] = df


# ============================================================
# 23. PRODUCTION BUSINESS RULE
# ============================================================

print("\nChecking production business rules...")

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
# 24. PRODUCTION OUTLIERS
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
# 25. FINANCIAL TRANSACTION OUTLIERS
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
# 26. DATE KEY VALIDATION
# ============================================================

print("\nChecking date keys...")

df = data["dim_date"]

expected_date_key = pd.to_datetime(
    df["full_date"]
).dt.strftime(
    "%Y%m%d"
).astype(int)

invalid = (
    df["date_key"]
    != expected_date_key
)

count = invalid.sum()

if count > 0:

    df.loc[
        invalid,
        "date_key"
    ] = expected_date_key[invalid]

    add_issue(
        "dim_date",
        "Date key does not match full date",
        "Recalculate date key",
        int(count)
    )

data["dim_date"] = df


# ============================================================
# 27. FINAL TRUSTED DATA VALIDATION
# ============================================================

print("\n========================================")
print("FINAL TRUSTED DATA VALIDATION")
print("========================================")

print("\nChecking trusted dataset completeness...")

validation_results = []


for dataset in DATASETS:

    df = data[dataset]

    total_nulls = int(
        df.isna().sum().sum()
    )

    expected_nulls = 0

    # Check only the columns explicitly documented
    # as nullable in the Atlas data dictionary.

    if dataset in EXPECTED_NULLABLE_COLUMNS:

        for column in EXPECTED_NULLABLE_COLUMNS[dataset]:

            if column in df.columns:

                expected_nulls += int(
                    df[column].isna().sum()
                )

    unexpected_nulls = (
        total_nulls
        - expected_nulls
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if unexpected_nulls == 0 and duplicate_rows == 0:

        status = "PASS"

    else:

        status = "FAIL"

    validation_results.append({

        "Dataset": dataset,

        "Rows": len(df),

        "Total Nulls": total_nulls,

        "Expected Nulls": expected_nulls,

        "Unexpected Nulls": unexpected_nulls,

        "Duplicate Rows": duplicate_rows,

        "Status": status
    })


validation_df = pd.DataFrame(
    validation_results
)


# ============================================================
# FINAL FOREIGN KEY VALIDATION
# ============================================================

print("\nFinal foreign key validation...")

fk_validation_results = []


for (
    child_dataset,
    child_column,
    parent_dataset,
    parent_column
) in FOREIGN_KEYS:

    child_df = data[child_dataset]

    parent_df = data[parent_dataset]

    valid_values = set(
        parent_df[parent_column]
    )

    invalid = ~child_df[
        child_column
    ].isin(valid_values)

    count = int(
        invalid.sum()
    )

    status = "PASS"

    if count > 0:
        status = "FAIL"

    fk_validation_results.append({
        "Child Dataset": child_dataset,
        "Child Column": child_column,
        "Parent Dataset": parent_dataset,
        "Parent Column": parent_column,
        "Invalid References": count,
        "Status": status
    })


fk_validation_df = pd.DataFrame(
    fk_validation_results
)


# ============================================================
# SAVE TRUSTED DATA
# ============================================================

print("\nSaving trusted data...")

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
# CREATE DATASET SUMMARY
# ============================================================

print("\nGenerating dataset summary...")

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


# ============================================================
# CREATE QUALITY ISSUES DATAFRAME
# ============================================================

if len(issues) > 0:

    issues_df = pd.DataFrame(
        issues
    )

else:

    issues_df = pd.DataFrame(
        columns=[
            "Dataset",
            "Issue",
            "Action",
            "Rows Affected"
        ]
    )


# ============================================================
# SAVE EXCEL QUALITY SUMMARY
# ============================================================

print("\nSaving Excel quality summary...")

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

    fk_validation_df.to_excel(
        writer,
        sheet_name="FK Validation",
        index=False
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n========================================")
print("PHASE 4 DATA QUALITY COMPLETED")
print("========================================")

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
    "\nTrusted validation:"
)

print(
    validation_df.to_string(
        index=False
    )
)


print(
    "\nForeign key validation:"
)

print(
    fk_validation_df.to_string(
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

    print(
        "No quality issues detected."
    )


# ============================================================
# FINAL PASS / FAIL
# ============================================================

validation_failed = (
    validation_df["Status"]
    .eq("FAIL")
    .any()
)

fk_failed = (
    fk_validation_df["Status"]
    .eq("FAIL")
    .any()
)


print(
    "\n========================================"
)

if validation_failed or fk_failed:

    print(
        "PHASE 4 VALIDATION STATUS: FAIL"
    )

else:

    print(
        "PHASE 4 VALIDATION STATUS: PASS"
    )

print(
    "========================================"
)