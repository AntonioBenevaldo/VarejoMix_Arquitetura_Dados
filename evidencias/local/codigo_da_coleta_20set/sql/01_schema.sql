BEGIN;
SET TIME ZONE 'UTC';

CREATE SCHEMA IF NOT EXISTS oltp;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE oltp.customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    state_code CHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_customers_state CHECK (state_code ~ '^[A-Z]{2}$')
);

CREATE TABLE oltp.stores (
    store_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_code VARCHAR(12) NOT NULL UNIQUE,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_code CHAR(2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE oltp.products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR(24) NOT NULL UNIQUE,
    product_name VARCHAR(140) NOT NULL,
    category VARCHAR(60) NOT NULL,
    unit_cost NUMERIC(12,2) NOT NULL,
    list_price NUMERIC(12,2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_products_cost CHECK (unit_cost >= 0),
    CONSTRAINT ck_products_price CHECK (list_price >= unit_cost)
);

CREATE TABLE oltp.orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES oltp.customers(customer_id),
    store_id SMALLINT REFERENCES oltp.stores(store_id),
    channel VARCHAR(12) NOT NULL,
    order_ts TIMESTAMPTZ NOT NULL,
    status VARCHAR(16) NOT NULL,
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_orders_channel CHECK (channel IN ('ECOMMERCE', 'STORE')),
    CONSTRAINT ck_orders_status CHECK (status IN ('CREATED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED')),
    CONSTRAINT ck_orders_store_channel CHECK (
        (channel = 'STORE' AND store_id IS NOT NULL)
        OR (channel = 'ECOMMERCE' AND store_id IS NULL)
    ),
    CONSTRAINT ck_orders_total CHECK (total_amount >= 0)
);

CREATE TABLE oltp.order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES oltp.orders(order_id) ON DELETE CASCADE,
    line_number SMALLINT NOT NULL,
    product_id BIGINT NOT NULL REFERENCES oltp.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    unit_cost_at_sale NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT uq_order_line UNIQUE (order_id, line_number),
    CONSTRAINT ck_order_items_quantity CHECK (quantity > 0),
    CONSTRAINT ck_order_items_price CHECK (unit_price >= 0),
    CONSTRAINT ck_order_items_cost CHECK (unit_cost_at_sale >= 0),
    CONSTRAINT ck_order_items_discount CHECK (
        discount_amount >= 0 AND discount_amount <= unit_price * quantity
    )
);

CREATE TABLE oltp.payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES oltp.orders(order_id),
    payment_method VARCHAR(20) NOT NULL,
    payment_status VARCHAR(16) NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    paid_at TIMESTAMPTZ,
    transaction_reference VARCHAR(40) NOT NULL UNIQUE,
    CONSTRAINT ck_payments_method CHECK (payment_method IN ('PIX', 'CREDIT_CARD', 'DEBIT_CARD', 'CASH')),
    CONSTRAINT ck_payments_status CHECK (payment_status IN ('PENDING', 'APPROVED', 'REFUNDED', 'DECLINED')),
    CONSTRAINT ck_payments_amount CHECK (amount >= 0),
    CONSTRAINT ck_payments_timestamp CHECK (
        (payment_status IN ('APPROVED', 'REFUNDED') AND paid_at IS NOT NULL)
        OR (payment_status IN ('PENDING', 'DECLINED') AND paid_at IS NULL)
    )
);

CREATE TABLE oltp.inventory_snapshots (
    snapshot_date DATE NOT NULL,
    store_id SMALLINT NOT NULL REFERENCES oltp.stores(store_id),
    product_id BIGINT NOT NULL REFERENCES oltp.products(product_id),
    on_hand_quantity INTEGER NOT NULL,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (snapshot_date, store_id, product_id),
    CONSTRAINT ck_inventory_on_hand CHECK (on_hand_quantity >= 0),
    CONSTRAINT ck_inventory_reserved CHECK (reserved_quantity >= 0 AND reserved_quantity <= on_hand_quantity)
);

CREATE TABLE audit.pipeline_runs (
    run_id UUID PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status VARCHAR(16) NOT NULL,
    source_period_start TIMESTAMPTZ,
    source_period_end TIMESTAMPTZ,
    input_rows BIGINT,
    output_rows BIGINT,
    code_version VARCHAR(40),
    dataset_version VARCHAR(80),
    error_message TEXT,
    CONSTRAINT ck_pipeline_status CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED', 'REPROCESSED'))
);

CREATE INDEX idx_orders_customer_ts ON oltp.orders (customer_id, order_ts DESC);
CREATE INDEX idx_order_items_order ON oltp.order_items (order_id);
CREATE INDEX idx_order_items_product ON oltp.order_items (product_id);
CREATE INDEX idx_payments_order ON oltp.payments (order_id);

COMMIT;

