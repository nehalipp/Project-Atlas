import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ============================================================
# Project Atlas — Phase 5 ETL
# Raw → Staging Transformation
# ============================================================

ETL_ROOT = Path(__file__).resolve().parents[1]

if str(ETL_ROOT) not in sys.path:
    sys.path.insert(0, str(ETL_ROOT))


from config.etl_config import (
    EXPECTED_DATASETS,
    EXPECTED_ROW_COUNTS,
    LOG_DIR,
    RAW_DATA_DIR,
)


STAGING_DATA_DIR = ETL_ROOT / "data" / "staging"


# ============================================================
# Date Columns
# ============================================================

DATE_COLUMNS = {
    "budget": ["date"],
    "emissions": ["date"],
    "employees": ["hire_date"],
    "energy": ["date"],
    "financial_transactions": ["date"],
    "inventory": ["date"],
    "machines": ["installation_date"],
    "maintenance": ["date"],
    "production": ["date"],
    "sales": ["date"],
    "waste": ["date"],
}


# ============================================================
# Numeric Columns
# ============================================================

NUMERIC_COLUMNS = {
    "budget": [
        "budget_amount",
    ],
    "emissions": [
        "co2_kg",
    ],
    "energy": [
        "consumption",
    ],
    "financial_transactions": [
        "amount",
    ],
    "inventory": [
        "quantity_on_hand",
        "reorder_point",
        "inventory_value",
    ],
    "maintenance": [
        "downtime_hours",
        "maintenance_cost",
    ],
    "production": [
        "planned_quantity",
        "quantity_produced",
        "production_hours",
    ],
    "sales": [
        "quantity",
        "unit_price",
        "discount_rate",
        "revenue",
    ],
    "waste": [
        "quantity",
    ],
    "products": [
        "unit_cost",
        "unit_price",
    ],
}


# ============================================================
# Helper Functions
# ============================================================

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to lowercase snake_case.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    return df


