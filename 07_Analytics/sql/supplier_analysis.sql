-- Project Atlas
-- Phase 7 - Supplier Analysis
--
-- Supplier performance is interpreted through sales
-- associated with products supplied by each supplier.
-- Quantity metrics are reported by unit_of_measure.

-- ============================================================
-- SUPPLIER PERFORMANCE
-- ============================================================

SELECT
    sp.supplier_key,
    sp.supplier_id,
    sp.supplier_name,
    sp.supplier_category,
    sp.country,
    p.unit_of_measure,
    COUNT(DISTINCT p.product_key) AS products_supplied,
    SUM(s.quantity) AS quantity_sold,
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
    sp.country,
    p.unit_of_measure
ORDER BY
    associated_sales_revenue DESC;


-- ============================================================
-- SUPPLIER PERFORMANCE BY CATEGORY
-- ============================================================

SELECT
    sp.supplier_category,
    p.unit_of_measure,
    COUNT(DISTINCT sp.supplier_key) AS suppliers,
    COUNT(DISTINCT p.product_key) AS products,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS associated_sales_revenue
FROM dim_supplier sp
JOIN dim_product p
    ON sp.supplier_key = p.supplier_key
LEFT JOIN fact_sales s
    ON p.product_key = s.product_key
GROUP BY
    sp.supplier_category,
    p.unit_of_measure
ORDER BY
    associated_sales_revenue DESC;
