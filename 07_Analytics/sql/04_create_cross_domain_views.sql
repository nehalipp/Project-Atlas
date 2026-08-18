-- ============================================================
-- Project Atlas — Phase 7.3
-- Cross-Domain Analytics
--
-- Purpose:
-- Create reusable cross-domain analytical views while strictly
-- controlling fact grain and preventing fan-out/double counting.
--
-- Required cross-domain analyses:
--
-- 1. Sales + Production + Inventory
--    Grain: date + location + product
--
-- 2. Production + Maintenance
--    Grain: date + location + machine
--
-- 3. Production + Energy + Emissions
--    Grain: date + location
--
-- Design principle:
-- Aggregate each fact independently to the target analytical
-- grain before joining facts together.
-- ============================================================


CREATE SCHEMA IF NOT EXISTS analytics;


-- ============================================================
-- CLEANUP
-- ============================================================

DROP VIEW IF EXISTS analytics.vw_production_energy_emissions_daily;
DROP VIEW IF EXISTS analytics.vw_production_maintenance_daily;
DROP VIEW IF EXISTS analytics.vw_sales_production_inventory_daily;


-- ============================================================
-- 1. SALES + PRODUCTION + INVENTORY
-- ============================================================
--
-- Business question:
-- Are product sales, production output and inventory position
-- aligned by location?
--
-- Common grain:
-- One row represents one date + one location + one product.
--
-- Each fact is aggregated independently before joining.
-- ============================================================

CREATE VIEW analytics.vw_sales_production_inventory_daily AS

WITH sales AS (

    SELECT
        s.date_key,
        s.location_key,
        s.product_key,

        COUNT(DISTINCT s.sales_id)
            AS sales_transaction_count,

        SUM(s.quantity)
            AS sales_quantity,

        SUM(s.revenue)
            AS sales_revenue,

        AVG(s.discount_rate)
            AS average_discount_rate

    FROM public.fact_sales s

    GROUP BY
        s.date_key,
        s.location_key,
        s.product_key
),

production AS (

    SELECT
        p.date_key,
        p.location_key,
        p.product_key,

        COUNT(DISTINCT p.production_id)
            AS production_record_count,

        SUM(p.planned_quantity)
            AS planned_production_quantity,

        SUM(p.quantity_produced)
            AS production_quantity,

        SUM(p.production_hours)
            AS production_hours,

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
        END) AS cancelled_production_count

    FROM public.fact_production p

    GROUP BY
        p.date_key,
        p.location_key,
        p.product_key
),

inventory AS (

    SELECT
        i.date_key,
        i.location_key,
        i.product_key,

        SUM(i.quantity_on_hand)
            AS quantity_on_hand,

        SUM(i.inventory_value)
            AS inventory_value,

        MAX(i.reorder_point)
            AS reorder_point,

        COUNT(DISTINCT i.inventory_id)
            AS inventory_record_count

    FROM public.fact_inventory i

    GROUP BY
        i.date_key,
        i.location_key,
        i.product_key
),

combined AS (

    SELECT
        COALESCE(
            s.date_key,
            p.date_key,
            i.date_key
        ) AS date_key,

        COALESCE(
            s.location_key,
            p.location_key,
            i.location_key
        ) AS location_key,

        COALESCE(
            s.product_key,
            p.product_key,
            i.product_key
        ) AS product_key,

        COALESCE(
            s.sales_transaction_count,
            0
        ) AS sales_transaction_count,

        COALESCE(
            s.sales_quantity,
            0
        ) AS sales_quantity,

        COALESCE(
            s.sales_revenue,
            0
        ) AS sales_revenue,

        s.average_discount_rate,

        COALESCE(
            p.production_record_count,
            0
        ) AS production_record_count,

        COALESCE(
            p.planned_production_quantity,
            0
        ) AS planned_production_quantity,

        COALESCE(
            p.production_quantity,
            0
        ) AS production_quantity,

        COALESCE(
            p.production_hours,
            0
        ) AS production_hours,

        COALESCE(
            p.completed_production_count,
            0
        ) AS completed_production_count,

        COALESCE(
            p.partial_production_count,
            0
        ) AS partial_production_count,

        COALESCE(
            p.cancelled_production_count,
            0
        ) AS cancelled_production_count,

        COALESCE(
            i.quantity_on_hand,
            0
        ) AS quantity_on_hand,

        COALESCE(
            i.inventory_value,
            0
        ) AS inventory_value,

        i.reorder_point,

        COALESCE(
            i.inventory_record_count,
            0
        ) AS inventory_record_count

    FROM sales s

    FULL OUTER JOIN production p
        ON s.date_key = p.date_key
       AND s.location_key = p.location_key
       AND s.product_key = p.product_key

    FULL OUTER JOIN inventory i
        ON COALESCE(
            s.date_key,
            p.date_key
        ) = i.date_key

       AND COALESCE(
            s.location_key,
            p.location_key
        ) = i.location_key

       AND COALESCE(
            s.product_key,
            p.product_key
        ) = i.product_key
)

