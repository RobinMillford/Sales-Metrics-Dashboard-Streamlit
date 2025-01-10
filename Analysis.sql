use sales;

-- 1. sales data by region for the Midwest
SELECT r.name AS Region,
       sr.name AS Rep_name,
       a.name AS account_name
FROM region r
JOIN sales_reps sr ON r.id = sr.region_id
JOIN accounts a ON sr.id = a.sales_rep_id
WHERE r.name = 'Midwest'
ORDER BY account_name ASC;

-- 2. sales data for Midwest region sales representatives whose names start with 'S'
SELECT r.name AS Region,
       sr.name AS Rep_name,
       a.name AS account_name
FROM region r
JOIN sales_reps sr ON r.id = sr.region_id
JOIN accounts a ON sr.id = a.sales_rep_id
WHERE r.name = 'Midwest'
  AND sr.name LIKE 'S%'
ORDER BY account_name ASC;

-- 3. sales data for Midwest region sales representatives whose names contain 'K'
SELECT r.name AS Region,
       sr.name AS Rep_name,
       a.name AS account_name
FROM region r
JOIN sales_reps sr ON r.id = sr.region_id
JOIN accounts a ON sr.id = a.sales_rep_id
WHERE r.name = 'Midwest'
  AND sr.name LIKE '%K%'
ORDER BY account_name ASC;

-- 4. the unit price for orders with standard quantity greater than 100
SELECT r.name AS region,
       a.name AS account_name,
       o.total_amt_usd / (o.total + 0.01) AS unit_price
FROM region r
JOIN sales_reps sr ON r.id = sr.region_id
JOIN accounts a ON sr.id = a.sales_rep_id
JOIN orders o ON a.id = o.account_id
WHERE o.standard_qty > 100;

-- 5. Unit Price for Orders with Quantity Conditions and Sort by Unit Price (Descending).
SELECT r.name AS region,
       a.name AS account_name,
       o.total_amt_usd / (o.total + 0.01) AS unit_price
FROM region r
JOIN sales_reps sr ON r.id = sr.region_id
JOIN accounts a ON sr.id = a.sales_rep_id
JOIN orders o ON a.id = o.account_id
WHERE o.standard_qty > 100
  AND o.poster_qty > 50
ORDER BY unit_price DESC;

-- 6. Average Order Amounts by Account Name.
SELECT 
    a.name AS account_name,
    AVG(o.standard_amt_usd) AS avg_standard_amt_usd,
    AVG(o.gloss_amt_usd) AS avg_gloss_amt_usd,
    AVG(o.poster_amt_usd) AS avg_poster_amt_usd
FROM
    accounts a
        JOIN
    orders o ON a.id = o.account_id
GROUP BY a.name;

-- 7. Count Web Event Occurrences by Sales Representative and Channel, Sorted by Occurrence Count (Descending)
SELECT sr.name AS sales_rep_name,
       we.channel,
       COUNT(*) AS number_of_occurrences
FROM web_events we
JOIN accounts a ON we.account_id = a.id
JOIN sales_reps sr ON a.sales_rep_id = sr.id
GROUP BY sr.name, we.channel
ORDER BY number_of_occurrences DESC;

-- 8. Total USD Amount of Orders by Year and Sort by Total USD Amount
SELECT EXTRACT(YEAR FROM occurred_at) AS year,
       SUM(total_amt_usd) AS total_usd
FROM orders
GROUP BY EXTRACT(YEAR FROM occurred_at)
ORDER BY total_usd ASC;

-- 9. Total USD Amount of Orders by Year and Month, Filter by Specific Years, and Sort by Year
SELECT EXTRACT(YEAR FROM occurred_at) AS year,
       EXTRACT(MONTH FROM occurred_at) AS month,
       SUM(total_amt_usd) AS total_usd
FROM orders
WHERE EXTRACT(YEAR FROM occurred_at) IN (2013, 2017)
GROUP BY EXTRACT(YEAR FROM occurred_at), EXTRACT(MONTH FROM occurred_at)
ORDER BY year ASC;

