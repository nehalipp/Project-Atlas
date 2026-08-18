-- ============================================================
-- Project Atlas — Phase 7.4
-- Analytics — Final Validation
--
-- Purpose:
-- Validate the complete reusable analytics layer against the
-- PostgreSQL warehouse.
--
-- Validation areas:
--   1. Required analytics views
--   2. KPI view population
--   3. KPI date coverage
--   4. Warehouse-to-KPI reconciliation
--   5. Domain analytics reconciliation
--   6. Cross-domain reconciliation
--   7. Cross-domain grain uniqueness
--   8. Fan-out / double-counting protection
--
-- Expected result:
-- All validation queries should return PASS / zero discrepancy.
--
-- This script does not create or modify warehouse data.
-- ============================================================


-- ============================================================
-- 1. REQUIRED ANALYTICS VIEWS
-- ============================================================

WITH required_views(view_name) AS (
    VALUES
        ('vw_sales_kpis_daily'),
        ('vw_production_kpis_daily'),
        ('vw_maintenance_kpis_daily'),
        ('vw_financial_kpis_daily'),
        ('vw_budget_kpis_daily'),
        ('vw_energy_kpis_daily'),
        ('vw_emissions_kpis_daily'),
        ('vw_waste_kpis_daily'),
        ('vw_inventory_kpis_daily'),

        ('vw_account_sales_daily'),
        ('vw_customer_sales_daily'),
        ('vw_product_sales_daily'),
        ('vw_supplier_sales_daily'),
        ('vw_location_sales_daily'),
        ('vw_production_performance_daily'),
        ('vw_machine_production_daily'),
        ('vw_maintenance_performance_daily'),
        ('vw_employee_operations_daily'),
        ('vw_financial_performance_daily'),
        ('vw_budget_performance_daily'),
        ('vw_energy_performance_daily'),
        ('vw_emissions_performance_daily'),
        ('vw_waste_performance_daily'),
        ('vw_inventory_position_daily'),

        ('vw_sales_production_inventory_daily'),
        ('vw_production_maintenance_daily'),
        ('vw_production_energy_emissions_daily')
)

SELECT
    rv.view_name,
    CASE
        WHEN v.table_name IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM required_views rv
LEFT JOIN information_schema.views v
    ON v.table_schema = 'analytics'
   AND v.table_name = rv.view_name
ORDER BY rv.view_name;


-- ============================================================
-- 2. KPI VIEW POPULATION
-- ============================================================

SELECT
    view_name,
    row_count,
    CASE
        WHEN row_count > 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM (
    SELECT
        'vw_sales_kpis_daily' AS view_name,
        COUNT(*) AS row_count
    FROM analytics.vw_sales_kpis_daily

    UNION ALL

    SELECT
        'vw_production_kpis_daily',
        COUNT(*)
    FROM analytics.vw_production_kpis_daily

    UNION ALL

    SELECT
        'vw_maintenance_kpis_daily',
        COUNT(*)
    FROM analytics.vw_maintenance_kpis_daily

    UNION ALL

    SELECT
        'vw_financial_kpis_daily',
        COUNT(*)
    FROM analytics.vw_financial_kpis_daily

    UNION ALL

    SELECT
        'vw_budget_kpis_daily',
        COUNT(*)
    FROM analytics.vw_budget_kpis_daily

    UNION ALL

    SELECT
        'vw_energy_kpis_daily',
        COUNT(*)
    FROM analytics.vw_energy_kpis_daily

    UNION ALL

    SELECT
        'vw_emissions_kpis_daily',
        COUNT(*)
    FROM analytics.vw_emissions_kpis_daily

    UNION ALL

    SELECT
        'vw_waste_kpis_daily',
        COUNT(*)
    FROM analytics.vw_waste_kpis_daily

    UNION ALL

    SELECT
        'vw_inventory_kpis_daily',
        COUNT(*)
    FROM analytics.vw_inventory_kpis_daily
) x
ORDER BY view_name;


-- ============================================================
-- 3. KPI DATE COVERAGE
-- ============================================================

SELECT
    view_name,
    row_count,
    min_date,
    max_date,
    CASE
        WHEN row_count > 0
         AND min_date = DATE '2019-01-01'
         AND max_date = DATE '2025-12-31'
        THEN 'PASS'
        ELSE 'CHECK'
    END AS validation_status
FROM (
    SELECT
        'sales' AS view_name,
        COUNT(*) AS row_count,
        MIN(date) AS min_date,
        MAX(date) AS max_date
    FROM analytics.vw_sales_kpis_daily

    UNION ALL

    SELECT
        'production',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_production_kpis_daily

    UNION ALL

    SELECT
        'maintenance',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_maintenance_kpis_daily

    UNION ALL

    SELECT
        'financial',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_financial_kpis_daily

    UNION ALL

    SELECT
        'budget',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_budget_kpis_daily

    UNION ALL

    SELECT
        'energy',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_energy_kpis_daily

    UNION ALL

    SELECT
        'emissions',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_emissions_kpis_daily

    UNION ALL

    SELECT
        'waste',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_waste_kpis_daily

    UNION ALL

    SELECT
        'inventory',
        COUNT(*),
        MIN(date),
        MAX(date)
    FROM analytics.vw_inventory_kpis_daily
) x
ORDER BY view_name;


