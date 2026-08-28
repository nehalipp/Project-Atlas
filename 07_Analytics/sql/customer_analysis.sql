-- Project Atlas
-- Phase 7 - Customer Analysis
--
-- Customer performance analysis.
-- Quantity metrics are analyzed by unit_of_measure.

-- ============================================================
-- CUSTOMER PERFORMANCE
-- ============================================================

SELECT
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    a.account_name,
    s.unit_of_measure,
    COUNT(*) AS transactions,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue,
    AVG(s.revenue) AS average_transaction_revenue
FROM fact_sales s
JOIN dim_customer c
    ON s.customer_key = c.customer_key
JOIN dim_account a
    ON c.account_key = a.account_key
GROUP BY
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    a.account_name,
    s.unit_of_measure
ORDER BY
    revenue DESC;


-- ============================================================
-- CUSTOMER SEGMENT PERFORMANCE
-- ============================================================

SELECT
    c.customer_segment,
    s.unit_of_measure,
    COUNT(DISTINCT c.customer_key) AS customers,
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
-- ACCOUNT PERFORMANCE
-- ============================================================

SELECT
    a.account_key,
    a.account_id,
    a.account_name,
    a.account_type,
    s.unit_of_measure,
    COUNT(DISTINCT c.customer_key) AS customers,
    COUNT(s.sales_key) AS transactions,
    SUM(s.quantity) AS quantity_sold,
    SUM(s.revenue) AS revenue
FROM dim_account a
LEFT JOIN dim_customer c
    ON a.account_key = c.account_key
LEFT JOIN fact_sales s
    ON c.customer_key = s.customer_key
GROUP BY
    a.account_key,
    a.account_id,
    a.account_name,
    a.account_type,
    s.unit_of_measure
ORDER BY
    revenue DESC;
