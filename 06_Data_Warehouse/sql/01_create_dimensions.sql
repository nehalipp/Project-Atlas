-- ============================================================
-- Project Atlas — Phase 6 — PostgreSQL Data Warehouse
-- Script: 01_create_dimensions.sql
-- Purpose: Create warehouse dimension tables
-- ============================================================

-- ------------------------------------------------------------
-- dim_date
-- Grain: One row = one calendar date
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INTEGER PRIMARY KEY,
    date            DATE NOT NULL UNIQUE,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    week_of_year    INTEGER NOT NULL,
    day             INTEGER NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    day_of_week     INTEGER NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);


-- ------------------------------------------------------------
-- dim_account
-- Grain: One row = one account
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_account (
    account_key     INTEGER PRIMARY KEY,
    account_id      VARCHAR(20) NOT NULL UNIQUE,
    account_name    VARCHAR(255) NOT NULL,
    account_type    VARCHAR(100),
    industry        VARCHAR(100),
    country         VARCHAR(100),
    status          VARCHAR(50)
);


-- ------------------------------------------------------------
-- dim_customer
-- Grain: One row = one customer
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key       INTEGER PRIMARY KEY,
    customer_id        VARCHAR(20) NOT NULL UNIQUE,
    account_id         VARCHAR(20),
    customer_name      VARCHAR(255) NOT NULL,
    customer_segment   VARCHAR(100),
    industry           VARCHAR(100),
    country            VARCHAR(100),
    status             VARCHAR(50),

    CONSTRAINT fk_customer_account
        FOREIGN KEY (account_id)
        REFERENCES dim_account(account_id)
);


-- ------------------------------------------------------------
-- dim_supplier
-- Grain: One row = one supplier
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_key        INTEGER PRIMARY KEY,
    supplier_id         VARCHAR(20) NOT NULL UNIQUE,
    supplier_name       VARCHAR(255) NOT NULL,
    supplier_category   VARCHAR(100),
    country              VARCHAR(100),
    status               VARCHAR(50)
);


-- ------------------------------------------------------------
-- dim_product
-- Grain: One row = one product
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_product (
    product_key     INTEGER PRIMARY KEY,
    product_id      VARCHAR(20) NOT NULL UNIQUE,
    supplier_id     VARCHAR(20),
    product_name    VARCHAR(255) NOT NULL,
    category        VARCHAR(100),
    unit_cost       NUMERIC(12,2),
    unit_price      NUMERIC(12,2),
    status          VARCHAR(50),

    CONSTRAINT fk_product_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES dim_supplier(supplier_id)
);


-- ------------------------------------------------------------
-- dim_location
-- Grain: One row = one location
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_location (
    location_key    INTEGER PRIMARY KEY,
    location_id     VARCHAR(20) NOT NULL UNIQUE,
    location_name   VARCHAR(255) NOT NULL,
    location_type   VARCHAR(100),
    city            VARCHAR(100),
    state_region    VARCHAR(100),
    country         VARCHAR(100),
    status          VARCHAR(50)
);


-- ------------------------------------------------------------
-- dim_employee
-- Grain: One row = one employee
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_employee (
    employee_key    INTEGER PRIMARY KEY,
    employee_id     VARCHAR(20) NOT NULL UNIQUE,
    location_id     VARCHAR(20),
    employee_name   VARCHAR(255) NOT NULL,
    department      VARCHAR(100),
    role            VARCHAR(100),
    hire_date       DATE,
    status          VARCHAR(50),

    CONSTRAINT fk_employee_location
        FOREIGN KEY (location_id)
        REFERENCES dim_location(location_id)
);


-- ------------------------------------------------------------
-- dim_machine
-- Grain: One row = one machine
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_machine (
    machine_key         INTEGER PRIMARY KEY,
    machine_id          VARCHAR(20) NOT NULL UNIQUE,
    location_id         VARCHAR(20),
    machine_name        VARCHAR(255) NOT NULL,
    machine_type        VARCHAR(100),
    installation_date   DATE,
    status              VARCHAR(50),

    CONSTRAINT fk_machine_location
        FOREIGN KEY (location_id)
        REFERENCES dim_location(location_id)
);