-- 10. Total USD Amount of Orders for January 1st and Sort by Total USD Amount.
SELECT EXTRACT(YEAR FROM occurred_at) AS year,
       EXTRACT(MONTH FROM occurred_at) AS month,
       EXTRACT(DAY FROM occurred_at) AS day,
       SUM(total_amt_usd) AS total_usd
FROM orders
WHERE EXTRACT(MONTH FROM occurred_at) = 1
  AND EXTRACT(DAY FROM occurred_at) = 1
GROUP BY EXTRACT(YEAR FROM occurred_at), EXTRACT(MONTH FROM occurred_at), EXTRACT(DAY FROM occurred_at)
ORDER BY total_usd ASC;

-- 11. the Account with the Highest Monthly Gloss Total for Walmart.
SELECT a.name AS account_name,
       EXTRACT(YEAR FROM o.occurred_at) AS year,
       EXTRACT(MONTH FROM o.occurred_at) AS month,
       SUM(o.gloss_amt_usd) AS gloss_total_usd
FROM accounts a
JOIN orders o ON a.id = o.account_id
WHERE a.name = 'Walmart'
GROUP BY a.name, EXTRACT(YEAR FROM o.occurred_at), EXTRACT(MONTH FROM o.occurred_at)
ORDER BY gloss_total_usd DESC
LIMIT 1;

-- 12. Top Performing Regions by Total Sales Amount
SELECT r.name AS region_name,
       SUM(o.total_amt_usd) AS total_sales
FROM orders o
JOIN accounts a ON o.account_id = a.id
JOIN sales_reps sr ON a.sales_rep_id = sr.id
JOIN region r ON sr.region_id = r.id
GROUP BY r.name
ORDER BY total_sales DESC;

-- 13. Customer Lifetime Value (CLV) Analysis
SELECT a.id AS account_id,
       a.name AS account_name,
       SUM(o.total_amt_usd) AS total_spent,
       COUNT(o.id) AS total_orders,
       AVG(o.total_amt_usd) AS average_order_amount
FROM accounts a
LEFT JOIN orders o ON a.id = o.account_id
GROUP BY a.id, a.name
ORDER BY total_spent DESC;

-- 14. Channel Effectiveness Analysis
SELECT we.channel,
       COUNT(we.id) AS total_events,
       COUNT(DISTINCT we.account_id) AS unique_accounts,
       COUNT(DISTINCT a.id) AS total_customers
FROM web_events we
LEFT JOIN accounts a ON we.account_id = a.id
GROUP BY we.channel
ORDER BY total_events DESC;

-- 15. Customer Acquisition Analysis by Sales Representative
SELECT sr.name AS sales_representative,
       COUNT(DISTINCT a.id) AS new_customers_acquired,
       EXTRACT(YEAR FROM MIN(o.occurred_at)) AS first_order_year
FROM sales_reps sr
LEFT JOIN accounts a ON sr.id = a.sales_rep_id
LEFT JOIN orders o ON a.id = o.account_id
GROUP BY sr.name
ORDER BY new_customers_acquired DESC;

-- 16. Customer Churn Analysis
WITH last_order_dates AS (
    SELECT
        account_id,
        MAX(occurred_at) AS last_order_date
    FROM orders
    GROUP BY account_id
)
SELECT
    COUNT(DISTINCT l.account_id) AS active_customers,
    COUNT(DISTINCT a.id) - COUNT(DISTINCT l.account_id) AS churned_customers
FROM accounts a
LEFT JOIN last_order_dates l ON a.id = l.account_id;

-- 17. Seasonal Sales Trends Analysis
SELECT
    EXTRACT(MONTH FROM o.occurred_at) AS month,
    SUM(o.total_amt_usd) AS total_sales
FROM orders o
GROUP BY month
ORDER BY month;

-- 18. Average Order Size Comparison Across Regions
SELECT
    r.name AS region_name,
    AVG(o.total_amt_usd) AS avg_order_size
FROM orders o
JOIN accounts a ON o.account_id = a.id
JOIN sales_reps sr ON a.sales_rep_id = sr.id
JOIN region r ON sr.region_id = r.id
GROUP BY r.name
ORDER BY avg_order_size DESC;


