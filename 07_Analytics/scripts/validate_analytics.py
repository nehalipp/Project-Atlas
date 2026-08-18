"""
Project Atlas — Phase 7.4
Analytics Validation

Purpose
-------
Validate the PostgreSQL analytics layer against the warehouse.

Validation areas
----------------
1. Database connectivity
2. Required analytics views
3. KPI view population
4. KPI date coverage
5. Core KPI reconciliation
6. Domain analytics reconciliation
7. Cross-domain reconciliation
8. Cross-domain grain uniqueness
9. Cross-domain view population
10. Final PASS / FAIL status

Usage
-----
python3 07_Analytics/scripts/validate_analytics.py

Database connection
-------------------
The script supports the following environment variables:

    DATABASE_URL

or individual PostgreSQL variables:

    PGHOST
    PGPORT
    PGDATABASE
    PGUSER
    PGPASSWORD

Example:

    export PGHOST=localhost
    export PGPORT=5432
    export PGDATABASE=atlas_warehouse
    export PGUSER=postgres
    export PGPASSWORD=your_password

Then:

    python3 07_Analytics/scripts/validate_analytics.py
"""

from __future__ import annotations

import os
import sys
from decimal import Decimal
from typing import Any

import psycopg2


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_START_DATE = "2019-01-01"
EXPECTED_END_DATE = "2025-12-31"

NUMERIC_TOLERANCE = Decimal("0.01")


REQUIRED_VIEWS = [
    # --------------------------------------------------------
    # KPI views
    # --------------------------------------------------------
    "vw_sales_kpis_daily",
    "vw_production_kpis_daily",
    "vw_maintenance_kpis_daily",
    "vw_financial_kpis_daily",
    "vw_budget_kpis_daily",
    "vw_energy_kpis_daily",
    "vw_emissions_kpis_daily",
    "vw_waste_kpis_daily",
    "vw_inventory_kpis_daily",

    # --------------------------------------------------------
    # Domain analytics views
    # --------------------------------------------------------
    "vw_account_sales_daily",
    "vw_customer_sales_daily",
    "vw_product_sales_daily",
    "vw_supplier_sales_daily",
    "vw_location_sales_daily",
    "vw_production_performance_daily",
    "vw_machine_production_daily",
    "vw_maintenance_performance_daily",
    "vw_employee_operations_daily",
    "vw_financial_performance_daily",
    "vw_budget_performance_daily",
    "vw_energy_performance_daily",
    "vw_emissions_performance_daily",
    "vw_waste_performance_daily",
    "vw_inventory_position_daily",

    # --------------------------------------------------------
    # Cross-domain analytics views
    # --------------------------------------------------------
    "vw_sales_production_inventory_daily",
    "vw_production_maintenance_daily",
    "vw_production_energy_emissions_daily",
]


KPI_VIEWS = [
    "vw_sales_kpis_daily",
    "vw_production_kpis_daily",
    "vw_maintenance_kpis_daily",
    "vw_financial_kpis_daily",
    "vw_budget_kpis_daily",
    "vw_energy_kpis_daily",
    "vw_emissions_kpis_daily",
    "vw_waste_kpis_daily",
    "vw_inventory_kpis_daily",
]


CROSS_DOMAIN_VIEWS = [
    "vw_sales_production_inventory_daily",
    "vw_production_maintenance_daily",
    "vw_production_energy_emissions_daily",
]


# ============================================================
# OUTPUT HELPERS
# ============================================================

PASS_COUNT = 0
FAIL_COUNT = 0
CHECK_COUNT = 0


def print_header(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)


def record_pass(message: str) -> None:
    """Record and print a successful validation."""
    global PASS_COUNT

    PASS_COUNT += 1
    print(f"[PASS] {message}")


def record_fail(message: str) -> None:
    """Record and print a failed validation."""
    global FAIL_COUNT

    FAIL_COUNT += 1
    print(f"[FAIL] {message}")


