-- Project Atlas
-- Phase 7 - Supplier Analysis

SELECT
    sp.supplier_key,
    sp.supplier_id,
    sp.supplier_name,
    sp.supplier_category,
    sp.country,
    COUNT(DISTINCT p.product_key) AS products_supplied,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS associated_sales_revenue
FROM dim_supplier sp
JOIN dim_product p
    ON sp.supplier_key = p.supplier_key
LEFT JOIN fact_sales s
    ON p.product_key = s.product_key
GROUP BY
    sp.supplier_key,
    sp.supplier_id,
    sp.supplier_name,
    sp.supplier_category,
    sp.country
ORDER BY associated_sales_revenue DESC;


-- Supplier performance by category
SELECT
    sp.supplier_category,
    COUNT(DISTINCT sp.supplier_key) AS suppliers,
    COUNT(DISTINCT p.product_key) AS products,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS associated_sales_revenue
FROM dim_supplier sp
JOIN dim_product p
    ON sp.supplier_key = p.supplier_key
LEFT JOIN fact_sales s
    ON p.product_key = s.product_key
GROUP BY sp.supplier_category
ORDER BY associated_sales_revenue DESC;