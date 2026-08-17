-- ============================================================
-- Project Atlas — Phase 6 — PostgreSQL Data Warehouse
-- Script: 02_create_facts.sql
-- Purpose: Create warehouse fact tables
-- ============================================================

-- ------------------------------------------------------------
-- fact_sales
-- Grain: One row = one sales transaction
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id        VARCHAR(30) PRIMARY KEY,
    date_key        INTEGER NOT NULL,
    account_key     INTEGER NOT NULL,
    customer_key    INTEGER NOT NULL,
    product_key     INTEGER NOT NULL,
    location_key    INTEGER NOT NULL,
    quantity        NUMERIC(14,2),
    unit_price      NUMERIC(14,2),
    discount_rate   NUMERIC(8,4),
    revenue         NUMERIC(16,2),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_sales_account
        FOREIGN KEY (account_key)
        REFERENCES dim_account(account_key),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_sales_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_production
-- Grain: One row = one production event
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_production (
    production_id       VARCHAR(30) PRIMARY KEY,
    date_key            INTEGER NOT NULL,
    product_key         INTEGER NOT NULL,
    location_key        INTEGER NOT NULL,
    machine_key         INTEGER NOT NULL,
    employee_key        INTEGER NOT NULL,
    planned_quantity    NUMERIC(14,2),
    quantity_produced   NUMERIC(14,2),
    production_hours    NUMERIC(10,2),
    production_status   VARCHAR(50),

    CONSTRAINT fk_production_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_production_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_production_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key),

    CONSTRAINT fk_production_machine
        FOREIGN KEY (machine_key)
        REFERENCES dim_machine(machine_key),

    CONSTRAINT fk_production_employee
        FOREIGN KEY (employee_key)
        REFERENCES dim_employee(employee_key)
);


-- ------------------------------------------------------------
-- fact_maintenance
-- Grain: One row = one maintenance event
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_maintenance (
    maintenance_id      VARCHAR(30) PRIMARY KEY,
    date_key            INTEGER NOT NULL,
    location_key        INTEGER NOT NULL,
    machine_key         INTEGER NOT NULL,
    employee_key        INTEGER NOT NULL,
    maintenance_type    VARCHAR(100),
    downtime_hours      NUMERIC(10,2),
    maintenance_cost    NUMERIC(14,2),

    CONSTRAINT fk_maintenance_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_maintenance_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key),

    CONSTRAINT fk_maintenance_machine
        FOREIGN KEY (machine_key)
        REFERENCES dim_machine(machine_key),

    CONSTRAINT fk_maintenance_employee
        FOREIGN KEY (employee_key)
        REFERENCES dim_employee(employee_key)
);


-- ------------------------------------------------------------
-- fact_financial_transaction
-- Grain: One row = one financial transaction
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_financial_transaction (
    financial_transaction_id   VARCHAR(30) PRIMARY KEY,
    date_key                   INTEGER NOT NULL,
    location_key               INTEGER NOT NULL,
    transaction_type           VARCHAR(100),
    amount                     NUMERIC(16,2),
    description                VARCHAR(500),

    CONSTRAINT fk_financial_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_financial_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_budget
-- Grain: One row = one budget record
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_budget (
    budget_id       VARCHAR(30) PRIMARY KEY,
    date_key        INTEGER NOT NULL,
    location_key    INTEGER NOT NULL,
    category        VARCHAR(100),
    budget_amount   NUMERIC(16,2),

    CONSTRAINT fk_budget_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_budget_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_energy
-- Grain: One row = one energy measurement
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_energy (
    energy_id       VARCHAR(30) PRIMARY KEY,
    date_key        INTEGER NOT NULL,
    location_key    INTEGER NOT NULL,
    energy_type     VARCHAR(100),
    consumption     NUMERIC(16,2),
    unit            VARCHAR(30),

    CONSTRAINT fk_energy_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_energy_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_emissions
-- Grain: One row = one emissions measurement
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_emissions (
    emissions_id    VARCHAR(30) PRIMARY KEY,
    date_key        INTEGER NOT NULL,
    location_key    INTEGER NOT NULL,
    source          VARCHAR(100),
    co2_kg          NUMERIC(16,2),

    CONSTRAINT fk_emissions_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_emissions_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_waste
-- Grain: One row = one waste record
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_waste (
    waste_id         VARCHAR(30) PRIMARY KEY,
    date_key         INTEGER NOT NULL,
    location_key     INTEGER NOT NULL,
    waste_type       VARCHAR(100),
    quantity         NUMERIC(16,2),
    unit             VARCHAR(30),
    disposal_method  VARCHAR(100),

    CONSTRAINT fk_waste_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_waste_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);


-- ------------------------------------------------------------
-- fact_inventory
-- Grain: One row = one product/location/date inventory snapshot
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_inventory (
    inventory_id       VARCHAR(30) PRIMARY KEY,
    date_key           INTEGER NOT NULL,
    product_key        INTEGER NOT NULL,
    location_key       INTEGER NOT NULL,
    quantity_on_hand   NUMERIC(16,2),
    reorder_point      NUMERIC(16,2),
    inventory_value    NUMERIC(18,2),

    CONSTRAINT fk_inventory_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_inventory_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key),

    CONSTRAINT uq_inventory_snapshot
        UNIQUE (date_key, product_key, location_key)
);