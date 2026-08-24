-- Project Atlas
-- Phase 7 - Operations Analysis


-- Production performance
SELECT
    d.year,
    d.month,
    SUM(f.planned_quantity) AS planned_quantity,
    SUM(f.produced_quantity) AS produced_quantity,
    SUM(f.defect_quantity) AS defect_quantity,
    SUM(f.production_hours) AS production_hours,
    SUM(f.produced_quantity) - SUM(f.planned_quantity) AS production_variance
FROM fact_production f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- Production by location
SELECT
    l.location_name,
    SUM(f.planned_quantity) AS planned_quantity,
    SUM(f.produced_quantity) AS produced_quantity,
    SUM(f.defect_quantity) AS defect_quantity,
    SUM(f.production_hours) AS production_hours
FROM fact_production f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.location_name
ORDER BY produced_quantity DESC;


-- Maintenance performance
SELECT
    d.year,
    d.month,
    SUM(m.maintenance_hours) AS maintenance_hours,
    SUM(m.downtime_hours) AS downtime_hours,
    SUM(m.maintenance_cost) AS maintenance_cost,
    COUNT(*) AS maintenance_events
FROM fact_maintenance m
JOIN dim_date d
    ON m.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- Machine maintenance performance
SELECT
    mc.machine_name,
    mc.machine_type,
    COUNT(m.maintenance_key) AS maintenance_events,
    SUM(m.maintenance_hours) AS maintenance_hours,
    SUM(m.downtime_hours) AS downtime_hours,
    SUM(m.maintenance_cost) AS maintenance_cost
FROM fact_maintenance m
JOIN dim_machine mc
    ON m.machine_key = mc.machine_key
GROUP BY
    mc.machine_name,
    mc.machine_type
ORDER BY downtime_hours DESC;