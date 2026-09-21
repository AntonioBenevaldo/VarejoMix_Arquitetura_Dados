SET TIME ZONE 'UTC';

-- Consulta seletiva (pedidos entregues em uma janela de 14 dias) usada para
-- comparar os planos de execucao antes e depois do indice composto.
-- Os tempos variam por hardware; a evidência principal é o tipo de acesso.

DROP INDEX IF EXISTS oltp.idx_orders_order_date_status;
ANALYZE oltp.orders;

SELECT 'PLANO A - SEM INDICE ESPECIFICO' AS etapa;
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT order_id, customer_id, order_ts, status, total_amount
FROM oltp.orders
WHERE order_ts >= TIMESTAMPTZ '2025-12-01 00:00:00+00'
  AND order_ts <  TIMESTAMPTZ '2025-12-15 00:00:00+00'
  AND status = 'DELIVERED';

CREATE INDEX idx_orders_order_date_status
    ON oltp.orders (order_ts, status)
    INCLUDE (customer_id, total_amount);
ANALYZE oltp.orders;

SELECT 'PLANO B - COM INDICE ESPECIFICO' AS etapa;
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT order_id, customer_id, order_ts, status, total_amount
FROM oltp.orders
WHERE order_ts >= TIMESTAMPTZ '2025-12-01 00:00:00+00'
  AND order_ts <  TIMESTAMPTZ '2025-12-15 00:00:00+00'
  AND status = 'DELIVERED';

SELECT 'INDICE CRIADO' AS etapa;
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'oltp'
  AND indexname = 'idx_orders_order_date_status';