def record_check(message: str) -> None:
    """Record and print an informational validation check."""
    global CHECK_COUNT

    CHECK_COUNT += 1
    print(f"[CHECK] {message}")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a PostgreSQL connection.

    Supports DATABASE_URL or standard PostgreSQL
    environment variables.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    connection_parameters = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE"),
        "user": os.getenv("PGUSER"),
        "password": os.getenv("PGPASSWORD"),
    }

    missing = [
        key
        for key, value in connection_parameters.items()
        if key in {"dbname", "user", "password"} and not value
    ]

    if missing:
        raise RuntimeError(
            "Missing PostgreSQL connection settings: "
            + ", ".join(missing)
            + ". Set DATABASE_URL or PGDATABASE/PGUSER/PGPASSWORD."
        )

    return psycopg2.connect(**connection_parameters)


# ============================================================
# SQL HELPERS
# ============================================================

def execute_scalar(cursor, sql: str) -> Any:
    """
    Execute SQL and return the first column of the first row.
    """

    cursor.execute(sql)

    result = cursor.fetchone()

    if result is None:
        return None

    return result[0]


def execute_row(cursor, sql: str) -> tuple:
    """
    Execute SQL and return the first row.
    """

    cursor.execute(sql)

    result = cursor.fetchone()

    if result is None:
        return tuple()

    return result


def decimal_value(value: Any) -> Decimal:
    """
    Convert numeric database values safely to Decimal.
    """

    if value is None:
        return Decimal("0")

    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def values_match(
    warehouse_value: Any,
    analytics_value: Any,
    tolerance: Decimal = NUMERIC_TOLERANCE,
) -> bool:
    """
    Return True when two numeric values reconcile
    within the configured tolerance.
    """

    warehouse_decimal = decimal_value(warehouse_value)
    analytics_decimal = decimal_value(analytics_value)

    return abs(warehouse_decimal - analytics_decimal) <= tolerance


# ============================================================
# VALIDATION 1 — DATABASE CONNECTION
# ============================================================

def validate_connection(connection) -> None:
    """Validate database connectivity."""

    print_header("1. DATABASE CONNECTIVITY")

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                current_database(),
                current_schema();
            """
        )

        database_name, schema_name = cursor.fetchone()

    record_pass(
        f"Connected to database '{database_name}' "
        f"with current schema '{schema_name}'."
    )


# ============================================================
# VALIDATION 2 — REQUIRED ANALYTICS VIEWS
# ============================================================

def validate_required_views(connection) -> None:
    """Validate that all required analytics views exist."""

    print_header("2. REQUIRED ANALYTICS VIEWS")

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'analytics';
            """
        )

        existing_views = {
            row[0]
            for row in cursor.fetchall()
        }

    missing_views = [
        view_name
        for view_name in REQUIRED_VIEWS
        if view_name not in existing_views
    ]

    for view_name in REQUIRED_VIEWS:

        if view_name in existing_views:

            record_pass(
                f"analytics.{view_name} exists."
            )

        else:

            record_fail(
                f"analytics.{view_name} is missing."
            )

    if missing_views:

        raise RuntimeError(
            "Required analytics views are missing: "
            + ", ".join(missing_views)
        )


# ============================================================
# VALIDATION 3 — KPI VIEW POPULATION
# ============================================================

def validate_kpi_population(connection) -> None:
    """Validate that every KPI view contains records."""

    print_header("3. KPI VIEW POPULATION")

    with connection.cursor() as cursor:

        for view_name in KPI_VIEWS:

            sql = f"""
                SELECT COUNT(*)
                FROM analytics.{view_name};
            """

            row_count = execute_scalar(
                cursor,
                sql,
            )

            if row_count and row_count > 0:

                record_pass(
                    f"{view_name}: {row_count:,} rows."
                )

            else:

                record_fail(
                    f"{view_name}: zero rows."
                )


# ============================================================
# VALIDATION 4 — KPI DATE COVERAGE
# ============================================================

