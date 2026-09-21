-- =====================================================================
-- Carga sintética determinística da VarejoMix.
-- Objetivo: gerar dados com VARIÂNCIA realista para que as análises
-- (cohorts, ruptura, recompra, mix de canal) tenham significado.
--
-- Determinismo: nenhuma chamada a random(). Todos os sorteios usam
-- oltp.rnd(seed), um gerador pseudoaleatório baseado em MD5. A mesma
-- execução produz sempre exatamente a mesma base.
-- =====================================================================

BEGIN;
SET TIME ZONE 'UTC';

CREATE OR REPLACE FUNCTION oltp.rnd(seed TEXT)
RETURNS DOUBLE PRECISION
LANGUAGE SQL IMMUTABLE STRICT AS $$
    SELECT (('x' || SUBSTR(MD5(seed), 1, 7))::BIT(28)::INT)::DOUBLE PRECISION / 268435456.0;
$$;

-- ---------------------------------------------------------------------
-- 1) Lojas físicas
-- ---------------------------------------------------------------------
INSERT INTO oltp.stores (store_code, store_name, city, state_code) VALUES
('LOJA-SP-01', 'VarejoMix Paulista',    'São Paulo',      'SP'),
('LOJA-SP-02', 'VarejoMix Campinas',    'Campinas',       'SP'),
('LOJA-RJ-01', 'VarejoMix Centro Rio',  'Rio de Janeiro', 'RJ'),
('LOJA-MG-01', 'VarejoMix Savassi',     'Belo Horizonte', 'MG'),
('LOJA-PR-01', 'VarejoMix Batel',       'Curitiba',       'PR');

-- ---------------------------------------------------------------------
-- 2) Clientes (200), com datas de cadastro espalhadas ao longo de cerca de 15 meses.
--    A data de cadastro condiciona o mês da primeira compra -> cohorts reais.
-- ---------------------------------------------------------------------
INSERT INTO oltp.customers (customer_code, full_name, email, state_code, created_at)
SELECT
    'CLI-' || LPAD(n::text, 4, '0'),
    'Cliente Sintético ' || LPAD(n::text, 3, '0'),
    'cliente' || LPAD(n::text, 3, '0') || '@example.invalid',
    (ARRAY['SP','RJ','MG','PR','BA','RS','SC','PE'])[1 + FLOOR(8 * oltp.rnd('uf' || n))::int],
    TIMESTAMPTZ '2024-10-01 09:00:00+00'
        + (FLOOR(440 * oltp.rnd('cad' || n))::int) * INTERVAL '1 day'
        + (FLOOR(10 * oltp.rnd('cadh' || n))::int) * INTERVAL '1 hour'
FROM generate_series(1, 200) AS g(n);

-- ---------------------------------------------------------------------
-- 3) Produtos (40) em 5 categorias
-- ---------------------------------------------------------------------
INSERT INTO oltp.products (sku, product_name, category, unit_cost, list_price)
SELECT
    'SKU-' || LPAD(n::text, 4, '0'),
    'Produto Sintético ' || LPAD(n::text, 3, '0'),
    (ARRAY['ELETRÔNICOS','CASA','MODA','BELEZA','ESPORTE'])[((n - 1) % 5) + 1],
    (20 + (n * 3.25))::NUMERIC(12,2),
    (35 + (n * 5.40))::NUMERIC(12,2)
FROM generate_series(1, 40) AS g(n);

-- ---------------------------------------------------------------------
-- 4) Pedidos (5.000)
--    - frequência assimétrica: poucos clientes compram muito (expoente 2.2)
--    - primeira compra >= cadastro do cliente
--    - ~30% dos clientes deixam de comprar (churn) antes do fim do período
--    - propensão de canal por cliente -> existem clientes 100% digitais,
--      100% loja e, principalmente, clientes omnichannel
--    - status depende da idade do pedido (pedidos recentes ainda em rota)
-- ---------------------------------------------------------------------
INSERT INTO oltp.orders (customer_id, store_id, channel, order_ts, status)
SELECT
    b.customer_id,
    CASE WHEN b.channel = 'STORE'
         THEN 1 + FLOOR(5 * oltp.rnd('loja' || b.n))::int
         ELSE NULL END,
    b.channel,
    b.order_ts,
    CASE
        WHEN oltp.rnd('st' || b.n) < 0.045                       THEN 'CANCELLED'
        WHEN b.days_old < 2                                      THEN 'CREATED'
        WHEN b.days_old < 6                                      THEN 'PAID'
        WHEN b.days_old < 14 OR oltp.rnd('sh' || b.n) < 0.05     THEN 'SHIPPED'
        ELSE 'DELIVERED'
    END
