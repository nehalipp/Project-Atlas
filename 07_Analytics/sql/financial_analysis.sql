-- Project Atlas
-- Phase 7 - Financial Analysis


-- Financial performance by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transactions,
    SUM(transaction_amount) AS total_amount
FROM fact_financial_transaction
GROUP BY transaction_type
ORDER BY total_amount DESC;


-- Financial performance by category
SELECT
    transaction_type,
    transaction_category,
    COUNT(*) AS transactions,
    SUM(transaction_amount) AS total_amount
FROM fact_financial_transaction
GROUP BY
    transaction_type,
    transaction_category
ORDER BY
    transaction_type,
    total_amount DESC;


-- Monthly financial trend
SELECT
    d.year,
    d.month,
    SUM(
        CASE
            WHEN f.transaction_type = 'Revenue'
            THEN f.transaction_amount
            ELSE 0
        END
    ) AS revenue_amount,
    SUM(
        CASE
            WHEN f.transaction_type = 'Expense'
            THEN f.transaction_amount
            ELSE 0
        END
    ) AS expense_amount,
    SUM(
        CASE
            WHEN f.transaction_type = 'Cost'
            THEN f.transaction_amount
            ELSE 0
        END
    ) AS cost_amount
FROM fact_financial_transaction f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- Budget summary
SELECT
    budget_category,
    COUNT(*) AS budget_rows,
    SUM(budget_amount) AS budget_amount
FROM fact_budget
GROUP BY budget_category
ORDER BY budget_amount DESC;