"""
Project Atlas
Phase 3 — Controlled Data Quality Issue Injection

Adds deliberate, reproducible data-quality issues to all
16 raw datasets.

Quality dimensions injected:
    1. Missing values
       - True NaN values
       - Hidden missing-value placeholders
    2. Exact duplicates
    3. Partial duplicates
    4. Structural inconsistencies
    5. Incorrect data types
    6. Outliers and anomalous values
    7. Invalid references
    8. Business-rule violations
    9. Leading/trailing whitespace
   10. Mixed date formats

IMPORTANT:
    This script must be run AFTER clean Phase 3 validation passes.

Workflow:

    Clean data generation
            ↓
    Clean baseline validation
            ↓
    inject_quality_issues.py
            ↓
    Intentionally imperfect raw data
            ↓
    Phase 4 — Data Quality
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    DUPLICATE_RATE,
    INVALID_REFERENCE_RATE,
    INVALID_VALUE_RATE,
    MISSING_RATE,
    OUTLIER_RATE,
    RAW_DATA_DIR,
    SEED,
)


rng = np.random.default_rng(SEED)


# ============================================================
# HELPERS
# ============================================================

def load(filename):
    """Load a raw dataset."""

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return pd.read_csv(path)


def save(df, filename):
    """Save the intentionally imperfect dataset."""

    path = RAW_DATA_DIR / filename
    df.to_csv(path, index=False)


def choose_rows(df, rate):
    """Return deterministic random row indexes."""

    count = max(
        1,
        int(len(df) * rate),
    )

    count = min(count, len(df))

    return rng.choice(
        df.index.to_numpy(),
        count,
        replace=False,
    )


def percentage_count(df, rate):
    """Calculate a minimum row count from a percentage."""

    return max(
        1,
        int(len(df) * rate),
    )


def add_exact_duplicates(df, rate):
    """
    Add identical row repeats.

    The original records and their duplicate copies are
    completely identical.
    """

    count = percentage_count(df, rate)

    duplicates = df.sample(
        n=count,
        random_state=SEED,
    ).copy()

    return pd.concat(
        [df, duplicates],
        ignore_index=True,
    )


def add_partial_duplicates(
    df,
    rate,
    key_column,
    modified_column,
    modification_type="text",
):
    """
    Add partial duplicates.

    The business/entity key remains the same, while one
    descriptive or temporal attribute is slightly changed.
    """

    count = percentage_count(df, rate)

    sample = df.sample(
        n=count,
        random_state=SEED + 1,
    ).copy()

    if modification_type == "text":

        sample[modified_column] = (
            sample[modified_column]
            .fillna("Unknown")
            .astype(str)
            + " - Updated"
        )

    elif modification_type == "whitespace":

        sample[modified_column] = (
            sample[modified_column]
            .fillna("")
            .astype(str)
            + " "
        )

    elif modification_type == "date":

        dates = pd.to_datetime(
            sample[modified_column],
            errors="coerce",
        )

        sample[modified_column] = (
            dates + pd.Timedelta(days=1)
        ).dt.strftime("%Y-%m-%d")

    else:
        raise ValueError(
            f"Unsupported modification_type: {modification_type}"
        )

    return pd.concat(
        [df, sample],
        ignore_index=True,
    )


def inject_nan(df, column, rate=MISSING_RATE):
    """Inject genuine NaN values."""

    rows = choose_rows(df, rate)

    df.loc[rows, column] = np.nan

    return len(rows)


def inject_placeholder(
    df,
    column,
    placeholder="unknown",
    rate=MISSING_RATE,
):
    """
    Inject hidden missing-value placeholders.

    Examples:
        unknown
        n/a
        999
    """

    rows = choose_rows(df, rate)

    df.loc[rows, column] = placeholder

    return len(rows)


def inject_whitespace(
    df,
    column,
    rate=INVALID_VALUE_RATE,
):
    """Inject leading/trailing whitespace."""

    rows = choose_rows(df, rate)

    df.loc[rows, column] = (
        " "
        + df.loc[rows, column]
        .fillna("")
        .astype(str)
        + " "
    )

    return len(rows)


def inject_numeric_as_text(
    df,
    column,
    rate=INVALID_VALUE_RATE,
):
    """
    Store numeric values as strings.

    This intentionally changes the column's effective
    datatype after the CSV is reloaded.
    """

    rows = choose_rows(df, rate)

    df.loc[rows, column] = (
        df.loc[rows, column]
        .astype(str)
    )

    return len(rows)


def inject_mixed_dates(
    df,
    column,
    rate=INVALID_VALUE_RATE,
):
    """
    Mix date formats within a single column.

    Formats introduced:
        MM/DD/YYYY
        DD-MM-YYYY
    """

    rows = choose_rows(df, rate)

    dates = pd.to_datetime(
        df.loc[rows, column],
        errors="coerce",
    )

    for position, index in enumerate(rows):

        if pd.isna(dates.loc[index]):
            continue

        if position % 2 == 0:
            df.loc[index, column] = (
                dates.loc[index]
                .strftime("%m/%d/%Y")
            )
        else:
            df.loc[index, column] = (
                dates.loc[index]
                .strftime("%d-%m-%Y")
            )

    return len(rows)


def inject_outlier(
    df,
    column,
    multiplier=100,
    rate=OUTLIER_RATE,
):
    """Inject extreme numeric outliers."""

    rows = choose_rows(df, rate)

    df.loc[rows, column] = (
        pd.to_numeric(
            df.loc[rows, column],
            errors="coerce",
        )
        * multiplier
    )

    return len(rows)


def inject_invalid_reference(
    df,
    column,
    prefix,
    rate=INVALID_REFERENCE_RATE,
):
    """
    Replace valid foreign keys with IDs that do not exist
    in the corresponding reference table.
    """

    rows = choose_rows(df, rate)

    df.loc[rows, column] = [
        f"{prefix}-INVALID-{i:05d}"
        for i in range(len(rows))
    ]

    return len(rows)


def print_summary(
    filename,
    messages,
):
    """Print a concise injection summary."""

    print(f"\n{filename}")

    for message in messages:
        print(f"  - {message}")


# ============================================================
# ACCOUNTS
# ============================================================

def inject_accounts():

    df = load("accounts.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'industry'):,} blank industry values"
    )

    messages.append(
        f"{inject_placeholder(df, 'country', 'unknown'):,} "
        "hidden missing country values"
    )

    messages.append(
        f"{inject_whitespace(df, 'account_name'):,} "
        "account names with whitespace"
    )

    messages.append(
        f"{inject_placeholder(df, 'account_type', 'n/a'):,} "
        "placeholder account types"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "country"] = rng.choice(
        ["NY", "New York", "ny"],
        len(rows),
    )

    messages.append(
        f"{len(rows):,} structurally inconsistent country values"
    )

    # Exact duplicates
    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    # Partial duplicates
    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "account_id",
        "account_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate accounts"
    )

    save(df, "accounts.csv")
    print_summary("accounts.csv", messages)


# ============================================================
# CUSTOMERS
# ============================================================

def inject_customers():

    df = load("customers.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'customer_segment'):,} blank segments"
    )

    messages.append(
        f"{inject_placeholder(df, 'industry', 'unknown'):,} "
        "hidden missing industries"
    )

    messages.append(
        f"{inject_whitespace(df, 'customer_name'):,} "
        "customer names with whitespace"
    )

    # Invalid account references
    messages.append(
        f"{inject_invalid_reference(df, 'account_id', 'ACC'):,} "
        "invalid account references"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "country"] = rng.choice(
        ["NY", "New York", "ny"],
        len(rows),
    )

    messages.append(
        f"{len(rows):,} inconsistent country representations"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "customer_id",
        "customer_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate customers"
    )

    save(df, "customers.csv")
    print_summary("customers.csv", messages)


# ============================================================
# SUPPLIERS
# ============================================================

def inject_suppliers():

    df = load("suppliers.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'supplier_category'):,} "
        "blank supplier categories"
    )

    messages.append(
        f"{inject_placeholder(df, 'country', 'n/a'):,} "
        "hidden missing countries"
    )

    messages.append(
        f"{inject_whitespace(df, 'supplier_name'):,} "
        "supplier names with whitespace"
    )

    # Structural category inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "supplier_category"] = (
        df.loc[rows, "supplier_category"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent category formats"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "supplier_id",
        "supplier_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate suppliers"
    )

    save(df, "suppliers.csv")
    print_summary("suppliers.csv", messages)


# ============================================================
# PRODUCTS
# ============================================================

def inject_products():

    df = load("products.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'category'):,} blank categories"
    )

    messages.append(
        f"{inject_placeholder(df, 'supplier_id', 'SUP-UNKNOWN'):,} "
        "hidden missing supplier references"
    )

    # Invalid supplier references
    messages.append(
        f"{inject_invalid_reference(df, 'supplier_id', 'SUP'):,} "
        "invalid supplier references"
    )

    # Negative prices / costs
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "unit_price"] *= -1

    messages.append(
        f"{len(rows):,} negative product prices"
    )

    # Outlier costs
    rows = choose_rows(df, OUTLIER_RATE)

    df.loc[rows, "unit_cost"] *= 100

    messages.append(
        f"{len(rows):,} extreme product-cost outliers"
    )

    # Price below cost
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "unit_price"] = (
        df.loc[rows, "unit_cost"] * 0.25
    ).round(2)

    messages.append(
        f"{len(rows):,} products with price below cost"
    )

    messages.append(
        f"{inject_whitespace(df, 'product_name'):,} "
        "product names with whitespace"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'unit_price'):,} "
        "unit prices represented as text"
    )

    # Category casing
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "category"] = (
        df.loc[rows, "category"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent category values"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "product_id",
        "product_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate products"
    )

    save(df, "products.csv")
    print_summary("products.csv", messages)


# ============================================================
# LOCATIONS
# ============================================================

def inject_locations():

    df = load("locations.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'state_region'):,} blank regions"
    )

    messages.append(
        f"{inject_placeholder(df, 'city', 'unknown'):,} "
        "hidden missing cities"
    )

    messages.append(
        f"{inject_whitespace(df, 'location_name'):,} "
        "location names with whitespace"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "state_region"] = rng.choice(
        ["NY", "New York", "ny"],
        len(rows),
    )

    messages.append(
        f"{len(rows):,} inconsistent region representations"
    )

    # Partial duplicates with changed city
    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "location_id",
        "location_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate locations"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    save(df, "locations.csv")
    print_summary("locations.csv", messages)


# ============================================================
# EMPLOYEES
# ============================================================

def inject_employees():

    df = load("employees.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'department'):,} blank departments"
    )

    messages.append(
        f"{inject_placeholder(df, 'role', 'unknown'):,} "
        "hidden missing roles"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'location_id', 'LOC'):,} "
        "invalid location references"
    )

    messages.append(
        f"{inject_whitespace(df, 'employee_name'):,} "
        "employee names with whitespace"
    )

    # Mixed date formats
    messages.append(
        f"{inject_mixed_dates(df, 'hire_date'):,} "
        "mixed hire-date formats"
    )

    # Implausible future hire date
    rows = choose_rows(df, OUTLIER_RATE)

    df.loc[rows, "hire_date"] = "01/01/2100"

    messages.append(
        f"{len(rows):,} implausible future hire dates"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "department"] = (
        df.loc[rows, "department"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent department formats"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "employee_id",
        "employee_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate employees"
    )

    save(df, "employees.csv")
    print_summary("employees.csv", messages)


# ============================================================
# MACHINES
# ============================================================

def inject_machines():

    df = load("machines.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'machine_type'):,} blank machine types"
    )

    messages.append(
        f"{inject_placeholder(df, 'status', 'unknown'):,} "
        "hidden missing statuses"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'location_id', 'LOC'):,} "
        "invalid location references"
    )

    messages.append(
        f"{inject_whitespace(df, 'machine_name'):,} "
        "machine names with whitespace"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'installation_date'):,} "
        "mixed installation-date formats"
    )

    # Structural machine type inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "machine_type"] = (
        df.loc[rows, "machine_type"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent machine-type formats"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "machine_id",
        "machine_name",
        "text",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate machines"
    )

    save(df, "machines.csv")
    print_summary("machines.csv", messages)


# ============================================================
# SALES
# ============================================================

def inject_sales():

    df = load("sales.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'product_id'):,} blank product references"
    )

    messages.append(
        f"{inject_placeholder(df, 'customer_id', 'unknown'):,} "
        "hidden missing customer references"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'product_id', 'PROD'):,} "
        "invalid product references"
    )

    # Negative quantities
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "quantity"] *= -1

    messages.append(
        f"{len(rows):,} negative quantities"
    )

    # Revenue mismatch
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "revenue"] = (
        df.loc[rows, "revenue"] * 1.10
    ).round(2)

    messages.append(
        f"{len(rows):,} revenue mismatches"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'quantity'):,} "
        "quantities represented as text"
    )

    # Outlier unit prices
    messages.append(
        f"{inject_outlier(df, 'unit_price'):,} "
        "unit-price outliers"
    )

    # Whitespace
    messages.append(
        f"{inject_whitespace(df, 'transaction_id'):,} "
        "transaction IDs with whitespace"
    )

    # Mixed dates
    messages.append(
        f"{inject_mixed_dates(df, 'transaction_date'):,} "
        "mixed transaction-date formats"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "transaction_id",
        "transaction_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate transactions"
    )

    save(df, "sales.csv")
    print_summary("sales.csv", messages)


# ============================================================
# PRODUCTION
# ============================================================

def inject_production():

    df = load("production.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'employee_id'):,} blank employees"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'machine_id', 'MCH'):,} "
        "invalid machine references"
    )

    # Negative produced quantity
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "produced_quantity"] *= -1

    messages.append(
        f"{len(rows):,} negative production quantities"
    )

    # Defects greater than production
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "defect_quantity"] = (
        df.loc[rows, "produced_quantity"].abs()
        + 100
    )

    messages.append(
        f"{len(rows):,} defect quantities exceeding production"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'production_hours'):,} "
        "production hours represented as text"
    )

    # Outlier production hours
    messages.append(
        f"{inject_outlier(df, 'production_hours'):,} "
        "production-hour outliers"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'production_date'):,} "
        "mixed production-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'production_id'):,} "
        "production IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "production_id",
        "production_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate production records"
    )

    save(df, "production.csv")
    print_summary("production.csv", messages)


# ============================================================
# MAINTENANCE
# ============================================================

def inject_maintenance():

    df = load("maintenance.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'machine_id'):,} blank machines"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'employee_id', 'EMP'):,} "
        "invalid employee references"
    )

    # Negative maintenance cost
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "maintenance_cost"] *= -1

    messages.append(
        f"{len(rows):,} negative maintenance costs"
    )

    # Negative downtime
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "downtime_hours"] *= -1

    messages.append(
        f"{len(rows):,} negative downtime values"
    )

    # Outlier cost
    messages.append(
        f"{inject_outlier(df, 'maintenance_cost'):,} "
        "maintenance-cost outliers"
    )

    messages.append(
        f"{inject_numeric_as_text(df, 'maintenance_hours'):,} "
        "maintenance hours represented as text"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'maintenance_date'):,} "
        "mixed maintenance-date formats"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "maintenance_type"] = (
        df.loc[rows, "maintenance_type"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent maintenance-type values"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "maintenance_id",
        "maintenance_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate maintenance records"
    )

    save(df, "maintenance.csv")
    print_summary("maintenance.csv", messages)


# ============================================================
# FINANCIAL TRANSACTIONS
# ============================================================

def inject_financial_transactions():

    df = load("financial_transactions.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'category'):,} blank categories"
    )

    messages.append(
        f"{inject_placeholder(df, 'transaction_type', 'n/a'):,} "
        "hidden missing transaction types"
    )

    # Negative amounts
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "amount"] *= -1

    messages.append(
        f"{len(rows):,} negative transaction amounts"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'amount'):,} "
        "amounts represented as text"
    )

    # Outlier amounts
    messages.append(
        f"{inject_outlier(df, 'amount'):,} "
        "transaction amount outliers"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "category"] = (
        df.loc[rows, "category"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent category formats"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'transaction_date'):,} "
        "mixed transaction-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'financial_transaction_id'):,} "
        "transaction IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "financial_transaction_id",
        "transaction_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate transactions"
    )

    save(
        df,
        "financial_transactions.csv",
    )

    print_summary(
        "financial_transactions.csv",
        messages,
    )


# ============================================================
# BUDGET
# ============================================================

def inject_budget():

    df = load("budget.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'budget_category'):,} blank categories"
    )

    # Negative budgets
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "budget_amount"] *= -1

    messages.append(
        f"{len(rows):,} negative budget amounts"
    )

    messages.append(
        f"{inject_numeric_as_text(df, 'budget_amount'):,} "
        "budget amounts represented as text"
    )

    messages.append(
        f"{inject_outlier(df, 'budget_amount'):,} "
        "budget amount outliers"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "budget_category"] = (
        df.loc[rows, "budget_category"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent budget categories"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'budget_date'):,} "
        "mixed budget-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'budget_id'):,} "
        "budget IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "budget_id",
        "budget_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate budgets"
    )

    save(df, "budget.csv")
    print_summary("budget.csv", messages)


# ============================================================
# ENERGY
# ============================================================

def inject_energy():

    df = load("energy.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'energy_type'):,} blank energy types"
    )

    messages.append(
        f"{inject_placeholder(df, 'unit', 'n/a'):,} "
        "hidden missing units"
    )

    # Negative consumption
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "consumption"] *= -1

    messages.append(
        f"{len(rows):,} negative energy-consumption values"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'consumption'):,} "
        "consumption values represented as text"
    )

    messages.append(
        f"{inject_outlier(df, 'energy_cost'):,} "
        "energy-cost outliers"
    )

    # Inconsistent energy type casing
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "energy_type"] = (
        df.loc[rows, "energy_type"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent energy-type values"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'measurement_date'):,} "
        "mixed measurement-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'energy_id'):,} "
        "energy IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "energy_id",
        "measurement_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate energy records"
    )

    save(df, "energy.csv")
    print_summary("energy.csv", messages)


# ============================================================
# EMISSIONS
# ============================================================

def inject_emissions():

    df = load("emissions.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'emission_source'):,} "
        "blank emission sources"
    )

    messages.append(
        f"{inject_placeholder(df, 'unit', 'unknown'):,} "
        "hidden missing emission units"
    )

    # Negative CO2e
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "co2e_amount"] *= -1

    messages.append(
        f"{len(rows):,} negative CO2e values"
    )

    messages.append(
        f"{inject_numeric_as_text(df, 'co2e_amount'):,} "
        "CO2e values represented as text"
    )

    messages.append(
        f"{inject_outlier(df, 'co2e_amount'):,} "
        "CO2e outliers"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "emission_source"] = (
        df.loc[rows, "emission_source"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent emission-source values"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'emissions_date'):,} "
        "mixed emissions-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'emissions_id'):,} "
        "emissions IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "emissions_id",
        "emissions_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate emissions records"
    )

    save(df, "emissions.csv")
    print_summary("emissions.csv", messages)


# ============================================================
# WASTE
# ============================================================

def inject_waste():

    df = load("waste.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'waste_type'):,} blank waste types"
    )

    messages.append(
        f"{inject_placeholder(df, 'disposal_method', 'n/a'):,} "
        "hidden missing disposal methods"
    )

    # Negative waste
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "waste_quantity"] *= -1

    messages.append(
        f"{len(rows):,} negative waste quantities"
    )

    messages.append(
        f"{inject_numeric_as_text(df, 'waste_quantity'):,} "
        "waste quantities represented as text"
    )

    messages.append(
        f"{inject_outlier(df, 'waste_quantity'):,} "
        "waste-quantity outliers"
    )

    # Structural inconsistency
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "waste_type"] = (
        df.loc[rows, "waste_type"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    messages.append(
        f"{len(rows):,} inconsistent waste-type values"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'waste_date'):,} "
        "mixed waste-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'waste_id'):,} "
        "waste IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "waste_id",
        "waste_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate waste records"
    )

    save(df, "waste.csv")
    print_summary("waste.csv", messages)


# ============================================================
# INVENTORY
# ============================================================

def inject_inventory():

    df = load("inventory.csv")
    messages = []

    messages.append(
        f"{inject_nan(df, 'product_id'):,} blank product references"
    )

    messages.append(
        f"{inject_invalid_reference(df, 'product_id', 'PROD'):,} "
        "invalid product references"
    )

    # Negative closing quantity
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "closing_quantity"] *= -1

    messages.append(
        f"{len(rows):,} negative closing quantities"
    )

    # Break inventory reconciliation
    rows = choose_rows(df, INVALID_VALUE_RATE)

    df.loc[rows, "closing_quantity"] += 100

    messages.append(
        f"{len(rows):,} inventory reconciliation violations"
    )

    # Numeric-as-text
    messages.append(
        f"{inject_numeric_as_text(df, 'issued_quantity'):,} "
        "issued quantities represented as text"
    )

    # Outlier reorder point
    messages.append(
        f"{inject_outlier(df, 'reorder_point'):,} "
        "reorder-point outliers"
    )

    messages.append(
        f"{inject_mixed_dates(df, 'inventory_date'):,} "
        "mixed inventory-date formats"
    )

    messages.append(
        f"{inject_whitespace(df, 'inventory_id'):,} "
        "inventory IDs with whitespace"
    )

    before = len(df)
    df = add_exact_duplicates(df, DUPLICATE_RATE)

    messages.append(
        f"{len(df) - before:,} exact duplicate rows"
    )

    before = len(df)
    df = add_partial_duplicates(
        df,
        DUPLICATE_RATE,
        "inventory_id",
        "inventory_date",
        "date",
    )

    messages.append(
        f"{len(df) - before:,} partial duplicate inventory records"
    )

    save(df, "inventory.csv")
    print_summary("inventory.csv", messages)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Controlled Data Quality Issue Injection")
    print("=" * 70)

    print("\nAll 16 raw datasets will receive controlled quality issues.")
    print("Randomness is controlled by the project seed.")
    print("\nStarting injection...")

    # --------------------------------------------------------
    # Reference datasets
    # --------------------------------------------------------

    inject_accounts()
    inject_customers()
    inject_suppliers()
    inject_products()
    inject_locations()
    inject_employees()
    inject_machines()

    # --------------------------------------------------------
    # Business datasets
    # --------------------------------------------------------

    inject_sales()
    inject_production()
    inject_maintenance()
    inject_financial_transactions()
    inject_budget()
    inject_energy()
    inject_emissions()
    inject_waste()
    inject_inventory()

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CONTROLLED QUALITY INJECTION COMPLETE")
    print("=" * 70)

    print("\nThe 16 raw datasets now intentionally contain")
    print("controlled data-quality defects.")

    print("\nQuality dimensions introduced:")
    print("  1. Missing values")
    print("  2. Hidden missing-value placeholders")
    print("  3. Exact duplicates")
    print("  4. Partial duplicates")
    print("  5. Structural inconsistencies")
    print("  6. Incorrect data types")
    print("  7. Outliers and anomalies")
    print("  8. Invalid references")
    print("  9. Business-rule violations")
    print(" 10. Leading/trailing whitespace")
    print(" 11. Mixed date formats")

    print("\nNext step:")
    print("Proceed to Phase 4 — Data Quality profiling and validation.")


if __name__ == "__main__":
    main()
