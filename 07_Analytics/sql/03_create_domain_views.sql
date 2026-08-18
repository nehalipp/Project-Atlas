-- ============================================================
-- Project Atlas — Phase 7 Analytics
-- Domain Analytics Views
--
-- Purpose:
-- Create reusable, dimension-aware analytical views for
-- commercial, operational, financial, sustainability, and
-- inventory analysis.
--
-- Design principles:
-- 1. Use warehouse surrogate keys for dimensional joins.
-- 2. Preserve conformed dimensions.
-- 3. Aggregate before combining facts.
-- 4. Avoid incompatible fact-to-fact joins.
-- 5. Keep views suitable for Power BI and Tableau consumption.
-- ============================================================


CREATE SCHEMA IF NOT EXISTS analytics;


-- ============================================================
-- CLEANUP
-- ============================================================

DROP VIEW IF EXISTS analytics.vw_inventory_position_daily;
DROP VIEW IF EXISTS analytics.vw_waste_performance_daily;
DROP VIEW IF EXISTS analytics.vw_emissions_performance_daily;
DROP VIEW IF EXISTS analytics.vw_energy_performance_daily;
DROP VIEW IF EXISTS analytics.vw_budget_performance_daily;
DROP VIEW IF EXISTS analytics.vw_financial_performance_daily;
DROP VIEW IF EXISTS analytics.vw_employee_operations_daily;
DROP VIEW IF EXISTS analytics.vw_maintenance_performance_daily;
DROP VIEW IF EXISTS analytics.vw_machine_production_daily;
DROP VIEW IF EXISTS analytics.vw_production_performance_daily;
DROP VIEW IF EXISTS analytics.vw_location_sales_daily;
DROP VIEW IF EXISTS analytics.vw_supplier_sales_daily;
DROP VIEW IF EXISTS analytics.vw_product_sales_daily;
DROP VIEW IF EXISTS analytics.vw_customer_sales_daily;
DROP VIEW IF EXISTS analytics.vw_account_sales_daily;


-- ============================================================
-- COMMERCIAL ANALYTICS
-- ============================================================


-- ============================================================
-- ACCOUNT SALES
-- Grain:
-- One row per date + account.
-- ============================================================

CREATE VIEW analytics.vw_account_sales_daily AS
SELECT
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    s.account_key,
    a.account_id,
    a.account_name,
    a.account_type,
    a.industry,
    a.country,
    a.status AS account_status,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price,

    AVG(s.discount_rate) AS average_discount_rate

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key
JOIN public.dim_account a
    ON s.account_key = a.account_key

GROUP BY
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    s.account_key,
    a.account_id,
    a.account_name,
    a.account_type,
    a.industry,
    a.country,
    a.status;


-- ============================================================
-- CUSTOMER SALES
-- Grain:
-- One row per date + customer.
-- ============================================================

CREATE VIEW analytics.vw_customer_sales_daily AS
SELECT
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    s.customer_key,
    c.customer_id,
    c.customer_name,
    c.account_id,
    c.customer_segment,
    c.industry,
    c.country,
    c.status AS customer_status,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price,

    AVG(s.discount_rate) AS average_discount_rate

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key
JOIN public.dim_customer c
    ON s.customer_key = c.customer_key

GROUP BY
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    s.customer_key,
    c.customer_id,
    c.customer_name,
    c.account_id,
    c.customer_segment,
    c.industry,
    c.country,
    c.status;


-- ============================================================
-- PRODUCT SALES
-- Grain:
-- One row per date + product.
-- ============================================================

CREATE VIEW analytics.vw_product_sales_daily AS
SELECT
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    s.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.supplier_id,
    p.unit_cost,
    p.unit_price,
    p.status AS product_status,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price,

    AVG(s.discount_rate) AS average_discount_rate,

    SUM(s.quantity * p.unit_cost) AS estimated_product_cost,

    SUM(s.revenue)
        - SUM(s.quantity * p.unit_cost) AS estimated_gross_margin

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key
JOIN public.dim_product p
    ON s.product_key = p.product_key

GROUP BY
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    s.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.supplier_id,
    p.unit_cost,
    p.unit_price,
    p.status;


-- ============================================================
-- SUPPLIER SALES
-- Grain:
-- One row per date + supplier + product.
--
-- Supplier is conformed through dim_product.supplier_id because
-- fact_sales contains product_key rather than supplier_key.
-- ============================================================