SELECT
    c.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    c.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.city,
    l.state_region,
    l.country,

    c.product_key,
    pr.product_id,
    pr.product_name,
    pr.category AS product_category,
    pr.supplier_id,

    c.sales_transaction_count,
    c.sales_quantity,
    c.sales_revenue,
    c.average_discount_rate,

    c.production_record_count,
    c.planned_production_quantity,
    c.production_quantity,
    c.production_hours,

    c.completed_production_count,
    c.partial_production_count,
    c.cancelled_production_count,

    c.quantity_on_hand,
    c.inventory_value,
    c.reorder_point,
    c.inventory_record_count,

    -- --------------------------------------------------------
    -- Cross-domain metrics
    -- --------------------------------------------------------

    c.production_quantity
        -
        c.sales_quantity
        AS production_minus_sales_quantity,

    CASE
        WHEN c.planned_production_quantity = 0 THEN NULL
        ELSE
            c.production_quantity::numeric
            /
            NULLIF(
                c.planned_production_quantity,
                0
            )
    END AS production_attainment_rate,

    CASE
        WHEN c.sales_quantity = 0 THEN NULL
        ELSE
            c.quantity_on_hand::numeric
            /
            NULLIF(
                c.sales_quantity,
                0
            )
    END AS inventory_to_daily_sales_ratio,

    CASE
        WHEN c.reorder_point IS NULL THEN NULL
        WHEN c.quantity_on_hand < c.reorder_point
        THEN TRUE
        ELSE FALSE
    END AS below_reorder_point

FROM combined c

JOIN public.dim_date d
    ON c.date_key = d.date_key

JOIN public.dim_location l
    ON c.location_key = l.location_key

JOIN public.dim_product pr
    ON c.product_key = pr.product_key;


-- ============================================================
-- 2. PRODUCTION + MAINTENANCE
-- ============================================================
--
-- Business question:
-- How are production activity and machine maintenance/downtime
-- related?
--
-- Common grain:
-- One row represents one date + one location + one machine.
--
-- Production and maintenance are aggregated independently.
-- ============================================================

CREATE VIEW analytics.vw_production_maintenance_daily AS

WITH production AS (

    SELECT
        p.date_key,
        p.location_key,
        p.machine_key,

        COUNT(DISTINCT p.production_id)
            AS production_record_count,

        SUM(p.planned_quantity)
            AS planned_production_quantity,

        SUM(p.quantity_produced)
            AS production_quantity,

        SUM(p.production_hours)
            AS production_hours,

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
        END) AS cancelled_production_count

    FROM public.fact_production p

    GROUP BY
        p.date_key,
        p.location_key,
        p.machine_key
),

maintenance AS (

    SELECT
        m.date_key,
        m.location_key,
        m.machine_key,

        COUNT(DISTINCT m.maintenance_id)
            AS maintenance_event_count,

        SUM(m.downtime_hours)
            AS downtime_hours,

        SUM(m.maintenance_cost)
            AS maintenance_cost

    FROM public.fact_maintenance m

    GROUP BY
        m.date_key,
        m.location_key,
        m.machine_key
),

