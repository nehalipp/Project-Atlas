DROP VIEW IF EXISTS analytics.vw_sales_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_production_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_maintenance_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_financial_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_budget_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_energy_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_emissions_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_waste_kpis_daily;
DROP VIEW IF EXISTS analytics.vw_inventory_kpis_daily;


-- ============================================================
-- SALES
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_sales_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    COUNT(DISTINCT s.sales_id) AS sales_transaction_count,
    SUM(s.quantity) AS sales_quantity,
    SUM(s.revenue) AS total_revenue,

    CASE
        WHEN SUM(s.quantity) = 0 THEN NULL
        ELSE SUM(s.revenue) / SUM(s.quantity)
    END AS average_selling_price,

    SUM(s.revenue * s.discount_rate) AS estimated_discount_amount

FROM public.fact_sales s
JOIN public.dim_date d
    ON s.date_key = d.date_key

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- PRODUCTION
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_production_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

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

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- MAINTENANCE
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_maintenance_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

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

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- FINANCIAL TRANSACTIONS
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_financial_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    COUNT(DISTINCT f.financial_transaction_id)
        AS financial_transaction_count,

    SUM(f.amount) AS total_transaction_amount,

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
    ) AS adjustment_amount

FROM public.fact_financial_transaction f
JOIN public.dim_date d
    ON f.date_key = d.date_key

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- BUDGET
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_budget_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    SUM(b.budget_amount) AS total_budget_amount,

    COUNT(DISTINCT b.budget_id) AS budget_record_count

FROM public.fact_budget b
JOIN public.dim_date d
    ON b.date_key = d.date_key

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- ENERGY
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_energy_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    SUM(e.consumption) AS total_energy_consumption_kwh,

    COUNT(DISTINCT e.energy_id) AS energy_record_count

FROM public.fact_energy e
JOIN public.dim_date d
    ON e.date_key = d.date_key

WHERE e.unit = 'kWh'

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- EMISSIONS
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_emissions_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    SUM(e.co2_kg) AS total_co2_kg,

    COUNT(DISTINCT e.emissions_id) AS emissions_record_count

FROM public.fact_emissions e
JOIN public.dim_date d
    ON e.date_key = d.date_key

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- WASTE
-- Grain: one row per date
-- ============================================================

CREATE VIEW analytics.vw_waste_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    SUM(w.quantity) AS total_waste_kg,

    COUNT(DISTINCT w.waste_id) AS waste_record_count

FROM public.fact_waste w
JOIN public.dim_date d
    ON w.date_key = d.date_key

WHERE w.unit = 'kg'

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;


-- ============================================================
-- INVENTORY
-- Grain: one row per date
-- Snapshot fact -- do not sum inventory snapshots across dates.
-- ============================================================

CREATE VIEW analytics.vw_inventory_kpis_daily AS
SELECT
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    SUM(i.quantity_on_hand) AS quantity_on_hand,

    SUM(i.inventory_value) AS inventory_value,

    SUM(
        CASE
            WHEN i.quantity_on_hand < i.reorder_point
            THEN 1
            ELSE 0
        END
    ) AS items_below_reorder_point,

    COUNT(DISTINCT i.inventory_id) AS inventory_record_count

FROM public.fact_inventory i
JOIN public.dim_date d
    ON i.date_key = d.date_key

GROUP BY
    d.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name;