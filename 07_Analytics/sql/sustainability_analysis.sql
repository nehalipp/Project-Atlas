-- Project Atlas
-- Phase 7 - Sustainability Analysis
--
-- Energy is measured in kWh.
-- CO2 emissions are measured in kg.
-- Waste is analyzed by its explicit unit_of_measure.

-- ============================================================
-- ENERGY CONSUMPTION BY SOURCE
-- ============================================================

SELECT
    energy_source,
    unit_of_measure,
    SUM(energy_consumption) AS energy_consumption
FROM fact_energy
GROUP BY
    energy_source,
    unit_of_measure
ORDER BY
    energy_consumption DESC;


-- ============================================================
-- ENERGY BY LOCATION
-- ============================================================

SELECT
    l.location_name,
    e.unit_of_measure,
    SUM(e.energy_consumption) AS energy_consumption
FROM fact_energy e
JOIN dim_location l
    ON e.location_key = l.location_key
GROUP BY
    l.location_name,
    e.unit_of_measure
ORDER BY
    energy_consumption DESC;


-- ============================================================
-- EMISSIONS BY CATEGORY
-- ============================================================

SELECT
    emissions_category,
    unit_of_measure,
    SUM(co2_emissions) AS co2_emissions
FROM fact_emissions
GROUP BY
    emissions_category,
    unit_of_measure
ORDER BY
    co2_emissions DESC;


-- ============================================================
-- WASTE BY CATEGORY AND DISPOSAL METHOD
-- ============================================================

SELECT
    waste_category,
    disposal_method,
    unit_of_measure,
    SUM(waste_quantity) AS waste_quantity
FROM fact_waste
GROUP BY
    waste_category,
    disposal_method,
    unit_of_measure
ORDER BY
    waste_quantity DESC;


-- ============================================================
-- MONTHLY ENERGY
-- ============================================================

SELECT
    d.year,
    d.month,
    e.unit_of_measure,
    SUM(e.energy_consumption) AS energy_consumption
FROM fact_energy e
JOIN dim_date d
    ON e.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    e.unit_of_measure
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- MONTHLY EMISSIONS
-- ============================================================

SELECT
    d.year,
    d.month,
    e.unit_of_measure,
    SUM(e.co2_emissions) AS co2_emissions
FROM fact_emissions e
JOIN dim_date d
    ON e.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    e.unit_of_measure
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- MONTHLY WASTE
-- ============================================================

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
ORDER BY
    d.year,
    d.month;