combined AS (

    SELECT
        COALESCE(
            p.date_key,
            m.date_key
        ) AS date_key,

        COALESCE(
            p.location_key,
            m.location_key
        ) AS location_key,

        COALESCE(
            p.machine_key,
            m.machine_key
        ) AS machine_key,

        COALESCE(
            p.production_record_count,
            0
        ) AS production_record_count,

        COALESCE(
            p.planned_production_quantity,
            0
        ) AS planned_production_quantity,

        COALESCE(
            p.production_quantity,
            0
        ) AS production_quantity,

        COALESCE(
            p.production_hours,
            0
        ) AS production_hours,

        COALESCE(
            p.completed_production_count,
            0
        ) AS completed_production_count,

        COALESCE(
            p.partial_production_count,
            0
        ) AS partial_production_count,

        COALESCE(
            p.cancelled_production_count,
            0
        ) AS cancelled_production_count,

        COALESCE(
            m.maintenance_event_count,
            0
        ) AS maintenance_event_count,

        COALESCE(
            m.downtime_hours,
            0
        ) AS downtime_hours,

        COALESCE(
            m.maintenance_cost,
            0
        ) AS maintenance_cost

    FROM production p

    FULL OUTER JOIN maintenance m
        ON p.date_key = m.date_key
       AND p.location_key = m.location_key
       AND p.machine_key = m.machine_key
)

SELECT
    c.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    c.location_key,
    l.location_id,
    l.location_name,
    l.location_type,

    c.machine_key,
    m.machine_id,
    m.machine_name,
    m.machine_type,
    m.installation_date,
    m.status AS machine_status,

    c.production_record_count,
    c.planned_production_quantity,
    c.production_quantity,
    c.production_hours,

    c.completed_production_count,
    c.partial_production_count,
    c.cancelled_production_count,

    c.maintenance_event_count,
    c.downtime_hours,
    c.maintenance_cost,

    -- --------------------------------------------------------
    -- Cross-domain metrics
    -- --------------------------------------------------------

    CASE
        WHEN c.planned_production_quantity = 0 THEN NULL
        ELSE
            c.production_quantity::numeric
            /
            NULLIF(
                c.planned_production_quantity,
                0
            )
    END AS production_attainment_rate,

    CASE
        WHEN c.production_hours = 0 THEN NULL
        ELSE
            c.production_quantity::numeric
            /
            NULLIF(
                c.production_hours,
                0
            )
    END AS production_rate,

    CASE
        WHEN c.production_hours = 0 THEN NULL
        ELSE
            c.downtime_hours::numeric
            /
            NULLIF(
                c.production_hours,
                0
            )
    END AS downtime_to_production_hours_ratio,

    CASE
        WHEN c.maintenance_event_count = 0 THEN NULL
        ELSE
            c.maintenance_cost::numeric
            /
            NULLIF(
                c.maintenance_event_count,
                0
            )
    END AS average_maintenance_cost_per_event,

    CASE
        WHEN c.production_quantity = 0 THEN NULL
        ELSE
            c.maintenance_cost::numeric
            /
            NULLIF(
                c.production_quantity,
                0
            )
    END AS maintenance_cost_per_produced_unit

FROM combined c

JOIN public.dim_date d
    ON c.date_key = d.date_key

JOIN public.dim_location l
    ON c.location_key = l.location_key

JOIN public.dim_machine m
    ON c.machine_key = m.machine_key;


-- ============================================================
-- 3. PRODUCTION + ENERGY + EMISSIONS
-- ============================================================
--
-- Business question:
-- What is the relationship between production output, energy
-- consumption and emissions at each location?
--
-- Common grain:
-- One row represents one date + one location.
--
-- Production, energy and emissions are independently aggregated.
--
-- Intensity metrics:
-- kWh / production unit
-- kg CO2 / production unit
--
-- These are analytical intensity measures, not causal claims.
-- ============================================================

CREATE VIEW analytics.vw_production_energy_emissions_daily AS

