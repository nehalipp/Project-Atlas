-- Project Atlas
-- Phase 7 - Executive KPIs


-- Commercial KPIs
SELECT
    SUM(revenue) AS total_revenue,
    SUM(quantity) AS total_units_sold,
    COUNT(*) AS total_transactions,
    AVG(revenue) AS average_transaction_revenue,
    SUM(discount_amount) AS total_discount
FROM fact_sales;


-- Operational KPIs
SELECT
    SUM(planned_quantity) AS planned_production,
    SUM(produced_quantity) AS produced_quantity,
    SUM(defect_quantity) AS defect_quantity,
    SUM(produced_quantity) - SUM(planned_quantity) AS production_variance,
    SUM(production_hours) AS production_hours
FROM fact_production;


-- Maintenance KPIs
SELECT
    COUNT(*) AS maintenance_events,
    SUM(maintenance_hours) AS maintenance_hours,
    SUM(downtime_hours) AS downtime_hours,
    SUM(maintenance_cost) AS maintenance_cost
FROM fact_maintenance;


-- Financial KPIs
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


-- Budget KPI
SELECT
    SUM(budget_amount) AS total_budget
FROM fact_budget;


-- Sustainability KPIs
SELECT
    (SELECT SUM(energy_consumption) FROM fact_energy)
        AS total_energy_consumption,
    (SELECT SUM(co2_emissions) FROM fact_emissions)
        AS total_co2_emissions,
    (SELECT SUM(waste_quantity) FROM fact_waste)
        AS total_waste_quantity;


-- Inventory KPI
SELECT
    SUM(closing_quantity) AS closing_inventory_quantity,
    SUM(
        CASE
            WHEN closing_quantity <= reorder_point
            THEN 1
            ELSE 0
        END
    ) AS inventory_rows_at_or_below_reorder_point
FROM fact_inventory;

-- Production KPI
WITH monthly_production AS (
    SELECT
        d.year,
        d.month,
        SUM(p.produced_quantity) AS produced_quantity
    FROM fact_production p
    JOIN dim_date d
        ON p.date_key = d.date_key
    GROUP BY d.year, d.month
),
monthly_energy AS (
    SELECT
        d.year,
        d.month,
        SUM(e.energy_consumption) AS energy_consumption
    FROM fact_energy e
    JOIN dim_date d
        ON e.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT
    p.year,
    p.month,
    p.produced_quantity,
    e.energy_consumption,
    e.energy_consumption / NULLIF(p.produced_quantity, 0)
        AS energy_per_unit_produced
FROM monthly_production p
JOIN monthly_energy e
    ON p.year = e.year
   AND p.month = e.month
ORDER BY p.year, p.month;