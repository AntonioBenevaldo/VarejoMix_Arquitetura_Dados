-- Consulta parametrizada para SQLAlchemy/pandas: parametro :cutoff (UTC).
-- Regra de venda confirmada centralizada em analytics.vw_valid_orders.
WITH eligible_orders AS (
    SELECT order_id, customer_id, order_ts, channel, total_amount
    FROM analytics.vw_valid_orders
    WHERE order_ts >= CAST(:cutoff AS timestamptz) - INTERVAL '365 days'
      AND order_ts < CAST(:cutoff AS timestamptz)
), order_features AS (
    SELECT customer_id,
        ((CAST(:cutoff AS timestamptz) AT TIME ZONE 'UTC')::date - MAX(order_ts AT TIME ZONE 'UTC')::date)::int AS recency_days,
        COUNT(*)::int AS frequency_365d,
        ROUND(SUM(total_amount),2) AS monetary_365d,
        ROUND(AVG(total_amount),2) AS average_ticket,
        ROUND(AVG((channel='ECOMMERCE')::int),4) AS ecommerce_share
    FROM eligible_orders GROUP BY customer_id
), category_features AS (
    SELECT o.customer_id,COUNT(DISTINCT p.category)::int AS distinct_categories
    FROM eligible_orders o
    JOIN oltp.order_items i USING(order_id)
    JOIN oltp.products p USING(product_id)
    GROUP BY o.customer_id
), future_purchase AS (
    SELECT customer_id,1::int AS repurchase_90d
    FROM analytics.vw_valid_orders
    WHERE order_ts >= CAST(:cutoff AS timestamptz)
      AND order_ts < CAST(:cutoff AS timestamptz) + INTERVAL '90 days'
    GROUP BY customer_id
)
SELECT o.*,c.distinct_categories,COALESCE(f.repurchase_90d,0) AS repurchase_90d
FROM order_features o
JOIN category_features c USING(customer_id)
LEFT JOIN future_purchase f USING(customer_id)
ORDER BY o.customer_id;