-- ============================================================
-- 4. CORE KPI RECONCILIATION
-- ============================================================

SELECT
    metric,
    warehouse_value,
    analytics_value,
    analytics_value - warehouse_value AS difference,
    CASE
        WHEN ABS(
            COALESCE(analytics_value, 0)
            -
            COALESCE(warehouse_value, 0)
        ) < 0.01
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM (
    SELECT
        'sales_revenue' AS metric,

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric AS warehouse_value,

        (
            SELECT SUM(total_revenue)
            FROM analytics.vw_sales_kpis_daily
        )::numeric AS analytics_value

    UNION ALL

    SELECT
        'production_quantity',

        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,

        (
            SELECT SUM(quantity_produced)
            FROM analytics.vw_production_kpis_daily
        )::numeric

    UNION ALL

    SELECT
        'maintenance_cost',

        (
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance
        )::numeric,

        (
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_maintenance_kpis_daily
        )::numeric

    UNION ALL

    SELECT
        'energy_kwh',

        (
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh'
        )::numeric,

        (
            SELECT SUM(energy_consumption)
            FROM analytics.vw_energy_kpis_daily
            WHERE unit = 'kWh'
        )::numeric

    UNION ALL

    SELECT
        'co2_kg',

        (
            SELECT SUM(co2_kg)
            FROM public.fact_emissions
        )::numeric,

        (
            SELECT SUM(co2_kg)
            FROM analytics.vw_emissions_kpis_daily
        )::numeric

    UNION ALL

    SELECT
        'waste_kg',

        (
            SELECT SUM(quantity)
            FROM public.fact_waste
            WHERE unit = 'kg'
        )::numeric,

        (
            SELECT SUM(waste_quantity)
            FROM analytics.vw_waste_kpis_daily
            WHERE unit = 'kg'
        )::numeric
) x
ORDER BY metric;


-- ============================================================
-- 5. DOMAIN ANALYTICS RECONCILIATION
-- ============================================================

SELECT
    metric,
    warehouse_value,
    analytics_value,
    analytics_value - warehouse_value AS difference,
    CASE
        WHEN ABS(
            COALESCE(analytics_value, 0)
            -
            COALESCE(warehouse_value, 0)
        ) < 0.01
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM (
    SELECT
        'account_sales_revenue' AS metric,

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric AS warehouse_value,

        (
            SELECT SUM(total_revenue)
            FROM analytics.vw_account_sales_daily
        )::numeric AS analytics_value

    UNION ALL

    SELECT
        'customer_sales_revenue',

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric,

        (
            SELECT SUM(total_revenue)
            FROM analytics.vw_customer_sales_daily
        )::numeric

    UNION ALL

    SELECT
        'product_sales_revenue',

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric,

        (
            SELECT SUM(total_revenue)
            FROM analytics.vw_product_sales_daily
        )::numeric

    UNION ALL

    SELECT
        'location_sales_revenue',

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric,

        (
            SELECT SUM(total_revenue)
            FROM analytics.vw_location_sales_daily
        )::numeric

    UNION ALL

    SELECT
        'production_performance_quantity',

        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,

        (
            SELECT SUM(quantity_produced)
            FROM analytics.vw_production_performance_daily
        )::numeric

    UNION ALL

    SELECT
        'machine_production_quantity',

        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,

        (
            SELECT SUM(quantity_produced)
            FROM analytics.vw_machine_production_daily
        )::numeric

    UNION ALL

    SELECT
        'maintenance_performance_cost',

        (
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance
        )::numeric,

        (
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_maintenance_performance_daily
        )::numeric

    UNION ALL

    SELECT
        'energy_performance_kwh',

        (
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh'
        )::numeric,

        (
            SELECT SUM(energy_consumption)
            FROM analytics.vw_energy_performance_daily
            WHERE unit = 'kWh'
        )::numeric

    UNION ALL

    SELECT
        'emissions_performance_co2',

        (
            SELECT SUM(co2_kg)
            FROM public.fact_emissions
        )::numeric,

        (
            SELECT SUM(co2_kg)
            FROM analytics.vw_emissions_performance_daily
        )::numeric

    UNION ALL

    SELECT
        'waste_performance_kg',

        (
            SELECT SUM(quantity)
            FROM public.fact_waste
            WHERE unit = 'kg'
        )::numeric,

        (
            SELECT SUM(waste_quantity)
            FROM analytics.vw_waste_performance_daily
            WHERE unit = 'kg'
        )::numeric
) x
ORDER BY metric;


-- ============================================================
-- 6. CROSS-DOMAIN RECONCILIATION
-- ============================================================

