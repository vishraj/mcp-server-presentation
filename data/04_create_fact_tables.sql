-- Fact Sales
CREATE TABLE fact_sales (
    sales_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES dim_customer(customer_id),
    product_id INT REFERENCES dim_product(product_id),
    store_id INT REFERENCES dim_store(store_id),
    date_id INT REFERENCES dim_date(date_id),
    quantity INT NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL
);

-- fact_orders table
CREATE TABLE fact_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES dim_customer(customer_id),
    store_id INT REFERENCES dim_store(store_id),
    order_date_id INT REFERENCES dim_date(date_id),
    total_amount NUMERIC(12,2),
    total_items INT,
    order_status VARCHAR(20) -- e.g. 'Pending', 'Shipped', 'Completed'
);

-- fact_order_items table
-- This table captures the details of each item in an order
CREATE TABLE fact_order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES fact_orders(order_id),
    product_id INT REFERENCES dim_product(product_id),
    quantity INT NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    total_price NUMERIC(12,2) NOT NULL
);
