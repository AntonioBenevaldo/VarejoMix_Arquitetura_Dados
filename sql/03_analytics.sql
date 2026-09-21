BEGIN;
SET TIME ZONE 'UTC';

-- Regra unica: pedido confirmado com pagamento aprovado integral.
-- Cancelados/reembolsados e CREATED/PENDING nao sao vendas confirmadas.
CREATE OR REPLACE VIEW analytics.vw_valid_orders AS
SELECT o.*
FROM oltp.orders o
WHERE o.status IN ('PAID', 'SHIPPED', 'DELIVERED')
  AND EXISTS (
      SELECT 1 FROM oltp.payments p
      WHERE p.order_id = o.order_id AND p.payment_status = 'APPROVED'
      GROUP BY p.order_id
      HAVING SUM(p.amount) = o.total_amount
  );

CREATE OR REPLACE VIEW analytics.vw_sales_line AS
SELECT
    i.order_item_id,
    i.line_number,
    o.order_id,
    o.order_ts,
    o.order_ts::date AS sale_date,
    o.customer_id,
    o.store_id,
    o.channel,
    o.status,
    i.product_id,
    p.sku,
    p.category,
    i.quantity,
    i.unit_price,
    i.discount_amount,
    ROUND((i.quantity * i.unit_price)::numeric, 2) AS gross_revenue,
    ROUND((i.quantity * i.unit_price - i.discount_amount)::numeric, 2) AS net_revenue,
    ROUND((i.quantity * i.unit_cost_at_sale)::numeric, 2) AS product_cost,
    ROUND((i.quantity * i.unit_price - i.discount_amount - i.quantity * i.unit_cost_at_sale)::numeric, 2) AS gross_margin
FROM analytics.vw_valid_orders o
JOIN oltp.order_items i ON i.order_id = o.order_id
JOIN oltp.products p ON p.product_id = i.product_id;

CREATE OR REPLACE VIEW analytics.vw_daily_kpis AS
SELECT
    sale_date,
    channel,
    COUNT(DISTINCT order_id) AS valid_orders,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(
        SUM(gross_margin)
        / NULLIF(SUM(net_revenue), 0),
        4
    ) AS margin_rate,
    ROUND(
        SUM(net_revenue)
        / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_ticket
FROM analytics.vw_sales_line
GROUP BY sale_date, channel;

CREATE OR REPLACE VIEW analytics.vw_stockout AS
SELECT
    s.snapshot_date,
    st.store_code,
    p.sku,
    p.product_name,
    p.category,
    s.on_hand_quantity,
    s.reserved_quantity,
    GREATEST(s.on_hand_quantity - s.reserved_quantity, 0) AS available_quantity,
    (s.on_hand_quantity - s.reserved_quantity <= 0) AS is_stockout
FROM oltp.inventory_snapshots s
JOIN oltp.stores st ON st.store_id = s.store_id
JOIN oltp.products p ON p.product_id = s.product_id;

CREATE OR REPLACE VIEW analytics.vw_customer_value AS
SELECT
    c.customer_id,
    c.customer_code,
    MAX(o.order_ts)::date AS last_order_date,
    COUNT(o.order_id) AS valid_orders,
    ROUND(SUM(o.total_amount), 2) AS lifetime_value,
    ROUND(AVG(o.total_amount), 2) AS average_ticket,
    ROUND(AVG((o.channel = 'ECOMMERCE')::int), 4) AS ecommerce_share
FROM oltp.customers c
LEFT JOIN analytics.vw_valid_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_code;

COMMIT;