CREATE VIEW analytics.vw_supplier_sales_daily AS
SELECT
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    sp.supplier_key,
    sp.supplier_id,
    sp.supplier_name,
    sp.supplier_category,
    sp.country AS supplier_country,
    sp.status AS supplier_status,

    p.product_key,
    p.product_id,
    p.product_name,
    p.category AS product_category,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key
JOIN public.dim_product p
    ON s.product_key = p.product_key
JOIN public.dim_supplier sp
    ON p.supplier_id = sp.supplier_id

GROUP BY
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    sp.supplier_key,
    sp.supplier_id,
    sp.supplier_name,
    sp.supplier_category,
    sp.country,
    sp.status,
    p.product_key,
    p.product_id,
    p.product_name,
    p.category;


-- ============================================================
-- LOCATION SALES
-- Grain:
-- One row per date + location.
-- ============================================================

CREATE VIEW analytics.vw_location_sales_daily AS
SELECT
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    s.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.city,
    l.state_region,
    l.country,
    l.status AS location_status,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key
JOIN public.dim_location l
    ON s.location_key = l.location_key

GROUP BY
    s.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    s.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.city,
    l.state_region,
    l.country,
    l.status;


-- ============================================================
-- OPERATIONS ANALYTICS
-- ============================================================


-- ============================================================
-- PRODUCTION PERFORMANCE
-- Grain:
-- One row per date + location + product.
-- ============================================================

CREATE VIEW analytics.vw_production_performance_daily AS
SELECT
    p.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    p.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    p.product_key,
    pr.product_id,
    pr.product_name,
    pr.category AS product_category,

    COUNT(DISTINCT p.production_id) AS production_record_count,

    COUNT(DISTINCT CASE
        WHEN p.production_status = 'Completed'
        THEN p.production_id
    END) AS completed_production_count,

    COUNT(DISTINCT CASE
        WHEN p.production_status = 'Partial'
        THEN p.production_id
    END) AS partial_production_count,

    COUNT(DISTINCT CASE
        WHEN p.production_status = 'Cancelled'
        THEN p.production_id
    END) AS cancelled_production_count,

    SUM(p.planned_quantity) AS planned_quantity,
    SUM(p.quantity_produced) AS quantity_produced,
    SUM(p.production_hours) AS production_hours,

    SUM(p.quantity_produced)
        - SUM(p.planned_quantity) AS production_variance,

    CASE
        WHEN SUM(p.planned_quantity) = 0 THEN NULL
        ELSE
            SUM(p.quantity_produced)
            / SUM(p.planned_quantity)
    END AS production_attainment_rate,

    CASE
        WHEN SUM(p.production_hours) = 0 THEN NULL
        ELSE
            SUM(p.quantity_produced)
            / SUM(p.production_hours)
    END AS production_rate

FROM public.fact_production p
JOIN public.dim_date d
    ON p.date_key = d.date_key
JOIN public.dim_location l
    ON p.location_key = l.location_key
JOIN public.dim_product pr
    ON p.product_key = pr.product_key

GROUP BY
    p.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    p.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    p.product_key,
    pr.product_id,
    pr.product_name,
    pr.category;


-- ============================================================
-- MACHINE PRODUCTION
-- Grain:
-- One row per date + machine.
-- ============================================================

CREATE VIEW analytics.vw_machine_production_daily AS
SELECT
    p.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    p.machine_key,
    m.machine_id,
    m.machine_name,
    m.machine_type,
    m.installation_date,
    m.status AS machine_status,

    p.location_key,
    l.location_id,
    l.location_name,

    COUNT(DISTINCT p.production_id) AS production_record_count,
    SUM(p.planned_quantity) AS planned_quantity,
    SUM(p.quantity_produced) AS quantity_produced,
    SUM(p.production_hours) AS production_hours,

    CASE
        WHEN SUM(p.production_hours) = 0 THEN NULL
        ELSE
            SUM(p.quantity_produced)
            / SUM(p.production_hours)
    END AS production_rate

FROM public.fact_production p
JOIN public.dim_date d
    ON p.date_key = d.date_key
JOIN public.dim_machine m
    ON p.machine_key = m.machine_key
JOIN public.dim_location l
    ON p.location_key = l.location_key

GROUP BY
    p.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    p.machine_key,
    m.machine_id,
    m.machine_name,
    m.machine_type,
    m.installation_date,
    m.status,
    p.location_key,
    l.location_id,
    l.location_name;


-- ============================================================
-- MAINTENANCE PERFORMANCE
-- Grain:
-- One row per date + machine.
-- ============================================================

