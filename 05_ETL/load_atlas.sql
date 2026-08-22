-- Project Atlas
-- Phase 5 - ETL
-- Loads validated warehouse-ready CSV files into PostgreSQL.
--
-- Run this script from the Project Atlas repository root.
-- The PostgreSQL tables must already exist from Phase 6 schema setup.
--
-- Load order:
-- 1. Dimensions
-- 2. Facts

BEGIN;

-- ============================================================
-- DIMENSIONS
-- ============================================================

\copy dim_date (
    date_key,
    full_date,
    day_of_week,
    day_name,
    week_number,
    month,
    month_name,
    quarter,
    year
)
FROM '05_ETL/data/warehouse_ready/dim_date.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_account (
    account_key,
    account_id,
    account_name,
    account_type,
    industry,
    country,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_account.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_customer (
    customer_key,
    customer_id,
    account_key,
    customer_name,
    customer_segment,
    industry,
    country,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_customer.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_product (
    product_key,
    product_id,
    supplier_key,
    product_name,
    category,
    subcategory,
    unit_of_measure,
    unit_cost,
    unit_price,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_product.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_supplier (
    supplier_key,
    supplier_id,
    supplier_name,
    supplier_category,
    country,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_supplier.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_location (
    location_key,
    location_id,
    location_name,
    location_type,
    city,
    state_region,
    country,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_location.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_employee (
    employee_key,
    employee_id,
    location_key,
    employee_name,
    department,
    role,
    hire_date,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_employee.csv'
WITH (FORMAT csv, HEADER true);

\copy dim_machine (
    machine_key,
    machine_id,
    location_key,
    machine_name,
    machine_type,
    installation_date,
    status
)
FROM '05_ETL/data/warehouse_ready/dim_machine.csv'
WITH (FORMAT csv, HEADER true);

-- ============================================================
-- FACTS
-- ============================================================

\copy fact_sales (
    sales_key,
    transaction_id,
    date_key,
    customer_key,
    product_key,
    location_key,
    quantity,
    unit_price,
    discount_amount,
    revenue
)
FROM '05_ETL/data/warehouse_ready/fact_sales.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_production (
    production_key,
    production_id,
    date_key,
    product_key,
    location_key,
    machine_key,
    employee_key,
    planned_quantity,
    produced_quantity,
    defect_quantity,
    production_hours
)
FROM '05_ETL/data/warehouse_ready/fact_production.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_maintenance (
    maintenance_key,
    maintenance_id,
    date_key,
    location_key,
    machine_key,
    employee_key,
    maintenance_type,
    maintenance_hours,
    downtime_hours,
    maintenance_cost
)
FROM '05_ETL/data/warehouse_ready/fact_maintenance.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_financial_transaction (
    financial_transaction_key,
    transaction_id,
    date_key,
    account_key,
    location_key,
    transaction_type,
    transaction_category,
    transaction_amount
)
FROM '05_ETL/data/warehouse_ready/fact_financial_transaction.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_budget (
    budget_key,
    budget_id,
    date_key,
    account_key,
    location_key,
    budget_category,
    budget_amount
)
FROM '05_ETL/data/warehouse_ready/fact_budget.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_energy (
    energy_key,
    energy_id,
    date_key,
    location_key,
    machine_key,
    energy_source,
    energy_consumption
)
FROM '05_ETL/data/warehouse_ready/fact_energy.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_emissions (
    emissions_key,
    emissions_id,
    date_key,
    location_key,
    emissions_category,
    co2_emissions
)
FROM '05_ETL/data/warehouse_ready/fact_emissions.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_waste (
    waste_key,
    waste_id,
    date_key,
    location_key,
    waste_category,
    disposal_method,
    waste_quantity
)
FROM '05_ETL/data/warehouse_ready/fact_waste.csv'
WITH (FORMAT csv, HEADER true);

\copy fact_inventory (
    inventory_key,
    inventory_id,
    date_key,
    product_key,
    location_key,
    opening_quantity,
    received_quantity,
    issued_quantity,
    closing_quantity,
    reorder_point
)
FROM '05_ETL/data/warehouse_ready/fact_inventory.csv'
WITH (FORMAT csv, HEADER true);

COMMIT;