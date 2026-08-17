"""
Project Atlas
Phase 5 — ETL
Step 3 — Staging → Warehouse-Ready Transformation

Purpose
-------
Transform the standardized Phase 5 staging datasets into
warehouse-ready dimension and fact datasets.

The outputs are prepared for Phase 6 PostgreSQL loading.

Approved warehouse baseline
---------------------------
Dimensions:
    dim_date
    dim_account
    dim_customer
    dim_product
    dim_supplier
    dim_location
    dim_employee
    dim_machine

Facts:
    fact_sales
    fact_production
    fact_maintenance
    fact_financial_transaction
    fact_budget
    fact_energy
    fact_emissions
    fact_waste
    fact_inventory

Important
---------
This script does NOT:
    - load PostgreSQL
    - join business facts to other business facts
    - change fact grain
    - implement SCD Type 2
    - perform incremental loading

It creates warehouse-ready CSV files with:
    - surrogate keys
    - preserved source/business identifiers
    - conformed dimension references
    - warehouse-ready column structure
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import sys

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

ETL_ROOT = Path(__file__).resolve().parents[1]

if str(ETL_ROOT) not in sys.path:
    sys.path.insert(0, str(ETL_ROOT))

from config.etl_config import (
    EXPECTED_DATASETS,
    EXPECTED_ROW_COUNTS,
    LOG_DIR,
)


STAGING_DIR = (
    ETL_ROOT
    / "data"
    / "staging"
)

WAREHOUSE_READY_DIR = (
    ETL_ROOT
    / "data"
    / "warehouse_ready"
)


# ============================================================
# APPROVED SOURCE DATASETS
# ============================================================

REFERENCE_DATASETS = {
    "accounts",
    "customers",
    "products",
    "suppliers",
    "locations",
    "employees",
    "machines",
}


FACT_DATASETS = {
    "sales",
    "production",
    "maintenance",
    "financial_transactions",
    "budget",
    "energy",
    "emissions",
    "waste",
    "inventory",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_staging(name: str) -> pd.DataFrame:
    """
    Load one staging dataset.
    """

    path = STAGING_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing staging dataset:\n{path}"
        )

    df = pd.read_csv(
        path,
        low_memory=False,
    )

    expected_rows = EXPECTED_ROW_COUNTS[name]

    if len(df) != expected_rows:
        raise ValueError(
            f"Unexpected row count for {name}.csv. "
            f"Expected {expected_rows:,}; "
            f"found {len(df):,}."
        )

    return df


def validate_unique_key(
    df: pd.DataFrame,
    column: str,
    dataset: str,
) -> None:
    """
    Confirm that a business key is unique.
    """

    if column not in df.columns:
        raise ValueError(
            f"{dataset}: missing required key column "
            f"'{column}'."
        )

    if df[column].isna().any():
        raise ValueError(
            f"{dataset}: key column '{column}' "
            f"contains NULL values."
        )

    duplicates = df[column].duplicated().sum()

    if duplicates > 0:
        raise ValueError(
            f"{dataset}: key column '{column}' "
            f"contains {duplicates:,} duplicates."
        )


def create_surrogate_key(
    df: pd.DataFrame,
    business_key: str,
    surrogate_key: str,
) -> pd.DataFrame:
    """
    Create deterministic integer surrogate keys.

    Keys are assigned after sorting by business key so that
    the same source data produces reproducible key assignments.
    """

    result = df.copy()

    result = result.sort_values(
        by=business_key
    ).reset_index(
        drop=True
    )

    result.insert(
        0,
        surrogate_key,
        range(
            1,
            len(result) + 1,
        ),
    )

    return result


def create_date_dimension(
    fact_dataframes: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build conformed Date dimension from all business-process
    date columns.

    Date range is determined from actual Phase 5 staging data.
    """

    all_dates = []

    date_columns = {
        "sales": "date",
        "production": "date",
        "maintenance": "date",
        "financial_transactions": "date",
        "budget": "date",
        "energy": "date",
        "emissions": "date",
        "waste": "date",
        "inventory": "date",
    }

    for dataset, column in date_columns.items():

        df = fact_dataframes[dataset]

        if column not in df.columns:
            raise ValueError(
                f"{dataset}: missing date column '{column}'."
            )

        all_dates.append(
            pd.to_datetime(
                df[column],
                errors="raise",
            )
        )

    dates = pd.concat(
        all_dates,
        ignore_index=True,
    )

    min_date = dates.min()
    max_date = dates.max()

    calendar = pd.date_range(
        start=min_date,
        end=max_date,
        freq="D",
    )

    dim_date = pd.DataFrame({
        "date": calendar,
    })

    dim_date["date_key"] = (
        dim_date["date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dim_date["year"] = (
        dim_date["date"]
        .dt.year
    )

    dim_date["quarter"] = (
        dim_date["date"]
        .dt.quarter
    )

    dim_date["month"] = (
        dim_date["date"]
        .dt.month
    )

    dim_date["month_name"] = (
        dim_date["date"]
        .dt.strftime("%B")
    )

    dim_date["week_of_year"] = (
        dim_date["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    dim_date["day"] = (
        dim_date["date"]
        .dt.day
    )

    dim_date["day_name"] = (
        dim_date["date"]
        .dt.strftime("%A")
    )

    dim_date["day_of_week"] = (
        dim_date["date"]
        .dt.dayofweek + 1
    )

    dim_date["is_weekend"] = (
        dim_date["date"]
        .dt.dayofweek
        >= 5
    )

    dim_date = dim_date[
        [
            "date_key",
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week_of_year",
            "day",
            "day_name",
            "day_of_week",
            "is_weekend",
        ]
    ]

    return dim_date


def build_dimensions(
    staging: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:

    dimensions = {}

    # --------------------------------------------------------
    # Account
    # --------------------------------------------------------

    accounts = staging["accounts"].copy()

    validate_unique_key(
        accounts,
        "account_id",
        "accounts",
    )

    dimensions["dim_account"] = create_surrogate_key(
        accounts,
        "account_id",
        "account_key",
    )

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    customers = staging["customers"].copy()

    validate_unique_key(
        customers,
        "customer_id",
        "customers",
    )

    dimensions["dim_customer"] = create_surrogate_key(
        customers,
        "customer_id",
        "customer_key",
    )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    products = staging["products"].copy()

    validate_unique_key(
        products,
        "product_id",
        "products",
    )

    dimensions["dim_product"] = create_surrogate_key(
        products,
        "product_id",
        "product_key",
    )

    # --------------------------------------------------------
    # Supplier
    # --------------------------------------------------------

    suppliers = staging["suppliers"].copy()

    validate_unique_key(
        suppliers,
        "supplier_id",
        "suppliers",
    )

    dimensions["dim_supplier"] = create_surrogate_key(
        suppliers,
        "supplier_id",
        "supplier_key",
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    locations = staging["locations"].copy()

    validate_unique_key(
        locations,
        "location_id",
        "locations",
    )

    dimensions["dim_location"] = create_surrogate_key(
        locations,
        "location_id",
        "location_key",
    )

    # --------------------------------------------------------
    # Employee
    # --------------------------------------------------------

    employees = staging["employees"].copy()

    validate_unique_key(
        employees,
        "employee_id",
        "employees",
    )

    dimensions["dim_employee"] = create_surrogate_key(
        employees,
        "employee_id",
        "employee_key",
    )

    # --------------------------------------------------------
    # Machine
    # --------------------------------------------------------

    machines = staging["machines"].copy()

    validate_unique_key(
        machines,
        "machine_id",
        "machines",
    )

    dimensions["dim_machine"] = create_surrogate_key(
        machines,
        "machine_id",
        "machine_key",
    )

    return dimensions


def validate_reference_mapping(
    fact_df: pd.DataFrame,
    source_column: str,
    dimension_df: pd.DataFrame,
    dimension_business_key: str,
    dataset: str,
) -> None:
    """
    Validate that every non-null fact business key exists
    in the corresponding dimension.
    """

    source_values = set(
        fact_df[source_column]
        .dropna()
        .astype(str)
    )

    dimension_values = set(
        dimension_df[dimension_business_key]
        .dropna()
        .astype(str)
    )

    missing = source_values - dimension_values

    if missing:
        preview = sorted(
            list(missing)
        )[:10]

        raise ValueError(
            f"{dataset}: {source_column} contains "
            f"{len(missing):,} unmapped business keys. "
            f"Examples: {preview}"
        )


def add_date_key(
    df: pd.DataFrame,
    date_column: str = "date",
) -> pd.DataFrame:
    """
    Add integer date_key in YYYYMMDD format.
    """

    result = df.copy()

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="raise",
    )

    result["date_key"] = (
        result[date_column]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    return result


def map_dimension_key(
    fact_df: pd.DataFrame,
    dimension_df: pd.DataFrame,
    business_key: str,
    surrogate_key: str,
    fact_dataset: str,
) -> pd.DataFrame:
    """
    Map source business key to warehouse surrogate key.
    """

    mapping = dimension_df[
        [
            business_key,
            surrogate_key,
        ]
    ].copy()

    result = fact_df.merge(
        mapping,
        on=business_key,
        how="left",
        validate="many_to_one",
    )

    missing = result[surrogate_key].isna().sum()

    if missing > 0:
        raise ValueError(
            f"{fact_dataset}: {missing:,} rows could not "
            f"be mapped to {surrogate_key}."
        )

    result[surrogate_key] = (
        result[surrogate_key]
        .astype(int)
    )

    return result


# ============================================================
# FACT BUILDERS
# ============================================================

def build_fact_sales(
    staging,
    dimensions,
):
    df = staging["sales"].copy()

    # Preserve one row per source sales transaction.
    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_account"],
        "account_id",
        "account_key",
        "sales",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_customer"],
        "customer_id",
        "customer_key",
        "sales",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_product"],
        "product_id",
        "product_key",
        "sales",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "sales",
    )

    # Business rule:
    # customer belongs to account.
    customer_accounts = dimensions["dim_customer"][
        [
            "customer_id",
            "account_id",
        ]
    ]

    account_check = df[
        [
            "customer_id",
            "account_id",
        ]
    ].merge(
        customer_accounts,
        on="customer_id",
        how="left",
        suffixes=(
            "_sales",
            "_customer",
        ),
        validate="many_to_one",
    )

    invalid_relationships = (
        account_check["account_id_sales"]
        != account_check["account_id_customer"]
    ).sum()

    if invalid_relationships > 0:
        raise ValueError(
            f"sales: {invalid_relationships:,} rows "
            f"violate Customer → Account relationship."
        )

    if len(df) != original_rows:
        raise ValueError(
            "fact_sales row count changed."
        )

    return df[
        [
            "sales_id",
            "date",
            "date_key",
            "account_id",
            "account_key",
            "customer_id",
            "customer_key",
            "product_id",
            "product_key",
            "location_id",
            "location_key",
            "quantity",
            "unit_price",
            "discount_rate",
            "revenue",
        ]
    ]


def build_fact_production(
    staging,
    dimensions,
):
    df = staging["production"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_product"],
        "product_id",
        "product_key",
        "production",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "production",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_machine"],
        "machine_id",
        "machine_key",
        "production",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_employee"],
        "employee_id",
        "employee_key",
        "production",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_production row count changed."
        )

    return df[
        [
            "production_id",
            "date",
            "date_key",
            "product_id",
            "product_key",
            "location_id",
            "location_key",
            "machine_id",
            "machine_key",
            "employee_id",
            "employee_key",
            "planned_quantity",
            "quantity_produced",
            "production_hours",
            "production_status",
        ]
    ]


def build_fact_maintenance(
    staging,
    dimensions,
):
    df = staging["maintenance"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "maintenance",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_machine"],
        "machine_id",
        "machine_key",
        "maintenance",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_employee"],
        "employee_id",
        "employee_key",
        "maintenance",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_maintenance row count changed."
        )

    return df[
        [
            "maintenance_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "machine_id",
            "machine_key",
            "employee_id",
            "employee_key",
            "maintenance_type",
            "downtime_hours",
            "maintenance_cost",
        ]
    ]


def build_fact_financial_transaction(
    staging,
    dimensions,
):
    df = staging[
        "financial_transactions"
    ].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "financial_transactions",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_financial_transaction row count changed."
        )

    return df[
        [
            "financial_transaction_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "transaction_type",
            "amount",
            "description",
        ]
    ]


def build_fact_budget(
    staging,
    dimensions,
):
    df = staging["budget"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "budget",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_budget row count changed."
        )

    return df[
        [
            "budget_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "category",
            "budget_amount",
        ]
    ]


def build_fact_energy(
    staging,
    dimensions,
):
    df = staging["energy"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "energy",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_energy row count changed."
        )

    return df[
        [
            "energy_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "energy_type",
            "consumption",
            "unit",
        ]
    ]


def build_fact_emissions(
    staging,
    dimensions,
):
    df = staging["emissions"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "emissions",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_emissions row count changed."
        )

    return df[
        [
            "emissions_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "source",
            "co2_kg",
        ]
    ]


def build_fact_waste(
    staging,
    dimensions,
):
    df = staging["waste"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "waste",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_waste row count changed."
        )

    return df[
        [
            "waste_id",
            "date",
            "date_key",
            "location_id",
            "location_key",
            "waste_type",
            "quantity",
            "unit",
            "disposal_method",
        ]
    ]


def build_fact_inventory(
    staging,
    dimensions,
):
    df = staging["inventory"].copy()

    original_rows = len(df)

    df = add_date_key(df)

    df = map_dimension_key(
        df,
        dimensions["dim_product"],
        "product_id",
        "product_key",
        "inventory",
    )

    df = map_dimension_key(
        df,
        dimensions["dim_location"],
        "location_id",
        "location_key",
        "inventory",
    )

    if len(df) != original_rows:
        raise ValueError(
            "fact_inventory row count changed."
        )

    return df[
        [
            "inventory_id",
            "date",
            "date_key",
            "product_id",
            "product_key",
            "location_id",
            "location_key",
            "quantity_on_hand",
            "reorder_point",
            "inventory_value",
        ]
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "Project Atlas — Phase 5 ETL — "
        "Staging to Warehouse-Ready"
    )
    print("=" * 80)

    STAGING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    WAREHOUSE_READY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load all staging datasets
    # --------------------------------------------------------

    print("\nLoading staging datasets...")

    staging = {}

    for dataset in EXPECTED_DATASETS:

        staging[dataset] = load_staging(
            dataset
        )

        print(
            f"{dataset:<30}"
            f"{len(staging[dataset]):>10,} rows"
        )

    # --------------------------------------------------------
    # Build dimensions
    # --------------------------------------------------------

    print("\nBuilding dimensions...")

    fact_source_data = {
        name: staging[name]
        for name in FACT_DATASETS
    }

    dimensions = build_dimensions(
        staging
    )

    dimensions["dim_date"] = create_date_dimension(
        fact_source_data
    )

    # --------------------------------------------------------
    # Build facts
    # --------------------------------------------------------

    print("\nBuilding facts...")

    facts = {}

    facts["fact_sales"] = build_fact_sales(
        staging,
        dimensions,
    )

    facts["fact_production"] = build_fact_production(
        staging,
        dimensions,
    )

    facts["fact_maintenance"] = build_fact_maintenance(
        staging,
        dimensions,
    )

    facts[
        "fact_financial_transaction"
    ] = build_fact_financial_transaction(
        staging,
        dimensions,
    )

    facts["fact_budget"] = build_fact_budget(
        staging,
        dimensions,
    )

    facts["fact_energy"] = build_fact_energy(
        staging,
        dimensions,
    )

    facts["fact_emissions"] = build_fact_emissions(
        staging,
        dimensions,
    )

    facts["fact_waste"] = build_fact_waste(
        staging,
        dimensions,
    )

    facts["fact_inventory"] = build_fact_inventory(
        staging,
        dimensions,
    )

    # --------------------------------------------------------
    # Combine warehouse-ready objects
    # --------------------------------------------------------

    warehouse_objects = {}

    warehouse_objects.update(
        dimensions
    )

    warehouse_objects.update(
        facts
    )

    # --------------------------------------------------------
    # Write outputs
    # --------------------------------------------------------

    print("\nWriting warehouse-ready datasets...")

    results = []

    for name, df in warehouse_objects.items():

        output_file = (
            WAREHOUSE_READY_DIR
            / f"{name}.csv"
        )

        df.to_csv(
            output_file,
            index=False,
            date_format="%Y-%m-%d",
        )

        results.append({
            "dataset": name,
            "rows": len(df),
            "columns": len(df.columns),
            "file": str(output_file),
            "status": "PASS",
        })

        print(
            f"{name:<35}"
            f"{len(df):>10,} rows | "
            f"{len(df.columns):>3} columns | PASS"
        )

    # --------------------------------------------------------
    # Log
    # --------------------------------------------------------

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    log_file = (
        LOG_DIR
        / f"warehouse_ready_{timestamp}.json"
    )

    log_payload = {
        "pipeline_stage":
            "staging_to_warehouse_ready",

        "timestamp_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "dimension_count":
            len(dimensions),

        "fact_count":
            len(facts),

        "warehouse_object_count":
            len(warehouse_objects),

        "status":
            "SUCCESS",

        "results":
            results,
    }

    log_file.write_text(
        json.dumps(
            log_payload,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "STAGING → WAREHOUSE-READY STATUS: SUCCESS"
    )
    print("=" * 80)

    print(
        f"Dimensions created: "
        f"{len(dimensions)}"
    )

    print(
        f"Facts created:      "
        f"{len(facts)}"
    )

    print(
        f"Warehouse objects:  "
        f"{len(warehouse_objects)}"
    )

    print(
        f"Output directory:   "
        f"{WAREHOUSE_READY_DIR}"
    )

    print(
        f"Log file:           "
        f"{log_file}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()