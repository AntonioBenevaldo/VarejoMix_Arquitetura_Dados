SET TIME ZONE 'UTC';
CREATE OR REPLACE TEMP VIEW resultados_validacao AS
SELECT 'pedidos_antes_do_cadastro' AS teste, COUNT(*)::bigint AS erros
FROM oltp.orders o JOIN oltp.customers c USING(customer_id)
WHERE o.order_ts < c.created_at
UNION ALL
SELECT 'total_pedido_diferente_dos_itens', COUNT(*)
FROM oltp.orders o LEFT JOIN (
 SELECT order_id, SUM(quantity*unit_price-discount_amount) AS valor
 FROM oltp.order_items GROUP BY order_id
) i USING(order_id) WHERE i.valor IS NULL OR i.valor <> o.total_amount
UNION ALL
SELECT 'pagamento_incompativel_com_pedido', COUNT(*)
FROM oltp.orders o LEFT JOIN oltp.payments p USING(order_id)
WHERE p.payment_id IS NULL OR p.amount <> o.total_amount
 OR (o.status IN ('PAID','SHIPPED','DELIVERED') AND p.payment_status <> 'APPROVED')
 OR (o.status = 'CREATED' AND p.payment_status <> 'PENDING')
 OR (o.status = 'CANCELLED' AND p.payment_status NOT IN ('REFUNDED','DECLINED'))
UNION ALL
SELECT 'reserva_acima_do_estoque', COUNT(*) FROM oltp.inventory_snapshots
WHERE reserved_quantity > on_hand_quantity
UNION ALL
SELECT 'duplicidade_do_grao_analitico', COUNT(*) FROM (
 SELECT order_item_id FROM analytics.vw_sales_line GROUP BY order_item_id HAVING COUNT(*) <> 1
) q
UNION ALL
SELECT 'receita_analitica_nao_reconciliada',
 CASE WHEN (SELECT SUM(net_revenue) FROM analytics.vw_sales_line) =
           (SELECT SUM(total_amount) FROM analytics.vw_valid_orders) THEN 0 ELSE 1 END
UNION ALL
SELECT 'ultima_compra_incorreta', COUNT(*) FROM analytics.vw_customer_value v
WHERE v.last_order_date IS DISTINCT FROM (
 SELECT MAX(order_ts)::date FROM analytics.vw_valid_orders o WHERE o.customer_id=v.customer_id
);
SELECT * FROM resultados_validacao ORDER BY teste;
DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM resultados_validacao WHERE erros <> 0) THEN
  RAISE EXCEPTION 'Falha de integridade: consulte os resultados acima.';
 END IF;
END $$;

-- Regressao: atualizar o custo do cadastro nao muda a margem historica.
BEGIN;
CREATE TEMP TABLE margem_antes AS SELECT SUM(gross_margin) AS valor FROM analytics.vw_sales_line;
UPDATE oltp.products SET unit_cost = unit_cost * 0.9;
DO $$ BEGIN
 IF (SELECT valor FROM margem_antes) <> (SELECT SUM(gross_margin) FROM analytics.vw_sales_line) THEN
  RAISE EXCEPTION 'A margem historica mudou com o cadastro do produto.';
 END IF;
END $$;
ROLLBACK;
SELECT 'APROVADO: integridade e custo historico' AS resultado;