def validate_kpi_date_coverage(connection) -> None:
    """
    Validate date ranges for KPI views.

    Some operational facts begin later than the overall
    warehouse date range. Those views are reported as
    informational CHECK items rather than failures.
    """

    print_header("4. KPI DATE COVERAGE")

    with connection.cursor() as cursor:

        for view_name in KPI_VIEWS:

            sql = f"""
                SELECT
                    COUNT(*),
                    MIN(date),
                    MAX(date)
                FROM analytics.{view_name};
            """

            row_count, min_date, max_date = execute_row(
                cursor,
                sql,
            )

            if row_count == 0:

                record_fail(
                    f"{view_name}: no rows available "
                    "for date validation."
                )

                continue

            min_date_text = str(min_date)
            max_date_text = str(max_date)

            if (
                min_date_text == EXPECTED_START_DATE
                and max_date_text == EXPECTED_END_DATE
            ):

                record_pass(
                    f"{view_name}: "
                    f"{min_date_text} → {max_date_text}."
                )

            else:

                record_check(
                    f"{view_name}: "
                    f"{min_date_text} → {max_date_text} "
                    f"(expected overall warehouse range "
                    f"{EXPECTED_START_DATE} → "
                    f"{EXPECTED_END_DATE})."
                )


# ============================================================
# GENERIC RECONCILIATION
# ============================================================

def validate_reconciliation(
    connection,
    metric: str,
    warehouse_sql: str,
    analytics_sql: str,
) -> bool:
    """
    Compare a warehouse aggregate with an analytics aggregate.
    """

    with connection.cursor() as cursor:

        warehouse_value = execute_scalar(
            cursor,
            warehouse_sql,
        )

        analytics_value = execute_scalar(
            cursor,
            analytics_sql,
        )

    if values_match(
        warehouse_value,
        analytics_value,
    ):

        difference = (
            decimal_value(analytics_value)
            - decimal_value(warehouse_value)
        )

        record_pass(
            f"{metric}: "
            f"warehouse={warehouse_value}, "
            f"analytics={analytics_value}, "
            f"difference={difference}."
        )

        return True

    difference = (
        decimal_value(analytics_value)
        - decimal_value(warehouse_value)
    )

    record_fail(
        f"{metric}: "
        f"warehouse={warehouse_value}, "
        f"analytics={analytics_value}, "
        f"difference={difference}."
    )

    return False


# ============================================================
# VALIDATION 5 — CORE KPI RECONCILIATION
# ============================================================

