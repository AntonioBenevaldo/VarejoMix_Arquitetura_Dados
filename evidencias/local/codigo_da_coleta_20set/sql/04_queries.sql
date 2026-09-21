SET TIME ZONE 'UTC';

-- 1) Receita, margem e ticket por mês e canal usando CTE.
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', sale_date)::date AS month,
        channel,
        COUNT(DISTINCT order_id) AS orders,
        SUM(net_revenue) AS revenue,
        SUM(gross_margin) AS margin
    FROM analytics.vw_sales_line
    GROUP BY 1, 2
)
SELECT
    month,
    channel,
    orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(margin, 2) AS margin,
    ROUND(revenue / NULLIF(orders, 0), 2) AS average_ticket
FROM monthly
ORDER BY month, channel;

-- 2) Receita mensal, mês anterior e média móvel de três meses com janelas.
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', sale_date)::date AS month,
        SUM(net_revenue) AS revenue
    FROM analytics.vw_sales_line
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS previous_month_revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_average_3m
FROM monthly
ORDER BY month;

-- 3) Cohorts: retenção mensal a partir da primeira compra válida.
WITH valid_orders AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', order_ts)::date AS activity_month
    FROM analytics.vw_valid_orders
), first_purchase AS (
    SELECT customer_id, MIN(activity_month) AS cohort_month
    FROM valid_orders
    GROUP BY customer_id
), cohort_activity AS (
    SELECT
        v.customer_id,
        f.cohort_month,
        v.activity_month,
        (EXTRACT(YEAR FROM AGE(v.activity_month, f.cohort_month)) * 12
         + EXTRACT(MONTH FROM AGE(v.activity_month, f.cohort_month)))::int AS month_number
    FROM valid_orders v
    JOIN first_purchase f USING (customer_id)
), cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    a.cohort_month,
    a.month_number,
    COUNT(DISTINCT a.customer_id) AS retained_customers,
    s.customers AS cohort_customers,
    ROUND(COUNT(DISTINCT a.customer_id)::numeric / s.customers, 4) AS retention_rate
FROM cohort_activity a
JOIN cohort_size s USING (cohort_month)
GROUP BY a.cohort_month, a.month_number, s.customers
ORDER BY a.cohort_month, a.month_number;

-- 4) Ruptura por loja e categoria.
SELECT
    snapshot_date,
    store_code,
    category,
    COUNT(*) AS monitored_skus,
    COUNT(*) FILTER (WHERE is_stockout) AS stockout_skus,
    ROUND(COUNT(*) FILTER (WHERE is_stockout)::numeric / COUNT(*), 4) AS stockout_rate
FROM analytics.vw_stockout
GROUP BY snapshot_date, store_code, category
ORDER BY stockout_rate DESC, store_code, category;

