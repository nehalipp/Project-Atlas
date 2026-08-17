-- ============================================================
-- Project Atlas — Phase 6 Data Warehouse
-- 04_validate_warehouse.sql
--
-- Purpose:
-- Reproducible validation of the PostgreSQL warehouse.
--
-- Validation areas:
-- 1. Warehouse table existence
-- 2. Row counts
-- 3. Primary keys
-- 4. Foreign keys
-- 5. Inventory grain
-- 6. Referential integrity
-- 7. Production data validity
-- 8. Production outlier monitoring
-- 9. Warehouse indexes
-- ============================================================


-- ============================================================
-- 1. Warehouse table existence
-- Expected: 17 tables
-- ============================================================

SELECT
    COUNT(*) AS warehouse_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE';


SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;


-- ============================================================
-- 2. Warehouse row counts
-- ============================================================

SELECT 'dim_account' AS table_name, COUNT(*) AS row_count
FROM dim_account

UNION ALL
SELECT 'dim_customer', COUNT(*)
FROM dim_customer

UNION ALL
SELECT 'dim_date', COUNT(*)
FROM dim_date

UNION ALL
SELECT 'dim_employee', COUNT(*)
FROM dim_employee

UNION ALL
SELECT 'dim_location', COUNT(*)
FROM dim_location

UNION ALL
SELECT 'dim_machine', COUNT(*)
FROM dim_machine

UNION ALL
SELECT 'dim_product', COUNT(*)
FROM dim_product

UNION ALL
SELECT 'dim_supplier', COUNT(*)
FROM dim_supplier

UNION ALL
SELECT 'fact_budget', COUNT(*)
FROM fact_budget

UNION ALL
SELECT 'fact_emissions', COUNT(*)
FROM fact_emissions

UNION ALL
SELECT 'fact_energy', COUNT(*)
FROM fact_energy

UNION ALL
SELECT 'fact_financial_transaction', COUNT(*)
FROM fact_financial_transaction

UNION ALL
SELECT 'fact_inventory', COUNT(*)
FROM fact_inventory

UNION ALL
SELECT 'fact_maintenance', COUNT(*)
FROM fact_maintenance

UNION ALL
SELECT 'fact_production', COUNT(*)
FROM fact_production

UNION ALL
SELECT 'fact_sales', COUNT(*)
FROM fact_sales

UNION ALL
SELECT 'fact_waste', COUNT(*)
FROM fact_waste

ORDER BY table_name;


-- ============================================================
-- 3. Primary-key validation
-- Expected: one PRIMARY KEY per warehouse table
-- ============================================================

SELECT
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
  AND constraint_type = 'PRIMARY KEY'
ORDER BY table_name;


-- ============================================================
-- 4. Foreign-key validation
-- ============================================================

SELECT
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
  AND constraint_type = 'FOREIGN KEY'
ORDER BY table_name, constraint_name;


-- ============================================================
-- 5. Inventory grain validation
--
-- Approved grain:
-- One row = one product/location/date inventory snapshot.
--
-- Expected: 0 duplicate combinations.
-- ============================================================

SELECT
    date_key,
    product_key,
    location_key,
    COUNT(*) AS record_count
FROM fact_inventory
GROUP BY
    date_key,
    product_key,
    location_key
HAVING COUNT(*) > 1
ORDER BY record_count DESC
LIMIT 20;


-- ============================================================
-- 6. Referential integrity validation
--
-- Expected: 0 orphan records.
-- ============================================================

-- Sales → Account
SELECT COUNT(*) AS orphan_sales_accounts
FROM fact_sales f
LEFT JOIN dim_account d
    ON f.account_key = d.account_key
WHERE d.account_key IS NULL;


-- Sales → Customer
SELECT COUNT(*) AS orphan_sales_customers
FROM fact_sales f
LEFT JOIN dim_customer d
    ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL;


-- Sales → Product
SELECT COUNT(*) AS orphan_sales_products
FROM fact_sales f
LEFT JOIN dim_product d
    ON f.product_key = d.product_key
WHERE d.product_key IS NULL;


-- Sales → Location
SELECT COUNT(*) AS orphan_sales_locations
FROM fact_sales f
LEFT JOIN dim_location d
    ON f.location_key = d.location_key
WHERE d.location_key IS NULL;


-- Production → Product
SELECT COUNT(*) AS orphan_production_products
FROM fact_production f
LEFT JOIN dim_product d
    ON f.product_key = d.product_key
WHERE d.product_key IS NULL;


-- Production → Location
SELECT COUNT(*) AS orphan_production_locations
FROM fact_production f
LEFT JOIN dim_location d
    ON f.location_key = d.location_key
WHERE d.location_key IS NULL;


-- Production → Machine
SELECT COUNT(*) AS orphan_production_machines
FROM fact_production f
LEFT JOIN dim_machine d
    ON f.machine_key = d.machine_key
WHERE d.machine_key IS NULL;


-- Production → Employee
SELECT COUNT(*) AS orphan_production_employees
FROM fact_production f
LEFT JOIN dim_employee d
    ON f.employee_key = d.employee_key
WHERE d.employee_key IS NULL;


-- Maintenance → Machine
SELECT COUNT(*) AS orphan_maintenance_machines
FROM fact_maintenance f
LEFT JOIN dim_machine d
    ON f.machine_key = d.machine_key
WHERE d.machine_key IS NULL;


-- Maintenance → Employee
SELECT COUNT(*) AS orphan_maintenance_employees
FROM fact_maintenance f
LEFT JOIN dim_employee d
    ON f.employee_key = d.employee_key
WHERE d.employee_key IS NULL;


-- Inventory → Product
SELECT COUNT(*) AS orphan_inventory_products
FROM fact_inventory f
LEFT JOIN dim_product d
    ON f.product_key = d.product_key
WHERE d.product_key IS NULL;


-- Inventory → Location
SELECT COUNT(*) AS orphan_inventory_locations
FROM fact_inventory f
LEFT JOIN dim_location d
    ON f.location_key = d.location_key
WHERE d.location_key IS NULL;


-- ============================================================
-- 7. Production validity
--
-- These are hard validity checks.
-- Expected: 0.
-- ============================================================

SELECT COUNT(*) AS invalid_production_records
FROM fact_production
WHERE planned_quantity < 0
   OR quantity_produced < 0
   OR production_hours < 0;


SELECT COUNT(*) AS zero_planned_quantity_records
FROM fact_production
WHERE planned_quantity = 0;


-- ============================================================
-- 8. Production outlier monitoring
--
-- Above-plan production is NOT treated as an error.
-- Extreme production is monitored as a data-quality observation.
-- ============================================================

SELECT
    COUNT(*) AS total_production_records,
    COUNT(*) FILTER (
        WHERE quantity_produced > planned_quantity
    ) AS above_plan_records,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE quantity_produced > planned_quantity
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS above_plan_pct
FROM fact_production;


SELECT
    COUNT(*) AS extreme_production_outliers
FROM fact_production
WHERE planned_quantity > 0
  AND quantity_produced > planned_quantity * 2;


-- ============================================================
-- 9. Warehouse index inventory
-- ============================================================

SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;