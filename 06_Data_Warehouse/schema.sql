-- Project Atlas
-- Phase 6 - Data Warehouse
--
-- Creates the PostgreSQL dimensional warehouse.
-- Database: atlas_warehouse
--
-- Warehouse baseline:
-- 8 dimensions
-- 9 facts
-- 17 tables
--
-- Data types and relationships follow the approved
-- Project Atlas data dictionary.

BEGIN;

-- ============================================================
-- DIMENSIONS
-- ============================================================

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week_number SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter SMALLINT NOT NULL,
    year SMALLINT NOT NULL
);

CREATE TABLE dim_account (
    account_key BIGINT PRIMARY KEY,
    account_id VARCHAR(30) NOT NULL UNIQUE,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE dim_supplier (
    supplier_key BIGINT PRIMARY KEY,
    supplier_id VARCHAR(30) NOT NULL UNIQUE,
    supplier_name VARCHAR(200) NOT NULL,
    supplier_category VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE dim_location (
    location_key BIGINT PRIMARY KEY,
    location_id VARCHAR(30) NOT NULL UNIQUE,
    location_name VARCHAR(200) NOT NULL,
    location_type VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_region VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id VARCHAR(30) NOT NULL UNIQUE,
    account_key BIGINT NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,

    CONSTRAINT fk_customer_account
        FOREIGN KEY (account_key)
        REFERENCES dim_account(account_key)
);

CREATE TABLE dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id VARCHAR(30) NOT NULL UNIQUE,
    supplier_key BIGINT NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    unit_of_measure VARCHAR(30) NOT NULL,
    unit_cost NUMERIC(14,2) NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL,
    status VARCHAR(30) NOT NULL,

    CONSTRAINT fk_product_supplier
        FOREIGN KEY (supplier_key)
        REFERENCES dim_supplier(supplier_key)
);

CREATE TABLE dim_employee (
    employee_key BIGINT PRIMARY KEY,
    employee_id VARCHAR(30) NOT NULL UNIQUE,
    location_key BIGINT NOT NULL,
    employee_name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,

    CONSTRAINT fk_employee_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

CREATE TABLE dim_machine (
    machine_key BIGINT PRIMARY KEY,
    machine_id VARCHAR(30) NOT NULL UNIQUE,
    location_key BIGINT NOT NULL,
    machine_name VARCHAR(200) NOT NULL,
    machine_type VARCHAR(100) NOT NULL,
    installation_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,

    CONSTRAINT fk_machine_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

-- ============================================================
-- FACTS
-- ============================================================

CREATE TABLE fact_sales (
    sales_key BIGINT PRIMARY KEY,
    transaction_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    location_key BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL,
    discount_amount NUMERIC(14,2) NOT NULL,
    revenue NUMERIC(16,2) NOT NULL,

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

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

CREATE TABLE fact_production (
    production_key BIGINT PRIMARY KEY,
    production_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    product_key BIGINT NOT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    location_key BIGINT NOT NULL,
    machine_key BIGINT NOT NULL,
    employee_key BIGINT NOT NULL,
    planned_quantity INTEGER NOT NULL,
    produced_quantity INTEGER NOT NULL,
    defect_quantity INTEGER NOT NULL,
    production_hours NUMERIC(10,2) NOT NULL,

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

CREATE TABLE fact_maintenance (
    maintenance_key BIGINT PRIMARY KEY,
    maintenance_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    location_key BIGINT NOT NULL,
    machine_key BIGINT NOT NULL,
    employee_key BIGINT NOT NULL,
    maintenance_type VARCHAR(40) NOT NULL,
    maintenance_hours NUMERIC(10,2) NOT NULL,
    downtime_hours NUMERIC(10,2) NOT NULL,
    maintenance_cost NUMERIC(14,2) NOT NULL,

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

CREATE TABLE fact_financial_transaction (
    financial_transaction_key BIGINT PRIMARY KEY,
    transaction_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    account_key BIGINT NOT NULL,
    location_key BIGINT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_category VARCHAR(100) NOT NULL,
    transaction_amount NUMERIC(16,2) NOT NULL,

    CONSTRAINT fk_financial_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_financial_account
        FOREIGN KEY (account_key)
        REFERENCES dim_account(account_key),

    CONSTRAINT fk_financial_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

CREATE TABLE fact_budget (
    budget_key BIGINT PRIMARY KEY,
    budget_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    account_key BIGINT NOT NULL,
    location_key BIGINT NOT NULL,
    budget_category VARCHAR(100) NOT NULL,
    budget_amount NUMERIC(16,2) NOT NULL,

    CONSTRAINT fk_budget_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_budget_account
        FOREIGN KEY (account_key)
        REFERENCES dim_account(account_key),

    CONSTRAINT fk_budget_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

CREATE TABLE fact_energy (
    energy_key BIGINT PRIMARY KEY,
    energy_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    location_key BIGINT NOT NULL,
    machine_key BIGINT NOT NULL,
    energy_source VARCHAR(50) NOT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    energy_consumption NUMERIC(16,3) NOT NULL,

    CONSTRAINT fk_energy_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_energy_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key),

    CONSTRAINT fk_energy_machine
        FOREIGN KEY (machine_key)
        REFERENCES dim_machine(machine_key)
);

CREATE TABLE fact_emissions (
    emissions_key BIGINT PRIMARY KEY,
    emissions_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    location_key BIGINT NOT NULL,
    emissions_category VARCHAR(100) NOT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    co2_emissions NUMERIC(16,3) NOT NULL,

    CONSTRAINT fk_emissions_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_emissions_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

CREATE TABLE fact_waste (
    waste_key BIGINT PRIMARY KEY,
    waste_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    location_key BIGINT NOT NULL,
    waste_category VARCHAR(100) NOT NULL,
    disposal_method VARCHAR(100),
    unit_of_measure VARCHAR(30) NOT NULL,
    waste_quantity NUMERIC(16,3) NOT NULL,

    CONSTRAINT fk_waste_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_waste_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

CREATE TABLE fact_inventory (
    inventory_key BIGINT PRIMARY KEY,
    inventory_id VARCHAR(40) NOT NULL UNIQUE,
    date_key INTEGER NOT NULL,
    product_key BIGINT NOT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    location_key BIGINT NOT NULL,
    opening_quantity INTEGER NOT NULL,
    received_quantity INTEGER NOT NULL,
    issued_quantity INTEGER NOT NULL,
    closing_quantity INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,

    CONSTRAINT fk_inventory_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_inventory_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

COMMIT;