SELECT
    metric,
    warehouse_value,
    analytics_value,
    analytics_value - warehouse_value AS difference,
    CASE
        WHEN ABS(
            COALESCE(analytics_value, 0)
            -
            COALESCE(warehouse_value, 0)
        ) < 0.01
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM (
    SELECT
        'cross_domain_sales_revenue' AS metric,

        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric AS warehouse_value,

        (
            SELECT SUM(sales_revenue)
            FROM analytics.vw_sales_production_inventory_daily
        )::numeric AS analytics_value

    UNION ALL

    SELECT
        'cross_domain_sales_quantity',

        (
            SELECT SUM(quantity)
            FROM public.fact_sales
        )::numeric,

        (
            SELECT SUM(sales_quantity)
            FROM analytics.vw_sales_production_inventory_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_production_quantity_sales_inventory',

        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,

        (
            SELECT SUM(production_quantity)
            FROM analytics.vw_sales_production_inventory_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_production_quantity_maintenance',

        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,

        (
            SELECT SUM(production_quantity)
            FROM analytics.vw_production_maintenance_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_maintenance_cost',

        (
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance
        )::numeric,

        (
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_production_maintenance_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_downtime_hours',

        (
            SELECT SUM(downtime_hours)
            FROM public.fact_maintenance
        )::numeric,

        (
            SELECT SUM(downtime_hours)
            FROM analytics.vw_production_maintenance_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_energy_kwh',

        (
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh'
        )::numeric,

        (
            SELECT SUM(energy_consumption_kwh)
            FROM analytics.vw_production_energy_emissions_daily
        )::numeric

    UNION ALL

    SELECT
        'cross_domain_co2_kg',

        (
            SELECT SUM(co2_kg)
            FROM public.fact_emissions
        )::numeric,

        (
            SELECT SUM(co2_kg)
            FROM analytics.vw_production_energy_emissions_daily
        )::numeric
) x
ORDER BY metric;


-- ============================================================
-- 7. CROSS-DOMAIN GRAIN UNIQUENESS
-- ============================================================
--
-- A governed analytical grain must produce at most one row for
-- each combination of its grain keys.
-- ============================================================


-- Sales + Production + Inventory
-- Grain: date + location + product

SELECT
    'sales_production_inventory_grain' AS validation,
    COUNT(*) AS duplicate_grain_groups,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
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
) duplicates;


-- Production + Maintenance
-- Grain: date + location + machine

SELECT
    'production_maintenance_grain' AS validation,
    COUNT(*) AS duplicate_grain_groups,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
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
) duplicates;


-- Production + Energy + Emissions
-- Grain: date + location

SELECT
    'production_energy_emissions_grain' AS validation,
    COUNT(*) AS duplicate_grain_groups,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM (
    SELECT
        date_key,
        location_key
    FROM analytics.vw_production_energy_emissions_daily
    GROUP BY
        date_key,
        location_key
    HAVING COUNT(*) > 1
) duplicates;


-- ============================================================
-- 8. FINAL FAN-OUT PROTECTION SUMMARY
-- ============================================================
--
-- This provides one concise summary of the most important
-- warehouse-to-cross-domain reconciliations.
-- ============================================================

WITH reconciliation AS (

    SELECT
        'sales_revenue' AS metric,
        (
            SELECT SUM(revenue)
            FROM public.fact_sales
        )::numeric AS warehouse_value,
        (
            SELECT SUM(sales_revenue)
            FROM analytics.vw_sales_production_inventory_daily
        )::numeric AS analytics_value

    UNION ALL

    SELECT
        'production_quantity',
        (
            SELECT SUM(quantity_produced)
            FROM public.fact_production
        )::numeric,
        (
            SELECT SUM(production_quantity)
            FROM analytics.vw_production_maintenance_daily
        )::numeric

    UNION ALL

    SELECT
        'maintenance_cost',
        (
            SELECT SUM(maintenance_cost)
            FROM public.fact_maintenance
        )::numeric,
        (
            SELECT SUM(maintenance_cost)
            FROM analytics.vw_production_maintenance_daily
        )::numeric

    UNION ALL

    SELECT
        'energy_kwh',
        (
            SELECT SUM(consumption)
            FROM public.fact_energy
            WHERE unit = 'kWh'
        )::numeric,
        (
            SELECT SUM(energy_consumption_kwh)
            FROM analytics.vw_production_energy_emissions_daily
        )::numeric

    UNION ALL

    SELECT
        'co2_kg',
        (
            SELECT SUM(co2_kg)
            FROM public.fact_emissions
        )::numeric,
        (
            SELECT SUM(co2_kg)
            FROM analytics.vw_production_energy_emissions_daily
        )::numeric
)

SELECT
    COUNT(*) AS metrics_tested,
    COUNT(*) FILTER (
        WHERE ABS(
            COALESCE(analytics_value, 0)
            -
            COALESCE(warehouse_value, 0)
        ) < 0.01
    ) AS metrics_passed,
    COUNT(*) FILTER (
        WHERE ABS(
            COALESCE(analytics_value, 0)
            -
            COALESCE(warehouse_value, 0)
        ) >= 0.01
    ) AS metrics_failed,

    CASE
        WHEN COUNT(*) FILTER (
            WHERE ABS(
                COALESCE(analytics_value, 0)
                -
                COALESCE(warehouse_value, 0)
            ) >= 0.01
        ) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS final_validation_status

FROM reconciliation;