-- 19. Web Event Effectiveness Analysis by Region and Channel
SELECT
    r.name AS region_name,
    we.channel,
    COUNT(we.id) AS total_events,
    COUNT(DISTINCT a.id) AS unique_accounts_impacted
FROM web_events we
LEFT JOIN accounts a ON we.account_id = a.id
LEFT JOIN sales_reps sr ON a.sales_rep_id = sr.id
LEFT JOIN region r ON sr.region_id = r.id
GROUP BY r.name, we.channel
ORDER BY r.name, total_events DESC;

-- 20. Customer Segmentation by Purchase Frequency and Total Spend
WITH customer_summary AS (
    SELECT
        a.id AS account_id,
        a.name AS account_name,
        COUNT(o.id) AS total_orders,
        SUM(o.total_amt_usd) AS total_spend,
        DENSE_RANK() OVER (ORDER BY COUNT(o.id) DESC) AS order_rank,
        DENSE_RANK() OVER (ORDER BY SUM(o.total_amt_usd) DESC) AS spend_rank
    FROM accounts a
    LEFT JOIN orders o ON a.id = o.account_id
    GROUP BY a.id, a.name
)
SELECT
    account_name,
    total_orders,
    total_spend,
    CASE
        WHEN order_rank <= 3 THEN 'Highly Active'
        WHEN order_rank <= 10 THEN 'Moderately Active'
        ELSE 'Less Active'
    END AS order_activity_segment,
    CASE
        WHEN spend_rank <= 3 THEN 'High Spender'
        WHEN spend_rank <= 10 THEN 'Moderate Spender'
        ELSE 'Low Spender'
    END AS spending_segment
FROM customer_summary
ORDER BY order_rank, spend_rank;

-- 21. Customer Retention Rate Analysis
WITH customer_first_order_dates AS (
    SELECT
        account_id,
        MIN(occurred_at) AS first_order_date
    FROM orders
    GROUP BY account_id
),
customer_retention_rates AS (
    SELECT
        EXTRACT(YEAR FROM c.first_order_date) AS first_order_year,
        COUNT(DISTINCT o.account_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN EXTRACT(YEAR FROM o.occurred_at) > EXTRACT(YEAR FROM c.first_order_date) THEN o.account_id END) AS retained_customers,
        COUNT(DISTINCT CASE WHEN EXTRACT(YEAR FROM o.occurred_at) = EXTRACT(YEAR FROM c.first_order_date) THEN o.account_id END) AS new_customers
    FROM customer_first_order_dates c
    LEFT JOIN orders o ON c.account_id = o.account_id
    GROUP BY first_order_year
)
SELECT
    first_order_year,
    total_customers,
    retained_customers,
    new_customers,
    ROUND((retained_customers / total_customers) * 100, 2) AS retention_rate
FROM customer_retention_rates
ORDER BY first_order_year;

-- 22. Analysis of Average Order Size by Customer Segment
WITH order_summary AS (
    SELECT
        a.id AS account_id,
        a.name AS account_name,
        AVG(o.total_amt_usd) AS avg_order_amt_usd,
        STDDEV(o.total_amt_usd) AS order_amt_std_dev,
        COUNT(o.id) AS total_orders
    FROM accounts a
    LEFT JOIN orders o ON a.id = o.account_id
    GROUP BY a.id, a.name
),
segmented_orders AS (
    SELECT
        account_id,
        account_name,
        avg_order_amt_usd,
        order_amt_std_dev,
        total_orders,
        CASE
            WHEN total_orders > 50 THEN 'High Volume'
            WHEN total_orders > 10 THEN 'Moderate Volume'
            ELSE 'Low Volume'
        END AS order_volume_segment
    FROM order_summary
)
SELECT
    order_volume_segment,
    COUNT(account_id) AS num_accounts,
    AVG(avg_order_amt_usd) AS avg_order_size_usd,
    AVG(order_amt_std_dev) AS avg_order_std_dev_usd
FROM segmented_orders
GROUP BY order_volume_segment
ORDER BY num_accounts DESC;

