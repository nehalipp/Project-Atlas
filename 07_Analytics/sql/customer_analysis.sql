-- Project Atlas
-- Phase 7 - Customer Analysis

-- Customer performance
SELECT
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    a.account_name,
    COUNT(*) AS transactions,
    SUM(s.quantity) AS units_sold,
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
    a.account_name
ORDER BY revenue DESC;


-- Customer segment performance
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_key) AS customers,
    COUNT(*) AS transactions,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_customer c
    ON s.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY revenue DESC;


-- Account performance
SELECT
    a.account_key,
    a.account_id,
    a.account_name,
    a.account_type,
    COUNT(DISTINCT c.customer_key) AS customers,
    COUNT(s.sales_key) AS transactions,
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
    a.account_type
ORDER BY revenue DESC;