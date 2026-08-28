-- Project Atlas
-- Phase 7 - Executive KPIs
--
-- Governed executive metrics.
--
-- Important:
-- Quantity-based measures are reported by unit_of_measure.
-- Quantities from different units must not be combined into
-- a single total.
--
-- Monetary, time, energy and emissions measures are aggregated
-- independently according to their defined measurement units.

-- ============================================================
-- COMMERCIAL KPIs
-- ============================================================

SELECT
    SUM(revenue) AS total_revenue,
    COUNT(*) AS total_transactions,
    AVG(revenue) AS average_transaction_revenue,
    SUM(discount_amount) AS total_discount
FROM fact_sales;


-- ============================================================
-- COMMERCIAL QUANTITY KPIs BY UNIT
-- ============================================================

SELECT
    unit_of_measure,
    SUM(quantity) AS quantity_sold,
    COUNT(*) AS transactions,
    SUM(revenue) AS revenue
FROM fact_sales
GROUP BY
    unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- OPERATIONAL KPIs BY UNIT
-- ============================================================

SELECT
    unit_of_measure,
    SUM(planned_quantity) AS planned_quantity,
    SUM(produced_quantity) AS produced_quantity,
    SUM(defect_quantity) AS defect_quantity,
    SUM(produced_quantity) - SUM(planned_quantity)
        AS production_variance,
    ROUND(
        100.0 * SUM(produced_quantity)
        / NULLIF(SUM(planned_quantity), 0),
        2
    ) AS production_achievement_pct,
    SUM(production_hours) AS production_hours
FROM fact_production
GROUP BY
    unit_of_measure
ORDER BY
    unit_of_measure;


-- ============================================================
-- MAINTENANCE KPIs
-- ============================================================

SELECT
    COUNT(*) AS maintenance_events,
    SUM(maintenance_hours) AS maintenance_hours,
    SUM(downtime_hours) AS downtime_hours,
    SUM(maintenance_cost) AS maintenance_cost
FROM fact_maintenance;


-- ============================================================
-- FINANCIAL KPIs
-- ============================================================

SELECT
    SUM(
        CASE
            WHEN transaction_type = 'Revenue'
            THEN transaction_amount
            ELSE 0
        END
    ) AS financial_revenue,

    SUM(
        CASE
            WHEN transaction_type = 'Expense'
            THEN transaction_amount
            ELSE 0
        END
    ) AS financial_expense,

    SUM(
        CASE
            WHEN transaction_type = 'Cost'
            THEN transaction_amount
            ELSE 0
        END
    ) AS financial_cost

FROM fact_financial_transaction;


-- ============================================================
-- BUDGET KPI
-- ============================================================

SELECT
    SUM(budget_amount) AS total_budget
FROM fact_budget;


-- ============================================================
-- SUSTAINABILITY KPIs
-- ============================================================

SELECT
    SUM(energy_consumption) AS total_energy_consumption_kwh
FROM fact_energy;


SELECT
    SUM(co2_emissions) AS total_co2_emissions_kg
FROM fact_emissions;


SELECT
    unit_of_measure,
    SUM(waste_quantity) AS total_waste_quantity
FROM fact_waste
GROUP BY
    unit_of_measure
ORDER BY
    unit_of_measure;


-- ============================================================
-- INVENTORY KPI BY UNIT
-- ============================================================
--
-- Inventory is a periodic snapshot.
-- Closing inventory should be evaluated at a reporting date.
-- Therefore, historical snapshots must not be blindly summed.
--
-- This query returns the latest available snapshot by unit.

WITH latest_inventory_date AS (
    SELECT
        MAX(date_key) AS latest_date_key
    FROM fact_inventory
)

SELECT
    i.unit_of_measure,
    SUM(i.closing_quantity) AS closing_inventory_quantity,
    SUM(
        CASE
            WHEN i.closing_quantity <= i.reorder_point
            THEN 1
            ELSE 0
        END
    ) AS inventory_rows_at_or_below_reorder_point
FROM fact_inventory i
JOIN latest_inventory_date d
    ON i.date_key = d.latest_date_key
GROUP BY
    i.unit_of_measure
ORDER BY
    i.unit_of_measure;


-- ============================================================
-- MONTHLY PRODUCTION BY UNIT
-- ============================================================

SELECT
    d.year,
    d.month,
    p.unit_of_measure,
    SUM(p.planned_quantity) AS planned_quantity,
    SUM(p.produced_quantity) AS produced_quantity,
    SUM(p.defect_quantity) AS defect_quantity,
    SUM(p.production_hours) AS production_hours
FROM fact_production p
JOIN dim_date d
    ON p.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    p.unit_of_measure
ORDER BY
    d.year,
    d.month,
    p.unit_of_measure;


-- ============================================================
-- MONTHLY ENERGY
-- ============================================================

SELECT
    d.year,
    d.month,
    SUM(e.energy_consumption) AS energy_consumption_kwh
FROM fact_energy e
JOIN dim_date d
    ON e.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- MONTHLY SUSTAINABILITY METRICS
-- ============================================================

WITH monthly_energy AS (
    SELECT
        d.year,
        d.month,
        SUM(e.energy_consumption) AS energy_consumption_kwh
    FROM fact_energy e
    JOIN dim_date d
        ON e.date_key = d.date_key
    GROUP BY
        d.year,
        d.month
),

monthly_emissions AS (
    SELECT
        d.year,
        d.month,
        SUM(e.co2_emissions) AS co2_emissions_kg
    FROM fact_emissions e
    JOIN dim_date d
        ON e.date_key = d.date_key
    GROUP BY
        d.year,
        d.month
),

monthly_waste AS (
    SELECT
        d.year,
        d.month,
        w.unit_of_measure,
        SUM(w.waste_quantity) AS waste_quantity
    FROM fact_waste w
    JOIN dim_date d
        ON w.date_key = d.date_key
    GROUP BY
        d.year,
        d.month,
        w.unit_of_measure
)

SELECT
    COALESCE(e.year, em.year, w.year) AS year,
    COALESCE(e.month, em.month, w.month) AS month,
    e.energy_consumption_kwh,
    em.co2_emissions_kg,
    w.unit_of_measure AS waste_unit_of_measure,
    w.waste_quantity
FROM monthly_energy e
FULL OUTER JOIN monthly_emissions em
    ON e.year = em.year
   AND e.month = em.month
FULL OUTER JOIN monthly_waste w
    ON COALESCE(e.year, em.year) = w.year
   AND COALESCE(e.month, em.month) = w.month
ORDER BY
    year,
    month,
    waste_unit_of_measure;