def validate_core_kpis(connection) -> None:
    """Validate core KPI analytics against warehouse facts."""

    print_header("5. CORE KPI RECONCILIATION")

    validations = [

        # ----------------------------------------------------
        # Sales
        # ----------------------------------------------------
        (
            "sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_sales_kpis_daily;
            """,
        ),

        # ----------------------------------------------------
        # Production
        # ----------------------------------------------------
        (
            "production quantity",

            """
            SELECT SUM(quantity_produced)
            FROM public.fact_production;
            """,

            """
            SELECT SUM(quantity_produced)
            FROM analytics.vw_production_kpis_daily;
            """,
        ),

        # ----------------------------------------------------
        # Maintenance
        # ----------------------------------------------------
        (
            "maintenance cost",

            """
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance;
            """,

            """
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_maintenance_kpis_daily;
            """,
        ),

        # ----------------------------------------------------
        # Energy
        #
        # Actual KPI view column:
        # total_energy_consumption_kwh
        # ----------------------------------------------------
        (
            "energy consumption kWh",

            """
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh';
            """,

            """
            SELECT SUM(total_energy_consumption_kwh)
            FROM analytics.vw_energy_kpis_daily;
            """,
        ),

        # ----------------------------------------------------
        # Emissions
        #
        # Actual KPI view column:
        # total_co2_kg
        # ----------------------------------------------------
        (
            "CO2 emissions kg",

            """
            SELECT SUM(co2_kg)
            FROM public.fact_emissions;
            """,

            """
            SELECT SUM(total_co2_kg)
            FROM analytics.vw_emissions_kpis_daily;
            """,
        ),

        # ----------------------------------------------------
        # Waste
        #
        # Actual KPI view column:
        # total_waste_kg
        # ----------------------------------------------------
        (
            "waste kg",

            """
            SELECT SUM(quantity)
            FROM public.fact_waste
            WHERE unit = 'kg';
            """,

            """
            SELECT SUM(total_waste_kg)
            FROM analytics.vw_waste_kpis_daily;
            """,
        ),
    ]

    for metric, warehouse_sql, analytics_sql in validations:

        validate_reconciliation(
            connection,
            metric,
            warehouse_sql,
            analytics_sql,
        )


# ============================================================
# VALIDATION 6 — DOMAIN ANALYTICS
# ============================================================

def validate_domain_analytics(connection) -> None:
    """Validate domain analytics against warehouse facts."""

    print_header("6. DOMAIN ANALYTICS RECONCILIATION")

    validations = [

        # ----------------------------------------------------
        # Account Sales
        # ----------------------------------------------------
        (
            "account sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_account_sales_daily;
            """,
        ),

        # ----------------------------------------------------
        # Customer Sales
        # ----------------------------------------------------
        (
            "customer sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_customer_sales_daily;
            """,
        ),

        # ----------------------------------------------------
        # Product Sales
        # ----------------------------------------------------
        (
            "product sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_product_sales_daily;
            """,
        ),

        # ----------------------------------------------------
        # Supplier Sales
        # ----------------------------------------------------
        (
            "supplier sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_supplier_sales_daily;
            """,
        ),

        # ----------------------------------------------------
        # Location Sales
        # ----------------------------------------------------
        (
            "location sales revenue",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(total_revenue)
            FROM analytics.vw_location_sales_daily;
            """,
        ),

        # ----------------------------------------------------
        # Production Performance
        # ----------------------------------------------------
        (
            "production performance quantity",

            """
            SELECT SUM(quantity_produced)
            FROM public.fact_production;
            """,

            """
            SELECT SUM(quantity_produced)
            FROM analytics.vw_production_performance_daily;
            """,
        ),

        # ----------------------------------------------------
        # Machine Production
        # ----------------------------------------------------
        (
            "machine production quantity",

            """
            SELECT SUM(quantity_produced)
            FROM public.fact_production;
            """,

            """
            SELECT SUM(quantity_produced)
            FROM analytics.vw_machine_production_daily;
            """,
        ),

        # ----------------------------------------------------
        # Maintenance Performance
        # ----------------------------------------------------
        (
            "maintenance performance cost",

            """
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance;
            """,

            """
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_maintenance_performance_daily;
            """,
        ),

        # ----------------------------------------------------
        # Energy Performance
        #
        # Domain view uses energy_consumption.
        # This is intentionally different from the core KPI
        # view, which uses total_energy_consumption_kwh.
        # ----------------------------------------------------
        (
            "energy performance kWh",

            """
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh';
            """,

            """
            SELECT SUM(energy_consumption)
            FROM analytics.vw_energy_performance_daily
            WHERE unit = 'kWh';
            """,
        ),

        # ----------------------------------------------------
        # Emissions Performance
        # ----------------------------------------------------
        (
            "emissions performance kg",

            """
            SELECT SUM(co2_kg)
            FROM public.fact_emissions;
            """,

            """
            SELECT SUM(co2_kg)
            FROM analytics.vw_emissions_performance_daily;
            """,
        ),

        # ----------------------------------------------------
        # Waste Performance
        # ----------------------------------------------------
        (
            "waste performance kg",

            """
            SELECT SUM(quantity)
            FROM public.fact_waste
            WHERE unit = 'kg';
            """,

            """
            SELECT SUM(waste_quantity)
            FROM analytics.vw_waste_performance_daily
            WHERE unit = 'kg';
            """,
        ),
    ]

    for metric, warehouse_sql, analytics_sql in validations:

        validate_reconciliation(
            connection,
            metric,
            warehouse_sql,
            analytics_sql,
        )


# ============================================================
# VALIDATION 7 — CROSS-DOMAIN ANALYTICS
# ============================================================