WITH production AS (

    SELECT
        p.date_key,
        p.location_key,

        COUNT(DISTINCT p.production_id)
            AS production_record_count,

        SUM(p.planned_quantity)
            AS planned_production_quantity,

        SUM(p.quantity_produced)
            AS production_quantity,

        SUM(p.production_hours)
            AS production_hours

    FROM public.fact_production p

    GROUP BY
        p.date_key,
        p.location_key
),

energy AS (

    SELECT
        e.date_key,
        e.location_key,

        SUM(
            CASE
                WHEN e.unit = 'kWh'
                THEN e.consumption
                ELSE 0
            END
        ) AS energy_consumption_kwh,

        COUNT(DISTINCT e.energy_id)
            AS energy_record_count

    FROM public.fact_energy e

    GROUP BY
        e.date_key,
        e.location_key
),

emissions AS (

    SELECT
        e.date_key,
        e.location_key,

        SUM(e.co2_kg)
            AS co2_kg,

        COUNT(DISTINCT e.emissions_id)
            AS emissions_record_count

    FROM public.fact_emissions e

    GROUP BY
        e.date_key,
        e.location_key
),

combined AS (

    SELECT
        COALESCE(
            p.date_key,
            e.date_key,
            em.date_key
        ) AS date_key,

        COALESCE(
            p.location_key,
            e.location_key,
            em.location_key
        ) AS location_key,

        COALESCE(
            p.production_record_count,
            0
        ) AS production_record_count,

        COALESCE(
            p.planned_production_quantity,
            0
        ) AS planned_production_quantity,

        COALESCE(
            p.production_quantity,
            0
        ) AS production_quantity,

        COALESCE(
            p.production_hours,
            0
        ) AS production_hours,

        COALESCE(
            e.energy_consumption_kwh,
            0
        ) AS energy_consumption_kwh,

        COALESCE(
            e.energy_record_count,
            0
        ) AS energy_record_count,

        COALESCE(
            em.co2_kg,
            0
        ) AS co2_kg,

        COALESCE(
            em.emissions_record_count,
            0
        ) AS emissions_record_count

    FROM production p

    FULL OUTER JOIN energy e
        ON p.date_key = e.date_key
       AND p.location_key = e.location_key

    FULL OUTER JOIN emissions em
        ON COALESCE(
            p.date_key,
            e.date_key
        ) = em.date_key

       AND COALESCE(
            p.location_key,
            e.location_key
        ) = em.location_key
)

SELECT
    c.date_key,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,

    c.location_key,
    l.location_id,
    l.location_name,
    l.location_type,
    l.city,
    l.state_region,
    l.country,

    c.production_record_count,
    c.planned_production_quantity,
    c.production_quantity,
    c.production_hours,

    c.energy_record_count,
    c.energy_consumption_kwh,

    c.emissions_record_count,
    c.co2_kg,

    -- --------------------------------------------------------
    -- Cross-domain metrics
    -- --------------------------------------------------------

    CASE
        WHEN c.planned_production_quantity = 0 THEN NULL
        ELSE
            c.production_quantity::numeric
            /
            NULLIF(
                c.planned_production_quantity,
                0
            )
    END AS production_attainment_rate,

    CASE
        WHEN c.production_hours = 0 THEN NULL
        ELSE
            c.production_quantity::numeric
            /
            NULLIF(
                c.production_hours,
                0
            )
    END AS production_rate,

    CASE
        WHEN c.production_quantity = 0 THEN NULL
        ELSE
            c.energy_consumption_kwh::numeric
            /
            NULLIF(
                c.production_quantity,
                0
            )
    END AS energy_intensity_kwh_per_unit,

    CASE
        WHEN c.production_quantity = 0 THEN NULL
        ELSE
            c.co2_kg::numeric
            /
            NULLIF(
                c.production_quantity,
                0
            )
    END AS emissions_intensity_kg_per_unit

FROM combined c

JOIN public.dim_date d
    ON c.date_key = d.date_key

JOIN public.dim_location l
    ON c.location_key = l.location_key;