FROM (
    SELECT
        a.n,
        a.customer_id,
        a.order_ts,
        (DATE '2025-12-31' - a.order_ts::date) AS days_old,
        CASE WHEN oltp.rnd('ch' || a.n) < a.p_ecommerce THEN 'ECOMMERCE' ELSE 'STORE' END AS channel
    FROM (
        SELECT
            r.n,
            c.customer_id,
            oltp.rnd('pe' || c.customer_id) AS p_ecommerce,
            -- janela ativa do cliente: do cadastro até o fim do período
            -- (ou até a data de churn, quando aplicável)
            GREATEST(c.created_at, TIMESTAMPTZ '2024-12-01 00:00:00+00')
                + (
                    oltp.rnd('t' || r.n) * EXTRACT(EPOCH FROM (
                        GREATEST(
                          GREATEST(c.created_at, TIMESTAMPTZ '2024-12-01 00:00:00+00') + INTERVAL '1 day',
                          CASE
                            WHEN oltp.rnd('churn' || c.customer_id) < 0.30
                            THEN TIMESTAMPTZ '2025-08-01 00:00:00+00'
                                 + (FLOOR(75 * oltp.rnd('cd' || c.customer_id))::int) * INTERVAL '1 day'
                            ELSE TIMESTAMPTZ '2025-12-31 20:00:00+00'
                          END
                        )
                        - GREATEST(c.created_at, TIMESTAMPTZ '2024-12-01 00:00:00+00')
                    ))
                  ) * INTERVAL '1 second' AS order_ts
        FROM generate_series(1, 5000) AS r(n)
        JOIN oltp.customers c
          ON c.customer_id = 1 + FLOOR(200 * POWER(oltp.rnd('cli' || r.n), 2.2))::int
    ) a
) b;

-- ---------------------------------------------------------------------
-- 5) Itens do pedido: 1 a 3 linhas por pedido, produtos sorteados,
--    preço praticado com variação e desconto em parte das linhas.
-- ---------------------------------------------------------------------
INSERT INTO oltp.order_items
    (order_id, line_number, product_id, quantity, unit_price, unit_cost_at_sale, discount_amount)
SELECT
    o.order_id,
    l.line_number,
    p.product_id,
    q.quantity,
    q.unit_price,
    p.unit_cost,
    CASE
        WHEN oltp.rnd('dsc' || o.order_id || '-' || l.line_number) < 0.30
        THEN ROUND((q.unit_price * q.quantity
                   * (0.05 + 0.10 * oltp.rnd('dv' || o.order_id || '-' || l.line_number)))::numeric, 2)
        ELSE 0
    END
FROM oltp.orders o
CROSS JOIN LATERAL generate_series(
    1,
    1 + FLOOR(3 * oltp.rnd('nl' || o.order_id))::int
) AS l(line_number)
JOIN oltp.products p
  ON p.product_id = 1 + FLOOR(40 * oltp.rnd('prd' || o.order_id || '-' || l.line_number))::int
CROSS JOIN LATERAL (
    SELECT
        1 + FLOOR(3 * oltp.rnd('qtd' || o.order_id || '-' || l.line_number))::int AS quantity,
        ROUND((p.list_price * (0.92 + 0.16 * oltp.rnd('pr' || o.order_id || '-' || l.line_number)))::numeric, 2) AS unit_price
) q;

-- ---------------------------------------------------------------------
-- 6) Reconciliação do total do pedido com as linhas
-- ---------------------------------------------------------------------
UPDATE oltp.orders o
SET total_amount = totals.net_total,
    updated_at = o.order_ts + INTERVAL '30 minutes'
FROM (
    SELECT order_id,
           ROUND(SUM(quantity * unit_price - discount_amount), 2) AS net_total
    FROM oltp.order_items
    GROUP BY order_id
) totals
WHERE totals.order_id = o.order_id;

-- ---------------------------------------------------------------------
-- 7) Pagamentos (um por pedido), com status coerente com o pedido
-- ---------------------------------------------------------------------
INSERT INTO oltp.payments
    (order_id, payment_method, payment_status, amount, paid_at, transaction_reference)
SELECT
    order_id,
    (ARRAY['PIX','CREDIT_CARD','DEBIT_CARD','CASH'])[1 + FLOOR(4 * oltp.rnd('pay' || order_id))::int],
    CASE
        WHEN status = 'CANCELLED' THEN 'REFUNDED'
        WHEN status = 'CREATED'   THEN 'PENDING'
        ELSE 'APPROVED'
    END,
    total_amount,
    CASE WHEN status = 'CREATED' THEN NULL
         ELSE order_ts + INTERVAL '5 minutes' END,
    'TX-' || LPAD(order_id::text, 8, '0')
FROM oltp.orders;

-- ---------------------------------------------------------------------
-- 8) Estoque: snapshot diário de 14 dias x 5 lojas x 40 produtos.
--    O saldo cai ao longo da série e há reposição em alguns SKUs,
--    de forma que a ruptura varia por dia, loja e categoria.
-- ---------------------------------------------------------------------
INSERT INTO oltp.inventory_snapshots
    (snapshot_date, store_id, product_id, on_hand_quantity, reserved_quantity)
SELECT
    d.snapshot_date::date,
    s.store_id,
    p.product_id,
    GREATEST(
        0,
        (FLOOR(45 * oltp.rnd('inv' || s.store_id || '-' || p.product_id))::int
         - (d.snapshot_date::date - DATE '2025-12-18') * 3
         + CASE WHEN oltp.rnd('rep' || s.store_id || '-' || p.product_id || '-' || d.snapshot_date::date) < 0.10
                THEN 40 ELSE 0 END)
    ),
    0
FROM generate_series(DATE '2025-12-18', DATE '2025-12-31', INTERVAL '1 day') AS d(snapshot_date)
CROSS JOIN oltp.stores s
CROSS JOIN oltp.products p;

-- Reservas nao podem superar o estoque fisico no recorte sem backorders.
UPDATE oltp.inventory_snapshots
SET reserved_quantity = LEAST(on_hand_quantity, FLOOR(6 * oltp.rnd('res' || store_id || '-' || product_id || '-' || snapshot_date))::int);

-- audit.pipeline_runs comeca vazia. O pipeline Python registra execucoes reais.
DROP FUNCTION oltp.rnd(TEXT);
ANALYZE;
COMMIT;
