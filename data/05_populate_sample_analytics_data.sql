-- dim_customer table
INSERT INTO dim_customer (first_name, last_name, email, city, state, country, created_at) VALUES
('Alice', 'Johnson', 'alice.johnson@example.com', 'San Francisco', 'CA', 'USA', '2023-01-15'),
('Bob', 'Smith', 'bob.smith@example.com', 'New York', 'NY', 'USA', '2023-02-20'),
('Charlie', 'Davis', 'charlie.davis@example.com', 'Chicago', 'IL', 'USA', '2023-03-10'),
('Diana', 'Lopez', 'diana.lopez@example.com', 'Miami', 'FL', 'USA', '2023-04-05');

-- dim_product table
INSERT INTO dim_product (product_name, category, brand, price) VALUES
('iPhone 15', 'Electronics', 'Apple', 999.00),
('Galaxy S24', 'Electronics', 'Samsung', 899.00),
('AirPods Pro', 'Accessories', 'Apple', 249.00),
('Nike Running Shoes', 'Footwear', 'Nike', 120.00),
('Adidas Hoodie', 'Apparel', 'Adidas', 80.00);

-- dim_store table
INSERT INTO dim_store (store_name, city, state, country) VALUES
('Downtown Store', 'San Francisco', 'CA', 'USA'),
('Mall Outlet', 'Chicago', 'IL', 'USA'),
('Online Store', 'Seattle', 'WA', 'USA');

-- dim_date table
-- Populate dim_date from 2020-01-01 to 2030-12-31
INSERT INTO dim_date (full_date, day, month, quarter, year)
SELECT 
    d::date AS full_date,
    EXTRACT(DAY FROM d)::int AS day,
    EXTRACT(MONTH FROM d)::int AS month,
    EXTRACT(QUARTER FROM d)::int AS quarter,
    EXTRACT(YEAR FROM d)::int AS year
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day') d;

-- fact_sales table
INSERT INTO fact_sales (customer_id, product_id, store_id, date_id, quantity, total_amount) VALUES
(1, 1, 3, 1, 1, 999.00),   -- Alice buys an iPhone online
(2, 2, 1, 2, 1, 899.00),   -- Bob buys a Galaxy at SF store
(3, 3, 3, 3, 2, 498.00),   -- Charlie buys 2 AirPods online
(4, 4, 2, 4, 1, 120.00),   -- Diana buys Nike shoes at Chicago outlet
(1, 5, 3, 5, 3, 240.00);   -- Alice buys 3 Adidas hoodies online

-- insert orders
INSERT INTO fact_orders (customer_id, store_id, order_date_id, total_amount, total_items, order_status) VALUES
(1, 3, 1, 1239.00, 2, 'Completed'),  -- Alice’s order
(2, 1, 2, 899.00, 1, 'Completed'),   -- Bob’s order
(3, 3, 3, 498.00, 2, 'Completed'),   -- Charlie’s order
(4, 2, 4, 120.00, 1, 'Completed'),   -- Diana’s order
(1, 3, 5, 240.00, 3, 'Completed');   -- Alice’s second order

-- insert order items
-- Order 1: Alice buys iPhone + AirPods
INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 999.00, 999.00),   -- iPhone
(1, 3, 1, 240.00, 240.00);   -- AirPods

-- Order 2: Bob buys Galaxy
INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(2, 2, 1, 899.00, 899.00);

-- Order 3: Charlie buys 2 AirPods
INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(3, 3, 2, 249.00, 498.00);

-- Order 4: Diana buys Nike Shoes
INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(4, 4, 1, 120.00, 120.00);

-- Order 5: Alice buys 3 Hoodies
INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(5, 5, 3, 80.00, 240.00);