-- 23. Identifying High-Growth Accounts by Order Volume Increase
WITH order_growth_analysis AS (
    SELECT
        account_id,
        MIN(EXTRACT(YEAR FROM occurred_at)) AS first_order_year,
        MAX(EXTRACT(YEAR FROM occurred_at)) AS last_order_year,
        COUNT(DISTINCT id) AS total_orders,
        COUNT(DISTINCT EXTRACT(YEAR FROM occurred_at)) AS order_years_count,
        AVG(total_amt_usd) AS avg_order_amt_usd
    FROM orders
    GROUP BY account_id
),
high_growth_accounts AS (
    SELECT
        account_id,
        first_order_year,
        last_order_year,
        total_orders,
        order_years_count,
        avg_order_amt_usd,
        CASE
            WHEN order_years_count > 1 AND total_orders / order_years_count > 10 THEN 'High Growth'
            ELSE 'Low Growth'
        END AS growth_category
    FROM order_growth_analysis
)
SELECT
    a.name AS account_name,
    hga.first_order_year,
    hga.last_order_year,
    hga.total_orders,
    hga.order_years_count,
    hga.avg_order_amt_usd,
    hga.growth_category
FROM high_growth_accounts hga
JOIN accounts a ON hga.account_id = a.id
WHERE hga.growth_category = 'High Growth'
ORDER BY hga.total_orders DESC;

-- 24. Average Time Between Orders Analysis
WITH order_dates AS (
    SELECT
        account_id,
        occurred_at,
        LAG(occurred_at) OVER (PARTITION BY account_id ORDER BY occurred_at) AS prev_order_date
    FROM orders
),
order_gaps AS (
    SELECT
        account_id,
        occurred_at,
        prev_order_date,
        DATEDIFF(occurred_at, prev_order_date) AS days_between_orders
    FROM order_dates
    WHERE prev_order_date IS NOT NULL
),
avg_time_between_orders AS (
    SELECT
        account_id,
        AVG(days_between_orders) AS avg_days_between_orders
    FROM order_gaps
    GROUP BY account_id
)
SELECT
    a.name AS account_name,
    a.website,
    a.primary_poc AS primary_contact,
    ROUND(ato.avg_days_between_orders, 2) AS avg_days_between_orders
FROM avg_time_between_orders ato
JOIN accounts a ON ato.account_id = a.id
ORDER BY avg_days_between_orders DESC;

-- 25. Sales Contribution Analysis by Sales Representative and Region
WITH sales_contribution AS (
    SELECT
        r.name AS region_name,
        sr.name AS sales_representative,
        COUNT(o.id) AS num_orders,
        SUM(o.total_amt_usd) AS total_amt_usd
    FROM sales_reps sr
    JOIN accounts a ON sr.id = a.sales_rep_id
    JOIN orders o ON a.id = o.account_id
    JOIN region r ON sr.region_id = r.id
    GROUP BY r.name, sr.name
),
region_total_sales AS (
    SELECT
        region_name,
        SUM(total_amt_usd) AS region_total_amt_usd
    FROM sales_contribution
    GROUP BY region_name
)
SELECT
    sc.region_name,
    sc.sales_representative,
    sc.num_orders,
    sc.total_amt_usd,
    rt.region_total_amt_usd,
    ROUND(sc.total_amt_usd / rt.region_total_amt_usd * 100, 2) AS contribution_percent_of_region
FROM sales_contribution sc
JOIN region_total_sales rt ON sc.region_name = rt.region_name
ORDER BY sc.region_name, contribution_percent_of_region DESC;

