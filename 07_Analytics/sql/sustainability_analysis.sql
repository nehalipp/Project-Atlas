-- Project Atlas
-- Phase 7 - Sustainability Analysis


-- Energy consumption
SELECT
    energy_source,
    SUM(energy_consumption) AS energy_consumption
FROM fact_energy
GROUP BY energy_source
ORDER BY energy_consumption DESC;


-- Energy by location
SELECT
    l.location_name,
    SUM(e.energy_consumption) AS energy_consumption
FROM fact_energy e
JOIN dim_location l
    ON e.location_key = l.location_key
GROUP BY l.location_name
ORDER BY energy_consumption DESC;


-- Emissions by category
SELECT
    emissions_category,
    SUM(co2_emissions) AS co2_emissions
FROM fact_emissions
GROUP BY emissions_category
ORDER BY co2_emissions DESC;


-- Waste by category and disposal method
SELECT
    waste_category,
    disposal_method,
    SUM(waste_quantity) AS waste_quantity
FROM fact_waste
GROUP BY
    waste_category,
    disposal_method
ORDER BY waste_quantity DESC;


-- Monthly sustainability metrics
WITH monthly_energy AS (
    SELECT
        d.year,
        d.month,
        SUM(e.energy_consumption) AS energy_consumption
    FROM fact_energy e
    JOIN dim_date d
        ON e.date_key = d.date_key
    GROUP BY d.year, d.month
),
monthly_emissions AS (
    SELECT
        d.year,
        d.month,
        SUM(e.co2_emissions) AS co2_emissions
    FROM fact_emissions e
    JOIN dim_date d
        ON e.date_key = d.date_key
    GROUP BY d.year, d.month
),
monthly_waste AS (
    SELECT
        d.year,
        d.month,
        SUM(w.waste_quantity) AS waste_quantity
    FROM fact_waste w
    JOIN dim_date d
        ON w.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT
    COALESCE(e.year, em.year, w.year) AS year,
    COALESCE(e.month, em.month, w.month) AS month,
    e.energy_consumption,
    em.co2_emissions,
    w.waste_quantity
FROM monthly_energy e
FULL OUTER JOIN monthly_emissions em
    ON e.year = em.year
   AND e.month = em.month
FULL OUTER JOIN monthly_waste w
    ON COALESCE(e.year, em.year) = w.year
   AND COALESCE(e.month, em.month) = w.month
ORDER BY year, month;