CREATE VIEW analytics.vw_maintenance_performance_daily AS
SELECT
    m.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    m.machine_key,
    md.machine_id,
    md.machine_name,
    md.machine_type,
    md.status AS machine_status,

    m.location_key,
    l.location_id,
    l.location_name,

    COUNT(DISTINCT m.maintenance_id) AS maintenance_event_count,

    SUM(m.downtime_hours) AS downtime_hours,

    SUM(m.maintenance_cost) AS maintenance_cost,

    CASE
        WHEN COUNT(DISTINCT m.maintenance_id) = 0 THEN NULL
        ELSE
            SUM(m.maintenance_cost)
            / COUNT(DISTINCT m.maintenance_id)
    END AS average_maintenance_cost_per_event,

    CASE
        WHEN COUNT(DISTINCT m.maintenance_id) = 0 THEN NULL
        ELSE
            SUM(m.downtime_hours)
            / COUNT(DISTINCT m.maintenance_id)
    END AS average_downtime_hours_per_event

FROM public.fact_maintenance m
JOIN public.dim_date d
    ON m.date_key = d.date_key
JOIN public.dim_machine md
    ON m.machine_key = md.machine_key
JOIN public.dim_location l
    ON m.location_key = l.location_key

GROUP BY
    m.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    m.machine_key,
    md.machine_id,
    md.machine_name,
    md.machine_type,
    md.status,
    m.location_key,
    l.location_id,
    l.location_name;


-- ============================================================
-- EMPLOYEE OPERATIONS
-- Grain:
-- One row per date + employee.
--
-- Production and maintenance are aggregated independently before
-- being combined. This prevents fact-to-fact fan-out.
-- ============================================================

CREATE VIEW analytics.vw_employee_operations_daily AS
WITH production AS (
    SELECT
        date_key,
        employee_key,
        COUNT(DISTINCT production_id) AS production_record_count,
        SUM(quantity_produced) AS quantity_produced,
        SUM(production_hours) AS production_hours
    FROM public.fact_production
    GROUP BY
        date_key,
        employee_key
),
maintenance AS (
    SELECT
        date_key,
        employee_key,
        COUNT(DISTINCT maintenance_id) AS maintenance_event_count,
        SUM(downtime_hours) AS downtime_hours,
        SUM(maintenance_cost) AS maintenance_cost
    FROM public.fact_maintenance
    GROUP BY
        date_key,
        employee_key
)
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    e.employee_key,
    e.employee_id,
    e.employee_name,
    e.department,
    e.role,
    e.hire_date,
    e.status AS employee_status,

    COALESCE(p.production_record_count, 0)
        AS production_record_count,

    COALESCE(p.quantity_produced, 0)
        AS quantity_produced,

    COALESCE(p.production_hours, 0)
        AS production_hours,

    COALESCE(m.maintenance_event_count, 0)
        AS maintenance_event_count,

    COALESCE(m.downtime_hours, 0)
        AS downtime_hours,

    COALESCE(m.maintenance_cost, 0)
        AS maintenance_cost

FROM public.dim_employee e
CROSS JOIN public.dim_date d

LEFT JOIN production p
    ON d.date_key = p.date_key
   AND e.employee_key = p.employee_key

LEFT JOIN maintenance m
    ON d.date_key = m.date_key
   AND e.employee_key = m.employee_key

WHERE
    p.employee_key IS NOT NULL
    OR m.employee_key IS NOT NULL;


-- ============================================================
-- FINANCIAL ANALYTICS
-- ============================================================


-- ============================================================
-- FINANCIAL PERFORMANCE
-- Grain:
-- One row per date + location.
-- ============================================================

CREATE VIEW analytics.vw_financial_performance_daily AS
SELECT
    f.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    f.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.country,

    COUNT(DISTINCT f.financial_transaction_id)
        AS financial_transaction_count,

    SUM(
        CASE
            WHEN f.transaction_type = 'Revenue'
            THEN f.amount
            ELSE 0
        END
    ) AS revenue_amount,

    SUM(
        CASE
            WHEN f.transaction_type = 'Expense'
            THEN f.amount
            ELSE 0
        END
    ) AS expense_amount,

    SUM(
        CASE
            WHEN f.transaction_type = 'Transfer'
            THEN f.amount
            ELSE 0
        END
    ) AS transfer_amount,

    SUM(
        CASE
            WHEN f.transaction_type = 'Adjustment'
            THEN f.amount
            ELSE 0
        END
    ) AS adjustment_amount,

    SUM(f.amount) AS total_transaction_amount

