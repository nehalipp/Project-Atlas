-- Project Atlas
-- Phase 7 - Product Analysis
--
-- Product performance analysis.
-- Product quantities are reported using the product's
-- associated unit_of_measure.

-- ============================================================
-- PRODUCT PERFORMANCE
-- ============================================================

SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue,
    AVG(s.unit_price) AS average_selling_price
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY
    p.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- CATEGORY PERFORMANCE
-- ============================================================

SELECT
    p.category,
    p.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue,
    AVG(s.unit_price) AS average_selling_price
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY
    p.category,
    p.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- SUBCATEGORY PERFORMANCE
-- ============================================================

SELECT
    p.category,
    p.subcategory,
    p.unit_of_measure,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue,
    AVG(s.unit_price) AS average_selling_price
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY
    p.category,
    p.subcategory,
    p.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- SUPPLIER-ASSOCIATED PRODUCT SALES
-- ============================================================

SELECT
    sp.supplier_key,
    sp.supplier_name,
    p.unit_of_measure,
    COUNT(DISTINCT p.product_key) AS products,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
JOIN dim_supplier sp
    ON p.supplier_key = sp.supplier_key
GROUP BY
    sp.supplier_key,
    sp.supplier_name,
    p.unit_of_measure
ORDER BY
    revenue DESC;
