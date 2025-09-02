-- Dimension Loads
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time, end_time)
VALUES
('dim_customer_load', 'SUCCESS', 500, 2.1, '2025-01-02 02:00', '2025-01-02 02:02'),
('dim_product_load', 'SUCCESS', 50, 0.8, '2025-01-07 03:00', '2025-01-07 03:05'),
('dim_store_load', 'SUCCESS', 10, 0.2, '2025-01-31 04:00', '2025-01-31 04:01'),
('dim_date_load', 'SUCCESS', 365, 1.5, '2025-01-01 01:00', '2025-01-01 01:03');

-- Fact Loads (Daily)
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time, end_time)
VALUES
('fact_orders_load', 'SUCCESS', 12000, 45.3, '2025-01-02 05:00', '2025-01-02 05:12'),
('fact_order_items_load', 'SUCCESS', 35000, 80.6, '2025-01-02 05:15', '2025-01-02 05:40'),
('fact_sales_agg_load', 'SUCCESS', 120000, 210.7, '2025-01-31 06:00', '2025-01-31 06:45');

-- Some failures / retries
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time, end_time, error_message)
VALUES
('fact_orders_load', 'FAILED', NULL, NULL, '2025-02-05 05:00', '2025-02-05 05:05', 'Source system timeout'),
('fact_orders_load', 'SUCCESS', 11800, 44.8, '2025-02-05 06:00', '2025-02-05 06:10', ''),
('fact_order_items_load', 'FAILED', NULL, NULL, '2025-03-10 05:15', '2025-03-10 05:20', 'Disk space issue'),
('fact_order_items_load', 'SUCCESS', 36200, 82.4, '2025-03-10 08:00', '2025-03-10 08:25', '');

-- Different months
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time, end_time)
VALUES
('dim_product_load', 'SUCCESS', 40, 0.7, '2025-04-07 03:00', '2025-04-07 03:04'),
('dim_store_load', 'SUCCESS', 15, 0.3, '2025-04-30 04:00', '2025-04-30 04:02'),
('fact_orders_load', 'SUCCESS', 12500, 46.0, '2025-05-12 05:00', '2025-05-12 05:14'),
('fact_order_items_load', 'SUCCESS', 37000, 83.2, '2025-05-12 05:15', '2025-05-12 05:41'),
('fact_sales_agg_load', 'SUCCESS', 128000, 225.9, '2025-06-30 06:00', '2025-06-30 06:48');

-- A recent run in August
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time, end_time)
VALUES
('dim_customer_load', 'SUCCESS', 600, 2.5, '2025-08-01 02:00', '2025-08-01 02:03'),
('fact_orders_load', 'SUCCESS', 13000, 48.2, '2025-08-01 05:00', '2025-08-01 05:13'),
('fact_order_items_load', 'SUCCESS', 39000, 87.0, '2025-08-01 05:15', '2025-08-01 05:42'),
('fact_sales_agg_load', 'SUCCESS', 132000, 230.5, '2025-08-31 06:00', '2025-08-31 06:50');

-- Add running jobs in August 2025
INSERT INTO etl_load_status (job_name, status, rows_loaded, dataset_size_mb, start_time)
VALUES
('fact_orders_load', 'RUNNING', NULL, NULL, '2025-08-02 05:00'),
('fact_order_items_load', 'RUNNING', NULL, NULL, '2025-08-02 05:15');