def validate_cross_domain_analytics(connection) -> None:
    """
    Validate cross-domain analytical views.

    Each reconciliation validates a measure against its
    corresponding warehouse fact aggregate.
    """

    print_header("7. CROSS-DOMAIN RECONCILIATION")

    validations = [

        # ----------------------------------------------------
        # Sales + Production + Inventory
        # ----------------------------------------------------
        (
            "sales revenue — Sales + Production + Inventory",

            """
            SELECT SUM(revenue)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(sales_revenue)
            FROM analytics.vw_sales_production_inventory_daily;
            """,
        ),

        (
            "sales quantity — Sales + Production + Inventory",

            """
            SELECT SUM(quantity)
            FROM public.fact_sales;
            """,

            """
            SELECT SUM(sales_quantity)
            FROM analytics.vw_sales_production_inventory_daily;
            """,
        ),

        (
            "production quantity — Sales + Production + Inventory",

            """
            SELECT SUM(quantity_produced)
            FROM public.fact_production;
            """,

            """
            SELECT SUM(production_quantity)
            FROM analytics.vw_sales_production_inventory_daily;
            """,
        ),

        # ----------------------------------------------------
        # Production + Maintenance
        # ----------------------------------------------------
        (
            "production quantity — Production + Maintenance",

            """
            SELECT SUM(quantity_produced)
            FROM public.fact_production;
            """,

            """
            SELECT SUM(production_quantity)
            FROM analytics.vw_production_maintenance_daily;
            """,
        ),

        (
            "maintenance cost — Production + Maintenance",

            """
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance;
            """,

            """
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_production_maintenance_daily;
            """,
        ),

        (
            "maintenance downtime — Production + Maintenance",

            """
            SELECT SUM(downtime_hours)
            FROM public.fact_maintenance;
            """,

            """
            SELECT SUM(downtime_hours)
            FROM analytics.vw_production_maintenance_daily;
            """,
        ),

        # ----------------------------------------------------
        # Production + Energy + Emissions
        # ----------------------------------------------------
        (
            "energy kWh — Production + Energy + Emissions",

            """
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh';
            """,

            """
            SELECT SUM(energy_consumption_kwh)
            FROM analytics.vw_production_energy_emissions_daily;
            """,
        ),

        (
            "CO2 kg — Production + Energy + Emissions",

            """
            SELECT SUM(co2_kg)
            FROM public.fact_emissions;
            """,

            """
            SELECT SUM(co2_kg)
            FROM analytics.vw_production_energy_emissions_daily;
            """,
        ),
    ]

    for metric, warehouse_sql, analytics_sql in validations:

        validate_reconciliation(
            connection,
            metric,
            warehouse_sql,
            analytics_sql,
        )


# ============================================================
# VALIDATION 8 — CROSS-DOMAIN GRAIN UNIQUENESS
# ============================================================