FROM public.fact_financial_transaction f
JOIN public.dim_date d
    ON f.date_key = d.date_key
JOIN public.dim_location l
    ON f.location_key = l.location_key

GROUP BY
    f.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    f.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.country;


-- ============================================================
-- BUDGET PERFORMANCE
-- Grain:
-- One row per date + location + budget category.
--
-- Budget remains separate from financial actuals because the
-- warehouse does not provide a justified common budget/actual
-- category mapping.
-- ============================================================

CREATE VIEW analytics.vw_budget_performance_daily AS
SELECT
    b.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    b.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    b.category AS budget_category,

    COUNT(DISTINCT b.budget_id) AS budget_record_count,

    SUM(b.budget_amount) AS budget_amount

FROM public.fact_budget b
JOIN public.dim_date d
    ON b.date_key = d.date_key
JOIN public.dim_location l
    ON b.location_key = l.location_key

GROUP BY
    b.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    b.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    b.category;


-- ============================================================
-- SUSTAINABILITY ANALYTICS
-- ============================================================


-- ============================================================
-- ENERGY PERFORMANCE
-- Grain:
-- One row per date + location + energy type.
-- ============================================================

CREATE VIEW analytics.vw_energy_performance_daily AS
SELECT
    e.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    e.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    e.energy_type,
    e.unit,

    COUNT(DISTINCT e.energy_id) AS energy_record_count,

    SUM(e.consumption) AS energy_consumption

FROM public.fact_energy e
JOIN public.dim_date d
    ON e.date_key = d.date_key
JOIN public.dim_location l
    ON e.location_key = l.location_key

GROUP BY
    e.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    e.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    e.energy_type,
    e.unit;


-- ============================================================
-- EMISSIONS PERFORMANCE
-- Grain:
-- One row per date + location + emissions source.
-- ============================================================

CREATE VIEW analytics.vw_emissions_performance_daily AS
SELECT
    e.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    e.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    e.source AS emissions_source,

    COUNT(DISTINCT e.emissions_id)
        AS emissions_record_count,

    SUM(e.co2_kg) AS co2_kg

FROM public.fact_emissions e
JOIN public.dim_date d
    ON e.date_key = d.date_key
JOIN public.dim_location l
    ON e.location_key = l.location_key

GROUP BY
    e.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    e.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    e.source;


-- ============================================================
-- WASTE PERFORMANCE
-- Grain:
-- One row per date + location + waste type + disposal method.
-- ============================================================

CREATE VIEW analytics.vw_waste_performance_daily AS
SELECT
    w.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    w.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    w.waste_type,
    w.unit,
    w.disposal_method,

    COUNT(DISTINCT w.waste_id) AS waste_record_count,

    SUM(w.quantity) AS waste_quantity

FROM public.fact_waste w
JOIN public.dim_date d
    ON w.date_key = d.date_key
JOIN public.dim_location l
    ON w.location_key = l.location_key

GROUP BY
    w.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    w.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    w.waste_type,
    w.unit,
    w.disposal_method;


-- ============================================================
-- INVENTORY ANALYTICS
-- ============================================================


-- ============================================================
-- INVENTORY POSITION
-- Grain:
-- One row per date + location + product.
--
-- Inventory is a snapshot fact. This view therefore represents
-- inventory position at a given date and must not be treated as
-- a transactional flow.
-- ============================================================

CREATE VIEW analytics.vw_inventory_position_daily AS
SELECT
    i.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    i.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    i.product_key,
    p.product_id,
    p.product_name,
    p.category AS product_category,
    p.supplier_id,

    SUM(i.quantity_on_hand) AS quantity_on_hand,
    SUM(i.inventory_value) AS inventory_value,
    MAX(i.reorder_point) AS reorder_point,

    CASE
        WHEN SUM(i.quantity_on_hand) < MAX(i.reorder_point)
        THEN TRUE
        ELSE FALSE
    END AS below_reorder_point,

    COUNT(DISTINCT i.inventory_id)
        AS inventory_record_count

FROM public.fact_inventory i
JOIN public.dim_date d
    ON i.date_key = d.date_key
JOIN public.dim_location l
    ON i.location_key = l.location_key
JOIN public.dim_product p
    ON i.product_key = p.product_key

GROUP BY
    i.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    i.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    i.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.supplier_id;