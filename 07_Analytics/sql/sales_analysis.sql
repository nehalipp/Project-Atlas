-- Project Atlas
-- Phase 7 - Sales Analysis
--
-- Sales performance analysis.
-- Quantity metrics are always analyzed by unit_of_measure.
-- Revenue and transaction metrics can be aggregated independently.

-- ============================================================
-- SALES PERFORMANCE BY DAY AND UNIT
-- ============================================================

SELECT
    d.full_date,
    s.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue,
    SUM(s.discount_amount) AS discount_amount
FROM fact_sales s
JOIN dim_date d
    ON s.date_key = d.date_key
GROUP BY
    d.full_date,
    s.unit_of_measure
ORDER BY
    d.full_date,
    s.unit_of_measure;


-- ============================================================
-- REVENUE BY PRODUCT CATEGORY AND UNIT
-- ============================================================

SELECT
    p.category,
    s.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue,
    SUM(s.discount_amount) AS discount_amount
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY
    p.category,
    s.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- REVENUE BY LOCATION AND UNIT
-- ============================================================

SELECT
    l.location_name,
    s.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_location l
    ON s.location_key = l.location_key
GROUP BY
    l.location_name,
    s.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- REVENUE BY CUSTOMER SEGMENT AND UNIT
-- ============================================================

SELECT
    c.customer_segment,
    s.unit_of_measure,
    COUNT(*) AS transactions,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_customer c
    ON s.customer_key = c.customer_key
GROUP BY
    c.customer_segment,
    s.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- SALES SUMMARY BY UNIT
-- ============================================================

SELECT
    unit_of_measure,
    COUNT(*) AS transactions,
    SUM(quantity) AS quantity_sold,
    SUM(revenue) AS revenue,
    SUM(discount_amount) AS discount_amount
FROM fact_sales
GROUP BY unit_of_measure
ORDER BY revenue DESC;
