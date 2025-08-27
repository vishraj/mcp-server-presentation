-- Generate 100 synthetic orders with 1-3 items per order
DO $$
DECLARE
    v_cust_id INT;
    v_store_id INT;
    v_prod_id INT;
    v_qty INT;
    v_unit_price NUMERIC(12,2);
    v_order_total NUMERIC(12,2);
    v_total_items INT;
    v_new_order_id INT;
    v_new_date_id INT;
    i INT;
    j INT;
    v_num_items INT;
BEGIN
    FOR i IN 1..100 LOOP
        -- Random customer (1–4)
        v_cust_id := (SELECT (floor(random()*4)+1)::int);
        -- Random store (1–3)
        v_store_id := (SELECT (floor(random()*3)+1)::int);
        -- Random date_id from 2023-01-01 to 2024-12-31
        v_new_date_id := (
            SELECT date_id
            FROM dim_date
            WHERE full_date BETWEEN '2023-01-01' AND '2024-12-31'
            ORDER BY random()
            LIMIT 1
        );

        -- Insert order header with dummy totals
        INSERT INTO fact_orders(customer_id, store_id, order_date_id, total_amount, total_items, order_status)
        VALUES (v_cust_id, v_store_id, v_new_date_id, 0, 0, 'Completed')
        RETURNING order_id INTO v_new_order_id;

        -- Random number of items per order: 1–3
        v_num_items := 1 + floor(random()*3)::int;
        v_order_total := 0;
        v_total_items := 0;

        FOR j IN 1..v_num_items LOOP
            -- Random product (1–5)
            v_prod_id := (SELECT (floor(random()*5)+1)::int);
            -- Random quantity 1–3
            v_qty := 1 + floor(random()*3)::int;
            -- Lookup unit price from dim_product
            SELECT price INTO v_unit_price
            FROM dim_product
            WHERE product_id = v_prod_id;

            -- Insert into fact_order_items
            INSERT INTO fact_order_items(order_id, product_id, quantity, unit_price, total_price)
            VALUES (v_new_order_id, v_prod_id, v_qty, v_unit_price, v_qty*v_unit_price);

            -- Update running totals for the order
            v_order_total := v_order_total + (v_qty*v_unit_price);
            v_total_items := v_total_items + v_qty;
        END LOOP;

        -- Update order totals
        UPDATE fact_orders
        SET total_amount = v_order_total,
            total_items = v_total_items
        WHERE order_id = v_new_order_id;
    END LOOP;
END $$;