-- 26. Quarterly Order Quantity Growth Analysis
WITH quarterly_order_quantities AS (
    SELECT
        account_id,
        EXTRACT(YEAR FROM occurred_at) AS order_year,
        EXTRACT(QUARTER FROM occurred_at) AS order_quarter,
        SUM(standard_qty) AS total_standard_qty,
        SUM(gloss_qty) AS total_gloss_qty,
        SUM(poster_qty) AS total_poster_qty
    FROM orders
    GROUP BY account_id, order_year, order_quarter
),
quarterly_growth_analysis AS (
    SELECT
        qo.account_id,
        qo.order_year,
        qo.order_quarter,
        qo.total_standard_qty,
        qo.total_gloss_qty,
        qo.total_poster_qty,
        LAG(qo.total_standard_qty) OVER (PARTITION BY qo.account_id ORDER BY qo.order_year, qo.order_quarter) AS prev_total_standard_qty,
        LAG(qo.total_gloss_qty) OVER (PARTITION BY qo.account_id ORDER BY qo.order_year, qo.order_quarter) AS prev_total_gloss_qty,
        LAG(qo.total_poster_qty) OVER (PARTITION BY qo.account_id ORDER BY qo.order_year, qo.order_quarter) AS prev_total_poster_qty
    FROM quarterly_order_quantities qo
),
quarterly_growth_metrics AS (
    SELECT
        account_id,
        order_year,
        order_quarter,
        total_standard_qty,
        total_gloss_qty,
        total_poster_qty,
        CASE
            WHEN prev_total_standard_qty IS NULL THEN 0
            ELSE total_standard_qty - prev_total_standard_qty
        END AS quarterly_standard_qty_growth,
        CASE
            WHEN prev_total_gloss_qty IS NULL THEN 0
            ELSE total_gloss_qty - prev_total_gloss_qty
        END AS quarterly_gloss_qty_growth,
        CASE
            WHEN prev_total_poster_qty IS NULL THEN 0
            ELSE total_poster_qty - prev_total_poster_qty
        END AS quarterly_poster_qty_growth
    FROM quarterly_growth_analysis
)
SELECT
    a.name AS account_name,
    qgm.order_year,
    qgm.order_quarter,
    qgm.quarterly_standard_qty_growth,
    qgm.quarterly_gloss_qty_growth,
    qgm.quarterly_poster_qty_growth
FROM quarterly_growth_metrics qgm
JOIN accounts a ON qgm.account_id = a.id
ORDER BY qgm.order_year, qgm.order_quarter, a.name;

-- 27. Year-over-Year Order Amount Fluctuation Analysis
WITH yearly_order_amounts AS (
    SELECT
        account_id,
        EXTRACT(YEAR FROM occurred_at) AS order_year,
        SUM(total_amt_usd) AS total_order_amount
    FROM orders
    GROUP BY account_id, order_year
),
yearly_fluctuation_analysis AS (
    SELECT
        ya.account_id,
        ya.order_year,
        ya.total_order_amount,
        LAG(ya.total_order_amount) OVER (PARTITION BY ya.account_id ORDER BY ya.order_year) AS prev_year_order_amount
    FROM yearly_order_amounts ya
),
yearly_fluctuation_metrics AS (
    SELECT
        yfa.account_id,
        yfa.order_year,
        yfa.total_order_amount,
        CASE
            WHEN yfa.prev_year_order_amount IS NULL THEN 0
            ELSE yfa.total_order_amount - yfa.prev_year_order_amount
        END AS year_over_year_order_amount_change
    FROM yearly_fluctuation_analysis yfa
)
SELECT
    a.name AS account_name,
    yfm.order_year,
    yfm.total_order_amount,
    yfm.year_over_year_order_amount_change
FROM yearly_fluctuation_metrics yfm
JOIN accounts a ON yfm.account_id = a.id
ORDER BY yfm.order_year, yfm.year_over_year_order_amount_change DESC;

-- 28. Average Order Amount Analysis and Top Accounts
WITH average_order_amounts AS (
    SELECT
        o.account_id,
        AVG(o.total_amt_usd) AS avg_order_amount
    FROM orders o
    GROUP BY o.account_id
),
top_accounts AS (
    SELECT
        ao.account_id,
        a.name AS account_name,
        ao.avg_order_amount
    FROM average_order_amounts ao
    JOIN accounts a ON ao.account_id = a.id
    WHERE ao.avg_order_amount = (SELECT MAX(avg_order_amount) FROM average_order_amounts)
)
SELECT
    ta.account_name,
    ta.avg_order_amount
FROM top_accounts ta
ORDER BY ta.avg_order_amount DESC;