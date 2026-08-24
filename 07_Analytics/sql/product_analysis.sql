-- Project Atlas
-- Phase 7 - Product Analysis

-- Product performance
SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    SUM(s.quantity) AS units_sold,
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
    p.subcategory
ORDER BY revenue DESC;


-- Category performance
SELECT
    p.category,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS revenue,
    AVG(s.unit_price) AS average_selling_price
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;


-- Supplier-associated product sales
SELECT
    sp.supplier_key,
    sp.supplier_name,
    COUNT(DISTINCT p.product_key) AS products,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
JOIN dim_supplier sp
    ON p.supplier_key = sp.supplier_key
GROUP BY
    sp.supplier_key,
    sp.supplier_name
ORDER BY revenue DESC;