def validate_cross_domain_grains(connection) -> None:
    """
    Validate that each cross-domain analytical view has
    exactly one row per governed analytical grain.
    """

    print_header("8. CROSS-DOMAIN GRAIN VALIDATION")

    validations = [

        # ----------------------------------------------------
        # Sales + Production + Inventory
        # Grain:
        # date_key + location_key + product_key
        # ----------------------------------------------------
        (
            "Sales + Production + Inventory",

            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    date_key,
                    location_key,
                    product_key
                FROM analytics.vw_sales_production_inventory_daily
                GROUP BY
                    date_key,
                    location_key,
                    product_key
                HAVING COUNT(*) > 1
            ) duplicate_grains;
            """,
        ),

        # ----------------------------------------------------
        # Production + Maintenance
        # Grain:
        # date_key + location_key + machine_key
        # ----------------------------------------------------
        (
            "Production + Maintenance",

            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    date_key,
                    location_key,
                    machine_key
                FROM analytics.vw_production_maintenance_daily
                GROUP BY
                    date_key,
                    location_key,
                    machine_key
                HAVING COUNT(*) > 1
            ) duplicate_grains;
            """,
        ),

        # ----------------------------------------------------
        # Production + Energy + Emissions
        # Grain:
        # date_key + location_key
        # ----------------------------------------------------
        (
            "Production + Energy + Emissions",

            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    date_key,
                    location_key
                FROM analytics.vw_production_energy_emissions_daily
                GROUP BY
                    date_key,
                    location_key
                HAVING COUNT(*) > 1
            ) duplicate_grains;
            """,
        ),
    ]

    with connection.cursor() as cursor:

        for analytical_grain, sql in validations:

            duplicate_groups = execute_scalar(
                cursor,
                sql,
            )

            if duplicate_groups == 0:

                record_pass(
                    f"{analytical_grain}: "
                    "no duplicate analytical grain groups."
                )

            else:

                record_fail(
                    f"{analytical_grain}: "
                    f"{duplicate_groups} duplicate grain groups found."
                )


# ============================================================
# VALIDATION 9 — CROSS-DOMAIN VIEW POPULATION
# ============================================================

def validate_cross_domain_population(connection) -> None:
    """Validate that all cross-domain views contain records."""

    print_header("9. CROSS-DOMAIN VIEW POPULATION")

    with connection.cursor() as cursor:

        for view_name in CROSS_DOMAIN_VIEWS:

            row_count = execute_scalar(
                cursor,
                f"""
                SELECT COUNT(*)
                FROM analytics.{view_name};
                """,
            )

            if row_count and row_count > 0:

                record_pass(
                    f"{view_name}: {row_count:,} rows."
                )

            else:

                record_fail(
                    f"{view_name}: zero rows."
                )


# ============================================================
# FINAL SUMMARY
# ============================================================

def print_summary() -> None:
    """Print the final validation summary."""

    print_header(
        "FINAL ANALYTICS VALIDATION SUMMARY"
    )

    print(f"PASS checks : {PASS_COUNT}")
    print(f"FAIL checks : {FAIL_COUNT}")
    print(f"CHECK items : {CHECK_COUNT}")

    if FAIL_COUNT == 0:

        print()
        print("=" * 90)
        print(
            "PROJECT ATLAS — PHASE 7 ANALYTICS VALIDATION: PASS"
        )
        print("=" * 90)
        print()

        print(
            "The analytics layer passed all automated "
            "validation checks."
        )

        print(
            "Warehouse measures reconcile with KPI, "
            "domain, and cross-domain analytics."
        )

        print(
            "Cross-domain analytical grains contain no "
            "duplicate grain groups."
        )

        print()

    else:

        print()
        print("=" * 90)
        print(
            "PROJECT ATLAS — PHASE 7 ANALYTICS VALIDATION: FAIL"
        )
        print("=" * 90)
        print()

        print(
            "One or more analytics validation checks failed."
        )

        print(
            "Resolve the failures before proceeding to Phase 8."
        )

        print()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run the complete analytics validation."""

    print("=" * 90)
    print(
        "Project Atlas — Phase 7 Analytics Validation"
    )
    print("=" * 90)

    connection = None

    try:

        # ----------------------------------------------------
        # Database connection
        # ----------------------------------------------------

        try:

            connection = get_connection()

        except Exception as exc:

            print()
            print(
                "[FAIL] Database connection failed."
            )

            print(
                f"       {exc}"
            )

            return 1

        # ----------------------------------------------------
        # Validation sequence
        # ----------------------------------------------------

        validate_connection(
            connection
        )

        validate_required_views(
            connection
        )

        validate_kpi_population(
            connection
        )

        validate_kpi_date_coverage(
            connection
        )

        validate_core_kpis(
            connection
        )

        validate_domain_analytics(
            connection
        )

        validate_cross_domain_analytics(
            connection
        )

        validate_cross_domain_grains(
            connection
        )

        validate_cross_domain_population(
            connection
        )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        print_summary()

        if FAIL_COUNT > 0:

            return 1

        return 0

    except Exception as exc:

        print()
        print("=" * 90)
        print(
            "UNEXPECTED VALIDATION ERROR"
        )
        print("=" * 90)

        print(
            str(exc)
        )

        print()

        return 1

    finally:

        if connection is not None:

            connection.close()


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )