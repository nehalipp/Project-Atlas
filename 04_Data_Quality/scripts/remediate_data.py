"""
Project Atlas
Phase 4 — Data Remediation

Purpose
-------
Convert intentionally imperfect Phase 3 source data into trusted datasets.

Source:
    03_Data_Generation/data/quality_issues/

Output:
    04_Data_Quality/data/trusted/

Principles
----------
1. Trusted reference dimensions are established first.
2. Invalid dimension records are removed.
3. Deleted reference IDs are propagated to dependent facts.
4. Business relationships are revalidated.
5. Approved fact grain is preserved.
6. Valid outliers are retained for investigation.
7. No new business data is fabricated.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]

SOURCE_DIR = (
    PROJECT_ROOT
    / "03_Data_Generation"
    / "data"
    / "quality_issues"
)

TRUSTED_DIR = (
    PROJECT_ROOT
    / "04_Data_Quality"
    / "data"
    / "trusted"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "04_Data_Quality"
    / "reports"
)

TRUSTED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATASET DEFINITIONS
# ============================================================

REFERENCE_DATASETS = [
    "accounts",
    "customers",
    "suppliers",
    "products",
    "locations",
    "employees",
    "machines",
]

BUSINESS_DATASETS = [
    "sales",
    "production",
    "maintenance",
    "financial_transactions",
    "budget",
    "energy",
    "emissions",
    "waste",
    "inventory",
]

ALL_DATASETS = (
    REFERENCE_DATASETS
    + BUSINESS_DATASETS
)


PRIMARY_KEYS = {
    "accounts": "account_id",
    "customers": "customer_id",
    "suppliers": "supplier_id",
    "products": "product_id",
    "locations": "location_id",
    "employees": "employee_id",
    "machines": "machine_id",
    "sales": "sales_id",
    "production": "production_id",
    "maintenance": "maintenance_id",
    "financial_transactions": "financial_transaction_id",
    "budget": "budget_id",
    "energy": "energy_id",
    "emissions": "emissions_id",
    "waste": "waste_id",
    "inventory": "inventory_id",
}


# ============================================================
# CLI HELPERS
# ============================================================

def header(title):
    print("=" * 70)
    print(f"Project Atlas — {title}")
    print("=" * 70)


def row_status(name, count, label="trusted records"):
    print(
        f"      ✓ {name + '.csv':<35}"
        f"{count:>10,} {label}"
    )


# ============================================================
# FILE HELPERS
# ============================================================

def load_source(name):
    path = SOURCE_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(
            "\nMissing quality-issue dataset:\n"
            f"    {path}\n\n"
            "Run Phase 3 first:\n"
            "    python3 03_Data_Generation/scripts/generate_all_data.py"
        )

    return pd.read_csv(path)


def save_trusted(name, df):
    path = TRUSTED_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def normalize_text(df):
    """
    Remove accidental surrounding whitespace from text fields.
    """
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].map(
            lambda value:
            value.strip()
            if isinstance(value, str)
            else value
        )

    return df


def fill_mode(df, column, fallback="Unknown"):
    """
    Fill missing categorical/text values with the most common
    valid value. If no valid value exists, use a documented
    Unknown placeholder.
    """
    if column not in df.columns:
        return

    mode = df[column].dropna().mode()

    replacement = (
        mode.iloc[0]
        if not mode.empty
        else fallback
    )

    df[column] = df[column].fillna(replacement)


def fill_numeric(df, column, default=0):
    """
    Fill missing numeric values using the column median.
    Falls back to a supplied business-safe default.
    """
    if column not in df.columns:
        return

    numeric = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    median = numeric.dropna().median()

    if pd.isna(median):
        median = default

    df[column] = numeric.fillna(median)


def convert_dates(df, column):
    """
    Standardize date fields.
    """
    if column not in df.columns:
        return

    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
    )


# ============================================================
# REFERENCE DATA REMEDIATION
# ============================================================

def clean_reference_dimensions(source):
    """
    Establish trusted reference dimensions in dependency order.
    """

    trusted = {}
    summary = []

    # --------------------------------------------------------
    # Accounts
    # --------------------------------------------------------

    df = normalize_text(source["accounts"].copy())

    before = len(df)

    df = df.dropna(subset=["account_id"])
    df = df.drop_duplicates(
        subset=["account_id"],
        keep="first",
    )

    for column in [
        "account_name",
        "account_type",
        "industry",
        "country",
        "status",
    ]:
        fill_mode(df, column)

    trusted["accounts"] = df

    summary.append(
        ["accounts", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Suppliers
    # --------------------------------------------------------

    df = normalize_text(source["suppliers"].copy())

    before = len(df)

    df = df.dropna(subset=["supplier_id"])
    df = df.drop_duplicates(
        subset=["supplier_id"],
        keep="first",
    )

    for column in [
        "supplier_name",
        "supplier_category",
        "country",
        "status",
    ]:
        fill_mode(df, column)

    trusted["suppliers"] = df

    summary.append(
        ["suppliers", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Locations
    # --------------------------------------------------------

    df = normalize_text(source["locations"].copy())

    before = len(df)

    df = df.dropna(subset=["location_id"])
    df = df.drop_duplicates(
        subset=["location_id"],
        keep="first",
    )

    for column in [
        "location_name",
        "location_type",
        "city",
        "state_region",
        "country",
        "status",
    ]:
        fill_mode(df, column)

    trusted["locations"] = df

    summary.append(
        ["locations", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Products
    # --------------------------------------------------------

    df = normalize_text(source["products"].copy())

    before = len(df)

    df = df.dropna(
        subset=[
            "product_id",
            "supplier_id",
        ]
    )

    valid_suppliers = set(
        trusted["suppliers"]["supplier_id"]
    )

    df = df[
        df["supplier_id"].isin(valid_suppliers)
    ]

    df = df.drop_duplicates(
        subset=["product_id"],
        keep="first",
    )

    for column in [
        "product_name",
        "category",
        "status",
    ]:
        fill_mode(df, column)

    fill_numeric(df, "unit_cost", 0)
    fill_numeric(df, "unit_price", 0)

    # Product prices must be positive and logically ordered.
    df["unit_cost"] = df["unit_cost"].abs()
    df["unit_price"] = df["unit_price"].abs()

    invalid_price = (
        df["unit_price"] < df["unit_cost"]
    )

    df.loc[
        invalid_price,
        "unit_price",
    ] = df.loc[
        invalid_price,
        "unit_cost",
    ]

    trusted["products"] = df

    summary.append(
        ["products", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Employees
    # --------------------------------------------------------

    df = normalize_text(source["employees"].copy())

    before = len(df)

    df = df.dropna(
        subset=[
            "employee_id",
            "location_id",
        ]
    )

    valid_locations = set(
        trusted["locations"]["location_id"]
    )

    df = df[
        df["location_id"].isin(valid_locations)
    ]

    df = df.drop_duplicates(
        subset=["employee_id"],
        keep="first",
    )

    fill_mode(df, "employee_name")
    fill_mode(df, "department")
    fill_mode(df, "role")
    fill_mode(df, "status")

    convert_dates(df, "hire_date")

    # A missing hire date cannot support temporal validation.
    df = df.dropna(subset=["hire_date"])

    trusted["employees"] = df

    summary.append(
        ["employees", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Machines
    # --------------------------------------------------------

    df = normalize_text(source["machines"].copy())

    before = len(df)

    df = df.dropna(
        subset=[
            "machine_id",
            "location_id",
        ]
    )

    df = df[
        df["location_id"].isin(valid_locations)
    ]

    df = df.drop_duplicates(
        subset=["machine_id"],
        keep="first",
    )

    fill_mode(df, "machine_name")
    fill_mode(df, "machine_type")
    fill_mode(df, "status")

    convert_dates(
        df,
        "installation_date",
    )

    df = df.dropna(
        subset=["installation_date"]
    )

    trusted["machines"] = df

    summary.append(
        ["machines", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    df = normalize_text(source["customers"].copy())

    before = len(df)

    df = df.dropna(
        subset=[
            "customer_id",
            "account_id",
        ]
    )

    valid_accounts = set(
        trusted["accounts"]["account_id"]
    )

    df = df[
        df["account_id"].isin(valid_accounts)
    ]

    df = df.drop_duplicates(
        subset=["customer_id"],
        keep="first",
    )

    for column in [
        "customer_name",
        "customer_segment",
        "industry",
        "country",
        "status",
    ]:
        fill_mode(df, column)

    trusted["customers"] = df

    summary.append(
        ["customers", before, len(df), before - len(df)]
    )

    return trusted, summary


# ============================================================
# FACT FILTERING HELPERS
# ============================================================

def valid_ids(df, column, reference):
    """
    Keep rows whose foreign key exists in the trusted dimension.
    """
    if column not in df.columns:
        return df

    valid = set(reference)

    return df[
        df[column].isin(valid)
    ].copy()


def remove_duplicate_key(df, key):
    if key not in df.columns:
        return df

    return df.drop_duplicates(
        subset=[key],
        keep="first",
    ).copy()


# ============================================================
# SALES
# ============================================================

def remediate_sales(df, ref):

    df = normalize_text(df)

    df = remove_duplicate_key(
        df,
        "sales_id",
    )

    df = df.dropna(
        subset=[
            "sales_id",
            "account_id",
            "customer_id",
            "product_id",
            "location_id",
            "date",
        ]
    )

    df = valid_ids(
        df,
        "account_id",
        ref["accounts"]["account_id"],
    )

    df = valid_ids(
        df,
        "customer_id",
        ref["customers"]["customer_id"],
    )

    df = valid_ids(
        df,
        "product_id",
        ref["products"]["product_id"],
    )

    df = valid_ids(
        df,
        "location_id",
        ref["locations"]["location_id"],
    )

    convert_dates(df, "date")

    df = df.dropna(subset=["date"])

    fill_numeric(df, "quantity", 1)
    fill_numeric(df, "unit_price", 0)
    fill_numeric(df, "discount_rate", 0)

    df["quantity"] = df["quantity"].abs()
    df["unit_price"] = df["unit_price"].abs()
    df["discount_rate"] = df["discount_rate"].clip(0, 1)

    # Account must match the customer's trusted account.
    customer_account = (
        ref["customers"]
        .set_index("customer_id")["account_id"]
    )

    expected_account = (
        df["customer_id"].map(customer_account)
    )

    df = df[
        df["account_id"].eq(expected_account)
    ].copy()

    # Recalculate trusted revenue from trusted inputs.
    df["revenue"] = np.round(
        (
            df["quantity"]
            * df["unit_price"]
        )
        * (
            1
            - df["discount_rate"]
        ),
        2,
    )

    return df


# ============================================================
# PRODUCTION
# ============================================================

def remediate_production(df, ref):

    df = normalize_text(df)

    df = remove_duplicate_key(
        df,
        "production_id",
    )

    df = df.dropna(
        subset=[
            "production_id",
            "date",
            "product_id",
            "location_id",
            "machine_id",
            "employee_id",
        ]
    )

    for column, dimension in [
        ("product_id", "products"),
        ("location_id", "locations"),
        ("machine_id", "machines"),
        ("employee_id", "employees"),
    ]:
        df = valid_ids(
            df,
            column,
            ref[dimension][
                PRIMARY_KEYS[dimension]
            ],
        )

    convert_dates(df, "date")
    df = df.dropna(subset=["date"])

    fill_numeric(df, "planned_quantity", 1)
    fill_numeric(df, "quantity_produced", 0)
    fill_numeric(df, "production_hours", 0)

    fill_mode(
        df,
        "production_status",
        "Completed",
    )

    df["planned_quantity"] = (
        df["planned_quantity"].abs()
    )

    df["quantity_produced"] = (
        df["quantity_produced"].clip(lower=0)
    )

    df["production_hours"] = (
        df["production_hours"].clip(lower=0)
    )

    # Machine and employee must belong to the recorded location.
    machine_location = (
        ref["machines"]
        .set_index("machine_id")["location_id"]
    )

    employee_location = (
        ref["employees"]
        .set_index("employee_id")["location_id"]
    )

    df = df[
        df["location_id"].eq(
            df["machine_id"].map(machine_location)
        )
        &
        df["location_id"].eq(
            df["employee_id"].map(employee_location)
        )
    ].copy()

    # Activity cannot precede installation/hire.
    machine_date = (
        ref["machines"]
        .set_index("machine_id")["installation_date"]
    )

    employee_date = (
        ref["employees"]
        .set_index("employee_id")["hire_date"]
    )

    machine_date = pd.to_datetime(
        df["machine_id"].map(machine_date)
    )

    employee_date = pd.to_datetime(
        df["employee_id"].map(employee_date)
    )

    df = df[
        (df["date"] >= machine_date)
        &
        (df["date"] >= employee_date)
    ].copy()

    return df


# ============================================================
# MAINTENANCE
# ============================================================

def remediate_maintenance(df, ref):

    df = normalize_text(df)

    df = remove_duplicate_key(
        df,
        "maintenance_id",
    )

    df = df.dropna(
        subset=[
            "maintenance_id",
            "date",
            "location_id",
            "machine_id",
            "employee_id",
        ]
    )

    for column, dimension in [
        ("location_id", "locations"),
        ("machine_id", "machines"),
        ("employee_id", "employees"),
    ]:
        df = valid_ids(
            df,
            column,
            ref[dimension][
                PRIMARY_KEYS[dimension]
            ],
        )

    convert_dates(df, "date")
    df = df.dropna(subset=["date"])

    fill_mode(
        df,
        "maintenance_type",
        "Inspection",
    )

    fill_numeric(df, "downtime_hours", 0)
    fill_numeric(df, "maintenance_cost", 0)

    df["downtime_hours"] = (
        df["downtime_hours"].clip(lower=0)
    )

    df["maintenance_cost"] = (
        df["maintenance_cost"].clip(lower=0)
    )

    machine_location = (
        ref["machines"]
        .set_index("machine_id")["location_id"]
    )

    employee_location = (
        ref["employees"]
        .set_index("employee_id")["location_id"]
    )

    df = df[
        df["location_id"].eq(
            df["machine_id"].map(machine_location)
        )
        &
        df["location_id"].eq(
            df["employee_id"].map(employee_location)
        )
    ].copy()

    machine_date = (
        ref["machines"]
        .set_index("machine_id")["installation_date"]
    )

    employee_date = (
        ref["employees"]
        .set_index("employee_id")["hire_date"]
    )

    machine_date = pd.to_datetime(
        df["machine_id"].map(machine_date)
    )

    employee_date = pd.to_datetime(
        df["employee_id"].map(employee_date)
    )

    df = df[
        (df["date"] >= machine_date)
        &
        (df["date"] >= employee_date)
    ].copy()

    return df


# ============================================================
# GENERIC LOCATION FACTS
# ============================================================

def remediate_location_fact(
    df,
    ref,
    id_column,
    numeric_columns,
    categorical_columns,
):

    df = normalize_text(df)

    df = remove_duplicate_key(
        df,
        id_column,
    )

    required = [
        id_column,
        "date",
        "location_id",
    ]

    df = df.dropna(
        subset=required
    )

    df = valid_ids(
        df,
        "location_id",
        ref["locations"]["location_id"],
    )

    convert_dates(df, "date")

    df = df.dropna(
        subset=["date"]
    )

    for column in numeric_columns:
        fill_numeric(df, column, 0)

        # Operational measurements cannot be negative.
        df[column] = df[column].clip(
            lower=0
        )

    for column in categorical_columns:
        fill_mode(df, column)

    return df


# ============================================================
# INVENTORY
# ============================================================

def remediate_inventory(df, ref):

    df = normalize_text(df)

    df = remove_duplicate_key(
        df,
        "inventory_id",
    )

    df = df.dropna(
        subset=[
            "inventory_id",
            "date",
            "product_id",
            "location_id",
        ]
    )

    df = valid_ids(
        df,
        "product_id",
        ref["products"]["product_id"],
    )

    df = valid_ids(
        df,
        "location_id",
        ref["locations"]["location_id"],
    )

    convert_dates(df, "date")

    df = df.dropna(subset=["date"])

    fill_numeric(
        df,
        "quantity_on_hand",
        0,
    )

    fill_numeric(
        df,
        "reorder_point",
        0,
    )

    fill_numeric(
        df,
        "inventory_value",
        0,
    )

    df["quantity_on_hand"] = (
        df["quantity_on_hand"].clip(lower=0)
    )

    df["reorder_point"] = (
        df["reorder_point"].clip(lower=0)
    )

    df["inventory_value"] = (
        df["inventory_value"].clip(lower=0)
    )

    # Approved inventory grain:
    # Date + Product + Location.
    #
    # If duplicate grain exists, keep the first trusted
    # snapshot rather than aggregating potentially corrupted
    # records.
    df = df.drop_duplicates(
        subset=[
            "date",
            "product_id",
            "location_id",
        ],
        keep="first",
    )

    return df


# ============================================================
# FACT REMEDIATION
# ============================================================

def clean_business_facts(source, ref):

    trusted = {}
    summary = []

    # --------------------------------------------------------
    # Sales
    # --------------------------------------------------------

    before = len(source["sales"])

    df = remediate_sales(
        source["sales"].copy(),
        ref,
    )

    trusted["sales"] = df

    summary.append(
        ["sales", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Production
    # --------------------------------------------------------

    before = len(source["production"])

    df = remediate_production(
        source["production"].copy(),
        ref,
    )

    trusted["production"] = df

    summary.append(
        ["production", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    before = len(source["maintenance"])

    df = remediate_maintenance(
        source["maintenance"].copy(),
        ref,
    )

    trusted["maintenance"] = df

    summary.append(
        ["maintenance", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Financial Transactions
    # --------------------------------------------------------

    before = len(source["financial_transactions"])

    df = remediate_location_fact(
        source["financial_transactions"].copy(),
        ref,
        "financial_transaction_id",
        ["amount"],
        ["transaction_type", "description"],
    )

    trusted["financial_transactions"] = df

    summary.append(
        [
            "financial_transactions",
            before,
            len(df),
            before - len(df),
        ]
    )

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    before = len(source["budget"])

    df = remediate_location_fact(
        source["budget"].copy(),
        ref,
        "budget_id",
        ["budget_amount"],
        ["category"],
    )

    trusted["budget"] = df

    summary.append(
        ["budget", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Energy
    # --------------------------------------------------------

    before = len(source["energy"])

    df = remediate_location_fact(
        source["energy"].copy(),
        ref,
        "energy_id",
        ["consumption"],
        ["energy_type", "unit"],
    )

    trusted["energy"] = df

    summary.append(
        ["energy", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Emissions
    # --------------------------------------------------------

    before = len(source["emissions"])

    df = remediate_location_fact(
        source["emissions"].copy(),
        ref,
        "emissions_id",
        ["co2_kg"],
        ["source"],
    )

    trusted["emissions"] = df

    summary.append(
        ["emissions", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Waste
    # --------------------------------------------------------

    before = len(source["waste"])

    df = remediate_location_fact(
        source["waste"].copy(),
        ref,
        "waste_id",
        ["quantity"],
        ["waste_type", "unit", "disposal_method"],
    )

    trusted["waste"] = df

    summary.append(
        ["waste", before, len(df), before - len(df)]
    )

    # --------------------------------------------------------
    # Inventory
    # --------------------------------------------------------

    before = len(source["inventory"])

    df = remediate_inventory(
        source["inventory"].copy(),
        ref,
    )

    trusted["inventory"] = df

    summary.append(
        ["inventory", before, len(df), before - len(df)]
    )

    return trusted, summary


# ============================================================
# STRICT INTERNAL TRUST CHECK
# ============================================================

def validate_trusted_relationships(
    references,
    facts,
):
    """
    Final remediation-side gate.

    validate_trusted_data.py remains the authoritative strict
    Phase 4 validation script. This check prevents obviously
    invalid trusted output from being written unnoticed.
    """

    accounts = set(
        references["accounts"]["account_id"]
    )

    customers = references["customers"]

    customer_ids = set(
        customers["customer_id"]
    )

    suppliers = set(
        references["suppliers"]["supplier_id"]
    )

    products = references["products"]

    product_ids = set(
        products["product_id"]
    )

    locations = set(
        references["locations"]["location_id"]
    )

    employees = references["employees"]
    employee_ids = set(
        employees["employee_id"]
    )

    machines = references["machines"]
    machine_ids = set(
        machines["machine_id"]
    )

    # --------------------------------------------------------
    # Customer → Account
    # --------------------------------------------------------

    if not customers["account_id"].isin(accounts).all():
        raise ValueError(
            "Trusted Customer → Account relationship failed."
        )

    # --------------------------------------------------------
    # Product → Supplier
    # --------------------------------------------------------

    if not products["supplier_id"].isin(suppliers).all():
        raise ValueError(
            "Trusted Product → Supplier relationship failed."
        )

    # --------------------------------------------------------
    # Employee → Location
    # --------------------------------------------------------

    if not employees["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Employee → Location relationship failed."
        )

    # --------------------------------------------------------
    # Machine → Location
    # --------------------------------------------------------

    if not machines["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Machine → Location relationship failed."
        )

    # --------------------------------------------------------
    # Sales
    # --------------------------------------------------------

    sales = facts["sales"]

    if not sales["account_id"].isin(accounts).all():
        raise ValueError(
            "Trusted Sales → Account relationship failed."
        )

    if not sales["customer_id"].isin(customer_ids).all():
        raise ValueError(
            "Trusted Sales → Customer relationship failed."
        )

    if not sales["product_id"].isin(product_ids).all():
        raise ValueError(
            "Trusted Sales → Product relationship failed."
        )

    if not sales["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Sales → Location relationship failed."
        )

    customer_account = (
        customers
        .set_index("customer_id")["account_id"]
    )

    expected_accounts = (
        sales["customer_id"].map(customer_account)
    )

    if not sales["account_id"].eq(
        expected_accounts
    ).all():

        raise ValueError(
            "Trusted Sales Account → Customer consistency failed."
        )

    # --------------------------------------------------------
    # Production
    # --------------------------------------------------------

    production = facts["production"]

    if not production["product_id"].isin(product_ids).all():
        raise ValueError(
            "Trusted Production → Product failed."
        )

    if not production["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Production → Location failed."
        )

    if not production["machine_id"].isin(machine_ids).all():
        raise ValueError(
            "Trusted Production → Machine failed."
        )

    if not production["employee_id"].isin(employee_ids).all():
        raise ValueError(
            "Trusted Production → Employee failed."
        )

    machine_location = (
        machines
        .set_index("machine_id")["location_id"]
    )

    employee_location = (
        employees
        .set_index("employee_id")["location_id"]
    )

    if not production["location_id"].eq(
        production["machine_id"].map(machine_location)
    ).all():

        raise ValueError(
            "Trusted Production machine/location consistency failed."
        )

    if not production["location_id"].eq(
        production["employee_id"].map(employee_location)
    ).all():

        raise ValueError(
            "Trusted Production employee/location consistency failed."
        )

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    maintenance = facts["maintenance"]

    if not maintenance["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Maintenance → Location failed."
        )

    if not maintenance["machine_id"].isin(machine_ids).all():
        raise ValueError(
            "Trusted Maintenance → Machine failed."
        )

    if not maintenance["employee_id"].isin(employee_ids).all():
        raise ValueError(
            "Trusted Maintenance → Employee failed."
        )

    if not maintenance["location_id"].eq(
        maintenance["machine_id"].map(machine_location)
    ).all():

        raise ValueError(
            "Trusted Maintenance machine/location consistency failed."
        )

    if not maintenance["location_id"].eq(
        maintenance["employee_id"].map(employee_location)
    ).all():

        raise ValueError(
            "Trusted Maintenance employee/location consistency failed."
        )

    # --------------------------------------------------------
    # Location-based facts
    # --------------------------------------------------------

    for name in [
        "financial_transactions",
        "budget",
        "energy",
        "emissions",
        "waste",
    ]:
        df = facts[name]

        if not df["location_id"].isin(locations).all():
            raise ValueError(
                f"Trusted {name} → Location relationship failed."
            )

    # --------------------------------------------------------
    # Inventory
    # --------------------------------------------------------

    inventory = facts["inventory"]

    if not inventory["product_id"].isin(product_ids).all():
        raise ValueError(
            "Trusted Inventory → Product failed."
        )

    if not inventory["location_id"].isin(locations).all():
        raise ValueError(
            "Trusted Inventory → Location failed."
        )

    if inventory.duplicated(
        subset=[
            "date",
            "product_id",
            "location_id",
        ]
    ).any():

        raise ValueError(
            "Trusted Inventory grain violation."
        )

    # --------------------------------------------------------
    # Null gate
    # --------------------------------------------------------

    for name, df in {
        **references,
        **facts,
    }.items():

        if df.isna().any().any():
            columns = (
                df.columns[
                    df.isna().any()
                ].tolist()
            )

            raise ValueError(
                f"Trusted {name} contains missing values: "
                f"{columns}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    header("Phase 4 Data Remediation")

    print("\nSource:")
    print(f"  {SOURCE_DIR}")

    print("\nTrusted output:")
    print(f"  {TRUSTED_DIR}")

    print("\nLoading quality-issue datasets...")

    source = {}

    for name in ALL_DATASETS:
        source[name] = load_source(name)

    print(
        f"      ✓ {len(source)} datasets loaded"
    )

    # --------------------------------------------------------
    # Reference dimensions
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ESTABLISHING TRUSTED REFERENCE DIMENSIONS")
    print("-" * 70)

    references, reference_summary = (
        clean_reference_dimensions(source)
    )

    for name in REFERENCE_DATASETS:
        row_status(
            name,
            len(references[name]),
        )

    # --------------------------------------------------------
    # Business facts
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("REMEDIATING BUSINESS DATA")
    print("-" * 70)

    facts, fact_summary = clean_business_facts(
        source,
        references,
    )

    for name in BUSINESS_DATASETS:
        row_status(
            name,
            len(facts[name]),
        )

    # --------------------------------------------------------
    # Final remediation-side relationship gate
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("RUNNING TRUSTED RELATIONSHIP CHECKS")
    print("-" * 70)

    validate_trusted_relationships(
        references,
        facts,
    )

    print("      ✓ Account → Customer → Sales")
    print("      ✓ Product → Supplier")
    print("      ✓ Location → Employee")
    print("      ✓ Location → Machine")
    print("      ✓ Production relationships")
    print("      ✓ Maintenance relationships")
    print("      ✓ Inventory grain")
    print("      ✓ No missing values")

    # --------------------------------------------------------
    # Save trusted data
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("SAVING TRUSTED DATASETS")
    print("-" * 70)

    for name in REFERENCE_DATASETS:
        save_trusted(
            name,
            references[name],
        )

    for name in BUSINESS_DATASETS:
        save_trusted(
            name,
            facts[name],
        )

    # --------------------------------------------------------
    # Remediation summary
    # --------------------------------------------------------

    all_summary = (
        reference_summary
        + fact_summary
    )

    summary_df = pd.DataFrame(
        all_summary,
        columns=[
            "dataset",
            "source_records",
            "trusted_records",
            "records_removed",
        ],
    )

    summary_path = (
        REPORT_DIR
        / "remediation_summary.csv"
    )

    summary_df.to_csv(
        summary_path,
        index=False,
    )

    source_total = (
        summary_df["source_records"].sum()
    )

    trusted_total = (
        summary_df["trusted_records"].sum()
    )

    removed_total = (
        summary_df["records_removed"].sum()
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("REMEDIATION SUMMARY")
    print("-" * 70)

    print(
        f"{'Datasets processed':<35}: "
        f"{len(summary_df)}"
    )

    print(
        f"{'Source records':<35}: "
        f"{source_total:,}"
    )

    print(
        f"{'Trusted records':<35}: "
        f"{trusted_total:,}"
    )

    print(
        f"{'Records removed':<35}: "
        f"{removed_total:,}"
    )

    print(
        f"{'Trusted output':<35}: "
        f"{TRUSTED_DIR}"
    )

    print(
        f"{'Report':<35}: "
        f"{summary_path}"
    )

    print(
        "\nNote: Valid outliers are retained for investigation."
    )

    print("\n" + "=" * 70)
    print("DATA REMEDIATION COMPLETE")
    print("=" * 70)

    print(
        "\nTrusted data is ready for strict validation."
    )


if __name__ == "__main__":
    main()