SELECT 'customers' AS tabela, COUNT(*) FROM oltp.customers
UNION ALL SELECT 'products', COUNT(*) FROM oltp.products
UNION ALL SELECT 'stores', COUNT(*) FROM oltp.stores
UNION ALL SELECT 'orders', COUNT(*) FROM oltp.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM oltp.order_items
UNION ALL SELECT 'payments', COUNT(*) FROM oltp.payments
UNION ALL SELECT 'inventory_snapshots', COUNT(*) FROM oltp.inventory_snapshots
UNION ALL SELECT 'pipeline_runs', COUNT(*) FROM audit.pipeline_runs ORDER BY 1;
SELECT status, COUNT(*) AS pedidos FROM oltp.orders GROUP BY status ORDER BY status;
SELECT COUNT(*) AS vendas_confirmadas, SUM(total_amount) AS valor_confirmado FROM analytics.vw_valid_orders;
SELECT * FROM analytics.vw_daily_kpis ORDER BY sale_date DESC,channel LIMIT 10;
