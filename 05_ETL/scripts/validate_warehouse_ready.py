"""
Project Atlas
Phase 5 — ETL
Step 4 — Warehouse-Ready Validation

Purpose
-------
Validate the 17 warehouse-ready datasets produced by:

    05_ETL/scripts/transform_to_warehouse.py

Validation areas
----------------
1. Dataset existence
2. Row-count reconciliation
3. Dimension business-key uniqueness
4. Dimension surrogate-key uniqueness
5. Fact source-key uniqueness
6. Foreign-key integrity
7. Date-key integrity
8. Fact grain protection
9. Business relationship integrity
10. Numeric validity
11. Date validity
12. Warehouse object structure
13. Final ETL reconciliation

This is the formal Phase 5 validation gate.

The script does NOT:
    - modify data
    - load PostgreSQL
    - create database objects
    - silently repair failures
    - join facts together

A failure causes a non-zero exit status.
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


WAREHOUSE_READY_DIR = (
    ETL_ROOT
    / "data"
    / "warehouse_ready"
)

STAGING_DIR = (
    ETL_ROOT
    / "data"
    / "staging"
)

TRUSTED_DIR = (
    ETL_ROOT
    / ".."
    / "04_Data_Quality"
    / "data"
    / "trusted"
)


# ============================================================
# APPROVED WAREHOUSE OBJECTS
# ============================================================

DIMENSIONS = [
    "dim_date",
    "dim_account",
    "dim_customer",
    "dim_product",
    "dim_supplier",
    "dim_location",
    "dim_employee",
    "dim_machine",
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
    "fact_inventory",
]

WAREHOUSE_OBJECTS = DIMENSIONS + FACTS


# ============================================================
# SOURCE → FACT MAPPING
# ============================================================

FACT_SOURCE_MAPPING = {
    "fact_sales": "sales",
    "fact_production": "production",
    "fact_maintenance": "maintenance",
    "fact_financial_transaction": "financial_transactions",
    "fact_budget": "budget",
    "fact_energy": "energy",
    "fact_emissions": "emissions",
    "fact_waste": "waste",
    "fact_inventory": "inventory",
}


# ============================================================
# EXPECTED DIMENSION KEYS
# ============================================================

DIMENSION_KEYS = {
    "dim_account": {
        "business_key": "account_id",
        "surrogate_key": "account_key",
    },
    "dim_customer": {
        "business_key": "customer_id",
        "surrogate_key": "customer_key",
    },
    "dim_product": {
        "business_key": "product_id",
        "surrogate_key": "product_key",
    },
    "dim_supplier": {
        "business_key": "supplier_id",
        "surrogate_key": "supplier_key",
    },
    "dim_location": {
        "business_key": "location_id",
        "surrogate_key": "location_key",
    },
    "dim_employee": {
        "business_key": "employee_id",
        "surrogate_key": "employee_key",
    },
    "dim_machine": {
        "business_key": "machine_id",
        "surrogate_key": "machine_key",
    },
    "dim_date": {
        "business_key": "date",
        "surrogate_key": "date_key",
    },
}


# ============================================================
# EXPECTED FACT SOURCE KEYS
# ============================================================

FACT_SOURCE_KEYS = {
    "fact_sales": "sales_id",
    "fact_production": "production_id",
    "fact_maintenance": "maintenance_id",
    "fact_financial_transaction":
        "financial_transaction_id",
    "fact_budget": "budget_id",
    "fact_energy": "energy_id",
    "fact_emissions": "emissions_id",
    "fact_waste": "waste_id",
    "fact_inventory": "inventory_id",
}


# ============================================================
# EXPECTED FACT FOREIGN KEYS
# ============================================================

FACT_FOREIGN_KEYS = {
    "fact_sales": {
        "date_key": "dim_date",
        "account_key": "dim_account",
        "customer_key": "dim_customer",
        "product_key": "dim_product",
        "location_key": "dim_location",
    },

    "fact_production": {
        "date_key": "dim_date",
        "product_key": "dim_product",
        "location_key": "dim_location",
        "machine_key": "dim_machine",
        "employee_key": "dim_employee",
    },

    "fact_maintenance": {
        "date_key": "dim_date",
        "location_key": "dim_location",
        "machine_key": "dim_machine",
        "employee_key": "dim_employee",
    },

    "fact_financial_transaction": {
        "date_key": "dim_date",
        "location_key": "dim_location",
    },

    "fact_budget": {
        "date_key": "dim_date",
        "location_key": "dim_location",
    },

    "fact_energy": {
        "date_key": "dim_date",
        "location_key": "dim_location",
    },

    "fact_emissions": {
        "date_key": "dim_date",
        "location_key": "dim_location",
    },

    "fact_waste": {
        "date_key": "dim_date",
        "location_key": "dim_location",
    },

    "fact_inventory": {
        "date_key": "dim_date",
        "product_key": "dim_product",
        "location_key": "dim_location",
    },
}


# ============================================================
# EXPECTED FACT GRAINS
# ============================================================

FACT_GRAINS = {
    "fact_sales":
        "One row represents one sales transaction.",

    "fact_production":
        "One row represents one production event for "
        "a product, machine, employee, location and date.",

    "fact_maintenance":
        "One row represents one maintenance event for "
        "a machine, employee, location and date.",

    "fact_financial_transaction":
        "One row represents one financial transaction.",

    "fact_budget":
        "One row represents one budget record for "
        "a location, category and date.",

    "fact_energy":
        "One row represents one energy measurement for "
        "a location, energy type and date.",

    "fact_emissions":
        "One row represents one emissions measurement for "
        "a location, source and date.",

    "fact_waste":
        "One row represents one waste record for "
        "a location, waste type and date.",

    "fact_inventory":
        "One row represents one inventory snapshot for "
        "a product, location and date.",
}


# ============================================================
# EXPECTED OUTPUT COLUMNS
# ============================================================

EXPECTED_COLUMNS = {
    "dim_account": [
        "account_key",
        "account_id",
        "account_name",
        "account_type",
        "industry",
        "country",
        "status",
    ],

    "dim_customer": [
        "customer_key",
        "customer_id",
        "account_id",
        "customer_name",
        "customer_segment",
        "industry",
        "country",
        "status",
    ],

    "dim_product": [
        "product_key",
        "product_id",
        "supplier_id",
        "product_name",
        "category",
        "unit_cost",
        "unit_price",
        "status",
    ],

    "dim_supplier": [
        "supplier_key",
        "supplier_id",
        "supplier_name",
        "supplier_category",
        "country",
        "status",
    ],

    "dim_location": [
        "location_key",
        "location_id",
        "location_name",
        "location_type",
        "city",
        "state_region",
        "country",
        "status",
    ],

    "dim_employee": [
        "employee_key",
        "employee_id",
        "location_id",
        "employee_name",
        "department",
        "role",
        "hire_date",
        "status",
    ],

    "dim_machine": [
        "machine_key",
        "machine_id",
        "location_id",
        "machine_name",
        "machine_type",
        "installation_date",
        "status",
    ],

    "dim_date": [
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
    ],

    "fact_sales": [
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
    ],

    "fact_production": [
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
    ],

    "fact_maintenance": [
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
    ],

    "fact_financial_transaction": [
        "financial_transaction_id",
        "date",
        "date_key",
        "location_id",
        "location_key",
        "transaction_type",
        "amount",
        "description",
    ],

    "fact_budget": [
        "budget_id",
        "date",
        "date_key",
        "location_id",
        "location_key",
        "category",
        "budget_amount",
    ],

    "fact_energy": [
        "energy_id",
        "date",
        "date_key",
        "location_id",
        "location_key",
        "energy_type",
        "consumption",
        "unit",
    ],

    "fact_emissions": [
        "emissions_id",
        "date",
        "date_key",
        "location_id",
        "location_key",
        "source",
        "co2_kg",
    ],

    "fact_waste": [
        "waste_id",
        "date",
        "date_key",
        "location_id",
        "location_key",
        "waste_type",
        "quantity",
        "unit",
        "disposal_method",
    ],

    "fact_inventory": [
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
    ],
}


# ============================================================
# VALIDATION STATE
# ============================================================

results = []


def record_result(
    category: str,
    check: str,
    status: str,
    details: str,
):
    results.append({
        "category": category,
        "check": check,
        "status": status,
        "details": details,
    })


def print_result(
    check: str,
    status: str,
    details: str = "",
):
    print(
        f"{check:<55}"
        f"{status:<8}"
        f"{details}"
    )


# ============================================================
# LOAD WAREHOUSE-READY DATA
# ============================================================

def load_warehouse_ready():
    data = {}

    for object_name in WAREHOUSE_OBJECTS:

        path = (
            WAREHOUSE_READY_DIR
            / f"{object_name}.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Required warehouse-ready object "
                f"does not exist: {path}"
            )

        data[object_name] = pd.read_csv(
            path,
            low_memory=False,
        )

    return data


# ============================================================
# 1. OBJECT EXISTENCE
# ============================================================

def validate_object_existence():

    print("\nOBJECT EXISTENCE")
    print("-" * 90)

    for object_name in WAREHOUSE_OBJECTS:

        path = (
            WAREHOUSE_READY_DIR
            / f"{object_name}.csv"
        )

        if path.exists():

            record_result(
                "object_existence",
                object_name,
                "PASS",
                "Warehouse-ready object exists.",
            )

            print_result(
                object_name,
                "PASS",
            )

        else:

            record_result(
                "object_existence",
                object_name,
                "FAIL",
                "Missing warehouse-ready object.",
            )

            print_result(
                object_name,
                "FAIL",
                "Missing",
            )


# ============================================================
# 2. STRUCTURE VALIDATION
# ============================================================

def validate_structure(data):

    print("\nSTRUCTURE VALIDATION")
    print("-" * 90)

    for object_name in WAREHOUSE_OBJECTS:

        actual = list(
            data[object_name].columns
        )

        expected = EXPECTED_COLUMNS[
            object_name
        ]

        if actual == expected:

            record_result(
                "structure",
                object_name,
                "PASS",
                "Column structure matches specification.",
            )

            print_result(
                object_name,
                "PASS",
            )

        else:

            missing = [
                c for c in expected
                if c not in actual
            ]

            unexpected = [
                c for c in actual
                if c not in expected
            ]

            details = (
                f"Missing={missing}; "
                f"Unexpected={unexpected}"
            )

            record_result(
                "structure",
                object_name,
                "FAIL",
                details,
            )

            print_result(
                object_name,
                "FAIL",
                details,
            )


# ============================================================
# 3. ROW COUNT RECONCILIATION
# ============================================================

def validate_row_counts(data):

    print("\nROW COUNT RECONCILIATION")
    print("-" * 90)

    for fact_name, source_name in FACT_SOURCE_MAPPING.items():

        trusted_file = (
            TRUSTED_DIR
            / f"{source_name}.csv"
        )

        staging_file = (
            STAGING_DIR
            / f"{source_name}.csv"
        )

        warehouse_df = data[fact_name]

        trusted_rows = None
        staging_rows = None

        if trusted_file.exists():
            trusted_rows = len(
                pd.read_csv(
                    trusted_file,
                    usecols=[0],
                )
            )

        if staging_file.exists():
            staging_rows = len(
                pd.read_csv(
                    staging_file,
                    usecols=[0],
                )
            )

        warehouse_rows = len(
            warehouse_df
        )

        expected_rows = EXPECTED_ROW_COUNTS[
            source_name
        ]

        checks = [
            expected_rows == warehouse_rows,
            staging_rows is None
            or staging_rows == warehouse_rows,
            trusted_rows is None
            or trusted_rows == warehouse_rows,
        ]

        passed = all(checks)

        details = (
            f"Expected={expected_rows:,}; "
            f"Trusted={trusted_rows:,} "
            if trusted_rows is not None
            else
            f"Expected={expected_rows:,}; "
            f"Trusted=N/A "
        )

        details += (
            f"Staging={staging_rows:,} "
            if staging_rows is not None
            else
            "Staging=N/A "
        )

        details += (
            f"Warehouse={warehouse_rows:,}"
        )

        if passed:

            record_result(
                "row_count",
                fact_name,
                "PASS",
                details,
            )

            print_result(
                fact_name,
                "PASS",
                details,
            )

        else:

            record_result(
                "row_count",
                fact_name,
                "FAIL",
                details,
            )

            print_result(
                fact_name,
                "FAIL",
                details,
            )


# ============================================================
# 4. DIMENSION KEY VALIDATION
# ============================================================

def validate_dimension_keys(data):

    print("\nDIMENSION KEY VALIDATION")
    print("-" * 90)

    for dimension, keys in DIMENSION_KEYS.items():

        df = data[dimension]

        checks = []

        for key_type in [
            "business_key",
            "surrogate_key",
        ]:

            column = keys[key_type]

            null_count = df[column].isna().sum()

            duplicate_count = (
                df[column].duplicated()
                .sum()
            )

            checks.append(
                null_count == 0
            )

            checks.append(
                duplicate_count == 0
            )

            if null_count > 0:

                details = (
                    f"{column}: "
                    f"{null_count:,} NULL values"
                )

                record_result(
                    "dimension_keys",
                    f"{dimension}.{column}",
                    "FAIL",
                    details,
                )

                print_result(
                    f"{dimension}.{column}",
                    "FAIL",
                    details,
                )

            elif duplicate_count > 0:

                details = (
                    f"{column}: "
                    f"{duplicate_count:,} duplicates"
                )

                record_result(
                    "dimension_keys",
                    f"{dimension}.{column}",
                    "FAIL",
                    details,
                )

                print_result(
                    f"{dimension}.{column}",
                    "FAIL",
                    details,
                )

            else:

                details = (
                    f"{column}: unique and non-null"
                )

                record_result(
                    "dimension_keys",
                    f"{dimension}.{column}",
                    "PASS",
                    details,
                )

                print_result(
                    f"{dimension}.{column}",
                    "PASS",
                    details,
                )


# ============================================================
# 5. FACT SOURCE KEY VALIDATION
# ============================================================

def validate_fact_source_keys(data):

    print("\nFACT SOURCE KEY VALIDATION")
    print("-" * 90)

    for fact_name, source_key in FACT_SOURCE_KEYS.items():

        df = data[fact_name]

        null_count = (
            df[source_key]
            .isna()
            .sum()
        )

        duplicate_count = (
            df[source_key]
            .duplicated()
            .sum()
        )

        if null_count == 0 and duplicate_count == 0:

            record_result(
                "fact_source_keys",
                fact_name,
                "PASS",
                f"{source_key} is unique and non-null.",
            )

            print_result(
                fact_name,
                "PASS",
                source_key,
            )

        else:

            details = (
                f"{source_key}: "
                f"NULL={null_count:,}; "
                f"Duplicates={duplicate_count:,}"
            )

            record_result(
                "fact_source_keys",
                fact_name,
                "FAIL",
                details,
            )

            print_result(
                fact_name,
                "FAIL",
                details,
            )


# ============================================================
# 6. FOREIGN KEY VALIDATION
# ============================================================

def validate_foreign_keys(data):

    print("\nFOREIGN KEY VALIDATION")
    print("-" * 90)

    for fact_name, mappings in FACT_FOREIGN_KEYS.items():

        fact_df = data[fact_name]

        for fact_column, dimension in mappings.items():

            dimension_df = data[dimension]

            dimension_key = fact_column

            fact_values = set(
                fact_df[
                    fact_column
                ]
                .dropna()
                .astype(str)
            )

            dimension_values = set(
                dimension_df[
                    dimension_key
                ]
                .dropna()
                .astype(str)
            )

            missing = (
                fact_values
                - dimension_values
            )

            null_count = (
                fact_df[
                    fact_column
                ]
                .isna()
                .sum()
            )

            if not missing and null_count == 0:

                details = (
                    f"{fact_column} → "
                    f"{dimension}.{dimension_key}"
                )

                record_result(
                    "foreign_keys",
                    f"{fact_name}.{fact_column}",
                    "PASS",
                    details,
                )

                print_result(
                    f"{fact_name}.{fact_column}",
                    "PASS",
                    f"→ {dimension}",
                )

            else:

                details = (
                    f"NULL={null_count:,}; "
                    f"Unmapped={len(missing):,}"
                )

                record_result(
                    "foreign_keys",
                    f"{fact_name}.{fact_column}",
                    "FAIL",
                    details,
                )

                print_result(
                    f"{fact_name}.{fact_column}",
                    "FAIL",
                    details,
                )


# ============================================================
# 7. DATE KEY VALIDATION
# ============================================================

def validate_date_keys(data):

    print("\nDATE KEY VALIDATION")
    print("-" * 90)

    date_keys = set(
        data["dim_date"][
            "date_key"
        ]
        .dropna()
        .astype(int)
    )

    for fact_name in FACTS:

        fact_df = data[fact_name]

        fact_date_keys = set(
            fact_df[
                "date_key"
            ]
            .dropna()
            .astype(int)
        )

        missing = (
            fact_date_keys
            - date_keys
        )

        null_count = (
            fact_df["date_key"]
            .isna()
            .sum()
        )

        if not missing and null_count == 0:

            record_result(
                "date_keys",
                fact_name,
                "PASS",
                "All date keys resolve to dim_date.",
            )

            print_result(
                fact_name,
                "PASS",
            )

        else:

            details = (
                f"NULL={null_count:,}; "
                f"Unmapped={len(missing):,}"
            )

            record_result(
                "date_keys",
                fact_name,
                "FAIL",
                details,
            )

            print_result(
                fact_name,
                "FAIL",
                details,
            )


# ============================================================
# 8. FACT GRAIN VALIDATION
# ============================================================

def validate_fact_grains(data):

    print("\nFACT GRAIN VALIDATION")
    print("-" * 90)

    for fact_name, source_key in FACT_SOURCE_KEYS.items():

        df = data[fact_name]

        duplicate_count = (
            df[source_key]
            .duplicated()
            .sum()
        )

        grain = FACT_GRAINS[
            fact_name
        ]

        if duplicate_count == 0:

            details = (
                f"{grain} "
                f"Source key unique."
            )

            record_result(
                "fact_grain",
                fact_name,
                "PASS",
                details,
            )

            print_result(
                fact_name,
                "PASS",
                "Source transaction grain preserved.",
            )

        else:

            details = (
                f"{duplicate_count:,} duplicate "
                f"source-key rows. Grain: {grain}"
            )

            record_result(
                "fact_grain",
                fact_name,
                "FAIL",
                details,
            )

            print_result(
                fact_name,
                "FAIL",
                details,
            )


# ============================================================
# 9. BUSINESS RELATIONSHIP VALIDATION
# ============================================================

def validate_business_relationships(data):

    print("\nBUSINESS RELATIONSHIP VALIDATION")
    print("-" * 90)

    # --------------------------------------------------------
    # Customer → Account
    # --------------------------------------------------------

    customers = data["dim_customer"]

    customer_accounts = (
        customers[
            [
                "customer_id",
                "account_id",
            ]
        ]
        .dropna()
    )

    duplicate_customer_relationships = (
        customer_accounts[
            "customer_id"
        ]
        .duplicated()
        .sum()
    )

    if duplicate_customer_relationships == 0:

        record_result(
            "business_rules",
            "customer_account",
            "PASS",
            "Each customer maps to one account.",
        )

        print_result(
            "Customer → Account",
            "PASS",
        )

    else:

        record_result(
            "business_rules",
            "customer_account",
            "FAIL",
            (
                f"{duplicate_customer_relationships:,} "
                "customers map to multiple accounts."
            ),
        )

        print_result(
            "Customer → Account",
            "FAIL",
        )

    # --------------------------------------------------------
    # Product → Supplier
    # --------------------------------------------------------

    products = data["dim_product"]

    product_supplier_nulls = (
        products["supplier_id"]
        .isna()
        .sum()
    )

    if product_supplier_nulls == 0:

        record_result(
            "business_rules",
            "product_supplier",
            "PASS",
            "Every product has a supplier.",
        )

        print_result(
            "Product → Supplier",
            "PASS",
        )

    else:

        record_result(
            "business_rules",
            "product_supplier",
            "FAIL",
            (
                f"{product_supplier_nulls:,} "
                "products have no supplier."
            ),
        )

        print_result(
            "Product → Supplier",
            "FAIL",
        )

    # --------------------------------------------------------
    # Machine → Location
    # --------------------------------------------------------

    machines = data["dim_machine"]

    machine_location_nulls = (
        machines["location_id"]
        .isna()
        .sum()
    )

    if machine_location_nulls == 0:

        record_result(
            "business_rules",
            "machine_location",
            "PASS",
            "Every machine has a location.",
        )

        print_result(
            "Machine → Location",
            "PASS",
        )

    else:

        record_result(
            "business_rules",
            "machine_location",
            "FAIL",
            (
                f"{machine_location_nulls:,} "
                "machines have no location."
            ),
        )

        print_result(
            "Machine → Location",
            "FAIL",
        )

    # --------------------------------------------------------
    # Employee → Location
    # --------------------------------------------------------

    employees = data["dim_employee"]

    employee_location_nulls = (
        employees["location_id"]
        .isna()
        .sum()
    )

    if employee_location_nulls == 0:

        record_result(
            "business_rules",
            "employee_location",
            "PASS",
            "Every employee has a location.",
        )

        print_result(
            "Employee → Location",
            "PASS",
        )

    else:

        record_result(
            "business_rules",
            "employee_location",
            "FAIL",
            (
                f"{employee_location_nulls:,} "
                "employees have no location."
            ),
        )

        print_result(
            "Employee → Location",
            "FAIL",
        )


# ============================================================
# 10. NUMERIC VALIDATION
# ============================================================

def validate_numeric_values(data):

    print("\nNUMERIC VALIDATION")
    print("-" * 90)

    numeric_columns = {
        "dim_product": [
            "unit_cost",
            "unit_price",
        ],

        "fact_sales": [
            "quantity",
            "unit_price",
            "discount_rate",
            "revenue",
        ],

        "fact_production": [
            "planned_quantity",
            "quantity_produced",
            "production_hours",
        ],

        "fact_maintenance": [
            "downtime_hours",
            "maintenance_cost",
        ],

        "fact_financial_transaction": [
            "amount",
        ],

        "fact_budget": [
            "budget_amount",
        ],

        "fact_energy": [
            "consumption",
        ],

        "fact_emissions": [
            "co2_kg",
        ],

        "fact_waste": [
            "quantity",
        ],

        "fact_inventory": [
            "quantity_on_hand",
            "reorder_point",
            "inventory_value",
        ],
    }

    for dataset, columns in numeric_columns.items():

        df = data[dataset]

        invalid = False

        for column in columns:

            series = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            invalid_numeric = (
                series.isna()
                & df[column].notna()
            ).sum()

            infinite_values = (
                series.isin(
                    [
                        float("inf"),
                        float("-inf"),
                    ]
                )
                .sum()
            )

            if (
                invalid_numeric > 0
                or infinite_values > 0
            ):

                invalid = True

                details = (
                    f"{column}: "
                    f"Invalid={invalid_numeric:,}; "
                    f"Infinite={infinite_values:,}"
                )

                record_result(
                    "numeric_validation",
                    f"{dataset}.{column}",
                    "FAIL",
                    details,
                )

                print_result(
                    f"{dataset}.{column}",
                    "FAIL",
                    details,
                )

        if not invalid:

            record_result(
                "numeric_validation",
                dataset,
                "PASS",
                "Numeric fields are valid.",
            )

            print_result(
                dataset,
                "PASS",
            )


# ============================================================
# 11. DATE VALIDATION
# ============================================================

def validate_dates(data):

    print("\nDATE VALIDATION")
    print("-" * 90)

    for dataset in WAREHOUSE_OBJECTS:

        df = data[dataset]

        date_columns = [
            column
            for column in [
                "date",
                "hire_date",
                "installation_date",
            ]
            if column in df.columns
        ]

        for column in date_columns:

            converted = pd.to_datetime(
                df[column],
                errors="coerce",
            )

            invalid = (
                converted.isna()
                & df[column].notna()
            ).sum()

            if invalid == 0:

                record_result(
                    "date_validation",
                    f"{dataset}.{column}",
                    "PASS",
                    "Date values are valid.",
                )

                print_result(
                    f"{dataset}.{column}",
                    "PASS",
                )

            else:

                record_result(
                    "date_validation",
                    f"{dataset}.{column}",
                    "FAIL",
                    f"Invalid dates={invalid:,}",
                )

                print_result(
                    f"{dataset}.{column}",
                    "FAIL",
                    f"Invalid={invalid:,}",
                )


# ============================================================
# 12. NULL VALIDATION ON REQUIRED KEYS
# ============================================================

def validate_required_keys(data):

    print("\nREQUIRED KEY COMPLETENESS")
    print("-" * 90)

    required_columns = {}

    for dimension, keys in DIMENSION_KEYS.items():

        required_columns[
            dimension
        ] = [
            keys["business_key"],
            keys["surrogate_key"],
        ]

    for fact_name, source_key in FACT_SOURCE_KEYS.items():

        required_columns[
            fact_name
        ] = [
            source_key,
        ] + list(
            FACT_FOREIGN_KEYS[
                fact_name
            ].keys()
        )

    for dataset, columns in required_columns.items():

        df = data[dataset]

        nulls = {
            column: int(
                df[column].isna().sum()
            )
            for column in columns
            if df[column].isna().sum() > 0
        }

        if not nulls:

            record_result(
                "required_keys",
                dataset,
                "PASS",
                "Required keys are complete.",
            )

            print_result(
                dataset,
                "PASS",
            )

        else:

            details = str(nulls)

            record_result(
                "required_keys",
                dataset,
                "FAIL",
                details,
            )

            print_result(
                dataset,
                "FAIL",
                details,
            )


# ============================================================
# 13. DATE DIMENSION VALIDATION
# ============================================================

def validate_date_dimension(data):

    print("\nDATE DIMENSION VALIDATION")
    print("-" * 90)

    df = data["dim_date"]

    checks = []

    # Date key uniqueness
    checks.append(
        df["date_key"].is_unique
    )

    # Date uniqueness
    checks.append(
        df["date"].is_unique
    )

    # Date key format
    expected_keys = (
        pd.to_datetime(
            df["date"],
            errors="raise",
        )
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    checks.append(
        (expected_keys == df["date_key"]).all()
    )

    # Calendar continuity
    dates = pd.to_datetime(
        df["date"],
        errors="raise",
    ).sort_values()

    expected_range = pd.date_range(
        dates.min(),
        dates.max(),
        freq="D",
    )

    checks.append(
        len(dates) == len(expected_range)
    )

    checks.append(
        dates.reset_index(drop=True).equals(
            expected_range.to_series(
                index=range(
                    len(expected_range)
                )
            )
            .reset_index(drop=True)
        )
    )

    if all(checks):

        record_result(
            "date_dimension",
            "dim_date",
            "PASS",
            "Date dimension is unique, correctly keyed and continuous.",
        )

        print_result(
            "dim_date",
            "PASS",
        )

    else:

        record_result(
            "date_dimension",
            "dim_date",
            "FAIL",
            "Date dimension validation failed.",
        )

        print_result(
            "dim_date",
            "FAIL",
        )


# ============================================================
# 14. FACT DATE COVERAGE
# ============================================================

def validate_fact_date_coverage(data):

    print("\nFACT DATE COVERAGE")
    print("-" * 90)

    date_dimension = pd.to_datetime(
        data["dim_date"]["date"],
        errors="raise",
    )

    min_date = date_dimension.min()
    max_date = date_dimension.max()

    for fact_name in FACTS:

        fact_dates = pd.to_datetime(
            data[fact_name]["date"],
            errors="coerce",
        )

        invalid = (
            fact_dates.isna()
            | (fact_dates < min_date)
            | (fact_dates > max_date)
        ).sum()

        if invalid == 0:

            record_result(
                "fact_date_coverage",
                fact_name,
                "PASS",
                (
                    f"Dates within {min_date.date()} "
                    f"to {max_date.date()}."
                ),
            )

            print_result(
                fact_name,
                "PASS",
            )

        else:

            record_result(
                "fact_date_coverage",
                fact_name,
                "FAIL",
                f"Invalid/out-of-range dates={invalid:,}",
            )

            print_result(
                fact_name,
                "FAIL",
                f"Invalid={invalid:,}",
            )


# ============================================================
# 15. CUSTOMER → ACCOUNT FACT CONSISTENCY
# ============================================================

def validate_sales_customer_account(data):

    print("\nSALES CUSTOMER → ACCOUNT CONSISTENCY")
    print("-" * 90)

    sales = data["fact_sales"]

    customers = data["dim_customer"][
        [
            "customer_id",
            "account_id",
        ]
    ]

    merged = sales[
        [
            "customer_id",
            "account_id",
        ]
    ].merge(
        customers,
        on="customer_id",
        how="left",
        suffixes=(
            "_sales",
            "_customer",
        ),
        validate="many_to_one",
    )

    mismatches = (
        merged["account_id_sales"]
        != merged["account_id_customer"]
    ).sum()

    if mismatches == 0:

        record_result(
            "business_rules",
            "sales_customer_account",
            "PASS",
            "Sales customer/account relationships are consistent.",
        )

        print_result(
            "Sales Customer → Account",
            "PASS",
        )

    else:

        record_result(
            "business_rules",
            "sales_customer_account",
            "FAIL",
            f"Mismatches={mismatches:,}",
        )

        print_result(
            "Sales Customer → Account",
            "FAIL",
            f"Mismatches={mismatches:,}",
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

def final_summary():

    total_checks = len(results)

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    failed = sum(
        result["status"] == "FAIL"
        for result in results
    )

    print("\n" + "=" * 90)

    print(
        "PHASE 5 ETL VALIDATION SUMMARY"
    )

    print("=" * 90)

    print(
        f"Total checks: {total_checks:,}"
    )

    print(
        f"Passed:       {passed:,}"
    )

    print(
        f"Failed:       {failed:,}"
    )

    print("-" * 90)

    if failed == 0:

        status = "SUCCESS"

        print(
            "PHASE 5 ETL VALIDATION: SUCCESS"
        )

    else:

        status = "FAILED"

        print(
            "PHASE 5 ETL VALIDATION: FAILED"
        )

        print(
            "\nIMPORTANT: "
            "Do not proceed to Phase 6 until all "
            "validation failures are resolved."
        )

    print("=" * 90)

    return status


# ============================================================
# LOG RESULTS
# ============================================================

def write_validation_log(status):

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    log_file = (
        LOG_DIR
        / f"validation_{timestamp}.json"
    )

    payload = {
        "pipeline_stage":
            "warehouse_ready_validation",

        "timestamp_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "status":
            status,

        "results":
            results,
    }

    log_file.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    return log_file


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 90)
    print(
        "Project Atlas — Phase 5 ETL — "
        "Warehouse-Ready Validation"
    )
    print("=" * 90)

    print(
        f"\nWarehouse-ready directory:\n"
        f"{WAREHOUSE_READY_DIR}"
    )

    # --------------------------------------------------------
    # Object existence
    # --------------------------------------------------------

    validate_object_existence()

    failed_objects = [
        result
        for result in results
        if (
            result["category"] == "object_existence"
            and result["status"] == "FAIL"
        )
    ]

    if failed_objects:

        status = final_summary()

        log_file = write_validation_log(
            status
        )

        print(
            f"\nValidation log:\n{log_file}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Load objects
    # --------------------------------------------------------

    data = load_warehouse_ready()

    # --------------------------------------------------------
    # Run validations
    # --------------------------------------------------------

    validate_structure(data)

    validate_row_counts(data)

    validate_dimension_keys(data)

    validate_fact_source_keys(data)

    validate_foreign_keys(data)

    validate_date_keys(data)

    validate_fact_grains(data)

    validate_business_relationships(data)

    validate_numeric_values(data)

    validate_dates(data)

    validate_required_keys(data)

    validate_date_dimension(data)

    validate_fact_date_coverage(data)

    validate_sales_customer_account(data)

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    status = final_summary()

    log_file = write_validation_log(
        status
    )

    print(
        f"\nValidation log:\n{log_file}"
    )

    if status != "SUCCESS":
        sys.exit(1)


if __name__ == "__main__":
    main()