-- ============================================================
-- Project Atlas — Phase 6 Data Warehouse
-- 03_create_indexes.sql
--
-- Purpose:
-- Create justified indexes on fact-table foreign keys used
-- for dimensional joins and common analytical filtering.
--
-- Primary-key and unique-constraint indexes are managed by
-- PostgreSQL automatically and are therefore not duplicated here.
-- ============================================================


-- ============================================================
-- fact_sales
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key
    ON fact_sales (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_account_key
    ON fact_sales (account_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_key
    ON fact_sales (customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key
    ON fact_sales (product_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_location_key
    ON fact_sales (location_key);


-- ============================================================
-- fact_production
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_production_date_key
    ON fact_production (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_production_product_key
    ON fact_production (product_key);

CREATE INDEX IF NOT EXISTS idx_fact_production_location_key
    ON fact_production (location_key);

CREATE INDEX IF NOT EXISTS idx_fact_production_machine_key
    ON fact_production (machine_key);

CREATE INDEX IF NOT EXISTS idx_fact_production_employee_key
    ON fact_production (employee_key);


-- ============================================================
-- fact_maintenance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_date_key
    ON fact_maintenance (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_location_key
    ON fact_maintenance (location_key);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_machine_key
    ON fact_maintenance (machine_key);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_employee_key
    ON fact_maintenance (employee_key);


-- ============================================================
-- fact_financial_transaction
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_financial_transaction_date_key
    ON fact_financial_transaction (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_financial_transaction_location_key
    ON fact_financial_transaction (location_key);


-- ============================================================
-- fact_budget
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_budget_date_key
    ON fact_budget (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_budget_location_key
    ON fact_budget (location_key);


-- ============================================================
-- fact_energy
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_energy_date_key
    ON fact_energy (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_energy_location_key
    ON fact_energy (location_key);


-- ============================================================
-- fact_emissions
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_emissions_date_key
    ON fact_emissions (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_emissions_location_key
    ON fact_emissions (location_key);


-- ============================================================
-- fact_waste
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_waste_date_key
    ON fact_waste (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_waste_location_key
    ON fact_waste (location_key);


-- ============================================================
-- fact_inventory
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_inventory_date_key
    ON fact_inventory (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_product_key
    ON fact_inventory (product_key);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_location_key
    ON fact_inventory (location_key);