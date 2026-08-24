-- Project Atlas
-- Phase 7 - Sales Analysis

-- Revenue and sales performance by day
SELECT
    d.full_date,
    SUM(s.quantity) AS units_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue,
    SUM(s.discount_amount) AS discount_amount
FROM fact_sales s
JOIN dim_date d
    ON s.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;


-- Revenue by product category
SELECT
    p.category,
    SUM(s.quantity) AS units_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue,
    SUM(s.discount_amount) AS discount_amount
FROM fact_sales s
JOIN dim_product p
    ON s.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;


-- Revenue by location
SELECT
    l.location_name,
    SUM(s.quantity) AS units_sold,
    COUNT(*) AS transactions,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_location l
    ON s.location_key = l.location_key
GROUP BY l.location_name
ORDER BY revenue DESC;


-- Revenue by customer segment
SELECT
    c.customer_segment,
    COUNT(*) AS transactions,
    SUM(s.quantity) AS units_sold,
    SUM(s.revenue) AS revenue
FROM fact_sales s
JOIN dim_customer c
    ON s.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY revenue DESC;