def standardize_blank_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert blank or whitespace-only strings to pandas NA.
    """

    df = df.copy()

    object_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for column in object_columns:
        df[column] = (
            df[column]
            .replace(r"^\s*$", pd.NA, regex=True)
        )

    return df


def transform_dates(
    df: pd.DataFrame,
    dataset: str,
) -> pd.DataFrame:
    """
    Convert approved date columns to pandas datetime.
    """

    df = df.copy()

    for column in DATE_COLUMNS.get(dataset, []):

        if column not in df.columns:
            raise ValueError(
                f"Expected date column '{column}' "
                f"not found in {dataset}.csv"
            )

        original_non_null = df[column].notna().sum()

        converted = pd.to_datetime(
            df[column],
            format="%Y-%m-%d",
            errors="coerce",
        )

        conversion_failures = (
            df[column].notna()
            & converted.isna()
        ).sum()

        if conversion_failures > 0:
            raise ValueError(
                f"Date conversion failed for "
                f"{dataset}.{column}: "
                f"{conversion_failures:,} invalid values."
            )

        converted_non_null = converted.notna().sum()

        if original_non_null != converted_non_null:
            raise ValueError(
                f"Non-null date count changed for "
                f"{dataset}.{column}."
            )

        df[column] = converted

    return df


def transform_numeric_columns(
    df: pd.DataFrame,
    dataset: str,
) -> pd.DataFrame:
    """
    Convert approved numeric columns to numeric dtype.
    """

    df = df.copy()

    for column in NUMERIC_COLUMNS.get(dataset, []):

        if column not in df.columns:
            raise ValueError(
                f"Expected numeric column '{column}' "
                f"not found in {dataset}.csv"
            )

        original_non_null = df[column].notna().sum()

        converted = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        conversion_failures = (
            df[column].notna()
            & converted.isna()
        ).sum()

        if conversion_failures > 0:
            raise ValueError(
                f"Numeric conversion failed for "
                f"{dataset}.{column}: "
                f"{conversion_failures:,} invalid values."
            )

        converted_non_null = converted.notna().sum()

        if original_non_null != converted_non_null:
            raise ValueError(
                f"Non-null numeric count changed for "
                f"{dataset}.{column}."
            )

        df[column] = converted

    return df


def transform_dataset(
    dataset: str,
) -> dict:

    raw_file = (
        RAW_DATA_DIR
        / f"{dataset}.csv"
    )

    staging_file = (
        STAGING_DATA_DIR
        / f"{dataset}.csv"
    )

    if not raw_file.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_file}"
        )

    # --------------------------------------------------------
    # Read Raw
    # --------------------------------------------------------

    df = pd.read_csv(
        raw_file,
        low_memory=False,
    )

    raw_rows = len(df)

    expected_rows = EXPECTED_ROW_COUNTS[
        dataset
    ]

    if raw_rows != expected_rows:
        raise ValueError(
            f"Raw row-count mismatch for "
            f"{dataset}.csv. "
            f"Expected {expected_rows:,}; "
            f"found {raw_rows:,}."
        )

    original_columns = list(df.columns)

    # --------------------------------------------------------
    # Standardize structure
    # --------------------------------------------------------

    df = standardize_column_names(df)

    df = standardize_blank_values(df)

    # --------------------------------------------------------
    # Transform dates
    # --------------------------------------------------------

    df = transform_dates(
        df,
        dataset,
    )

    # --------------------------------------------------------
    # Transform numeric fields
    # --------------------------------------------------------

    df = transform_numeric_columns(
        df,
        dataset,
    )

    # --------------------------------------------------------
    # Final row-count validation
    # --------------------------------------------------------

    staging_rows = len(df)

    if staging_rows != raw_rows:
        raise ValueError(
            f"Staging row-count mismatch for "
            f"{dataset}.csv. "
            f"Raw={raw_rows:,}; "
            f"Staging={staging_rows:,}."
        )

    # --------------------------------------------------------
    # Write staging dataset
    # --------------------------------------------------------

    df.to_csv(
        staging_file,
        index=False,
        date_format="%Y-%m-%d",
    )

    return {
        "dataset": dataset,
        "raw_rows": raw_rows,
        "staging_rows": staging_rows,
        "column_count": len(df.columns),
        "original_columns": original_columns,
        "staging_columns": list(df.columns),
        "date_columns_transformed": DATE_COLUMNS.get(
            dataset,
            [],
        ),
        "numeric_columns_transformed": NUMERIC_COLUMNS.get(
            dataset,
            [],
        ),
        "status": "PASS",
    }


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 75)
    print("Project Atlas — Phase 5 ETL — Raw to Staging")
    print("=" * 75)

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found:\n"
            f"{RAW_DATA_DIR}"
        )

    STAGING_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    total_raw_rows = 0
    total_staging_rows = 0

    # --------------------------------------------------------
    # Process all 16 datasets
    # --------------------------------------------------------

    for dataset in EXPECTED_DATASETS:

        print(
            f"\nTransforming: {dataset}.csv"
        )

        result = transform_dataset(
            dataset
        )

        results.append(result)

        total_raw_rows += result["raw_rows"]
        total_staging_rows += result["staging_rows"]

        print(
            f"Rows: {result['staging_rows']:,} | "
            f"Columns: {result['column_count']} | "
            f"Transformation: PASS"
        )

    # --------------------------------------------------------
    # Overall reconciliation
    # --------------------------------------------------------

    print("\n" + "-" * 75)

    print(
        f"Raw total rows:      {total_raw_rows:,}"
    )

    print(
        f"Staging total rows:  {total_staging_rows:,}"
    )

    if total_raw_rows != total_staging_rows:
        raise RuntimeError(
            "Overall Raw → Staging row-count "
            "reconciliation failed."
        )

    if total_staging_rows != sum(
        EXPECTED_ROW_COUNTS.values()
    ):
        raise RuntimeError(
            "Staging total does not match "
            "the Phase 4 trusted-data contract."
        )

    # --------------------------------------------------------
    # Write transformation log
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
        / f"staging_{timestamp}.json"
    )

    log_payload = {
        "pipeline_stage": "raw_to_staging",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "datasets_processed": len(results),
        "total_raw_rows": total_raw_rows,
        "total_staging_rows": total_staging_rows,
        "status": "SUCCESS",
        "results": results,
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

    print("\n" + "=" * 75)
    print("RAW → STAGING STATUS: SUCCESS")
    print("=" * 75)

    print(
        f"Datasets processed: {len(results)}"
    )

    print(
        f"Total rows:         {total_staging_rows:,}"
    )

    print(
        f"Staging directory:  {STAGING_DATA_DIR}"
    )

    print(
        f"Log file:           {log_file}"
    )

    print("=" * 75)


if __name__ == "__main__":
    main()