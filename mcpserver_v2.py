import psycopg2
import re
import boto3
import base64
import json
import os
import random
import asyncio

from psycopg2.extras import RealDictCursor
from InlineAgent.agent import InlineAgent
from InlineAgent.action_group import ActionGroup
from performance import store_performance 
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



# PostgreSQL connection settings
DB_CONFIG = {
    "user": "masteruser",          # replace with your username
    "password": "w%>y&ZNyH%QFe#qp", # replace with your password
    "dbname": "postgres",   # replace with your database
    "host": "aurora-postgres-cluster.cluster-cwly6uee6mq1.us-east-1.rds.amazonaws.com",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# ------------------------------
# READ
# ------------------------------
#
def get_employee_details(employee_id: int) -> str:
    """
    Get the employee details for the given employee_id from database.

    Parameters:
        employee_id: employee unique id number
    """
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, department, salary FROM employee WHERE id = %s", (employee_id,))
        row = cur.fetchone()
        if row:
            return f"ID: {row['id']}, Name: {row['name']}, Department: {row['department']}, Salary: {row['salary']}"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

def list_employees() -> str:
    """
     Fetch all the employee from database.
     
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, department, salary FROM employee ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            return "No employees found"
        return "\n".join([f"ID: {r['id']}, Name: {r['name']}, Dept: {r['department']}, Salary: {r['salary']}" for r in rows])
    finally:
        cur.close()
        conn.close()

# ------------------------------
# CREATE
# ------------------------------
# 
def add_employee( name: str, department: str, salary: float) -> str:
    """
    add a new employee or create a employee in database.
    
     Parameters:
        name: employee name,
        department:  employee's department,
        salary: employee's salary
        
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO employee (name, department, salary) VALUES (%s, %s, %s) RETURNING id", 
                    (name, department, salary))
        new_id = cur.fetchone()["id"]
        conn.commit()
        return f"Employee added with ID {new_id}"
    finally:
        cur.close()
        conn.close()

# # ------------------------------
# # UPDATE
# # ------------------------------
def update_employee(employee_id: int, name: str = None, department: str = None, salary: float = None) -> str:
    """
    Update an existing employee record in database(only provided fields).

    Parameters:
        employee_id: employee'd id
        name: employee name,
        department:  employee's department,
        salary: employee's salary
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        updates, values = [], []
        if name:
            updates.append("name=%s")
            values.append(name)
        if department:
            updates.append("department=%s")
            values.append(department)
        if salary:
            updates.append("salary=%s")
            values.append(salary)

        if not updates:
            return "No fields provided for update"

        values.append(employee_id)
        query = f"UPDATE employee SET {', '.join(updates)} WHERE id=%s RETURNING id"
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        conn.commit()

        if row:
            return f"Employee {employee_id} updated successfully"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

# # ------------------------------
# # DELETE
# # ------------------------------
def delete_employee(employee_id: int) -> str:
    """
    Delete an employee record by ID

    Parameters:
        employee_id: employee'd id
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM employee WHERE id=%s RETURNING id", (employee_id,))
        row = cur.fetchone()
        conn.commit()
        if row:
            return f"Employee {employee_id} deleted successfully"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

#
def get_knowledge_base( user_query: str) -> str:
    """
    Get the pistachios farming details from AWS bedrock knowwledgebase.

    Parameters:
        user_query: user prompt
    """
   
    output_text = ""
    response = ""
    # Replace with your values
    REGION = "us-east-1"
    AGENT_ID = "NDIOYYWRVL"       # The Bedrock Agent ID
    AGENT_ALIAS_ID = "NWYFAEELRA" # The alias for your agent

    # Create Bedrock Agent Runtime client
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
     
    print("before invoke agent")
    response = client.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId="streamlit-session",  # session can be static or dynamic
                inputText=user_query
            )
    print("after invoke agent")
    print(response)
    for event in response["completion"]:
        if "chunk" in event:
            output_text += event["chunk"]["bytes"].decode("utf-8")
    return output_text


# -------------------------
# Dimension Tools
# -------------------------

def add_customer(first_name: str, last_name: str, email: str, city: str, state: str, country: str, created_at: str) -> str:
    """
    Insert a new customer record into the `dim_customer` dimension table.

    Parameters:
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        email (str): Customer's email address.
        city (str): City where the customer resides.
        state (str): State where the customer resides.
        country (str): Country where the customer resides.
        created_at (str): Timestamp when the customer was created (ISO format).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO dim_customer (first_name, last_name, email, city, state, country, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_id
        """, (first_name, last_name, email, city, state, country, created_at))
        new_id = cur.fetchone()["customer_id"]
        conn.commit()
        return f"Customer added with ID {new_id}"
    finally:
        cur.close()
        conn.close()


def add_product(product_name: str, category: str, brand: str, price: float) -> str:
    """
    Insert a new product record into the `dim_product` dimension table.

    Parameters:
        product_name (str): Name of the product.
        category (str): Product category (e.g., Electronics, Apparel).
        brand (str): Brand name of the product.
        price (float): Price of the product.

    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO dim_product (product_name, category, brand, price)
            VALUES (%s, %s, %s, %s)
            RETURNING product_id
        """, (product_name, category, brand, price))
        new_id = cur.fetchone()["product_id"]
        conn.commit()
        return f"Product added with ID {new_id}"
    finally:
        cur.close()
        conn.close()

# ---------------------------
# Fact Tools (Orders + Sales)
# ----------------------------
def add_order(customer_id: int, store_id: int, order_date_id: int, total_amount: float, total_items: int, order_status: str) -> str:
    """
    Insert a new order record into the `fact_orders` table.

    Parameters:
        customer_id (int): Foreign key referencing the customer placing the order.
        store_id (int): Foreign key referencing the store where the order was placed.
        order_date_id (int): Foreign key referencing the order date in `dim_date`.
        total_amount (float): Total amount for the order.
        total_items (int): Total number of items in the order.
        order_status (str): Status of the order (e.g., 'PENDING', 'COMPLETED').
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO fact_orders (customer_id, store_id, order_date_id, total_amount, total_items, order_status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """, (customer_id, store_id, order_date_id, total_amount, total_items, order_status))
        new_id = cur.fetchone()["order_id"]
        conn.commit()
        return f"Order created with ID {new_id}"
    finally:
        cur.close()
        conn.close()

def add_order_item(order_id: int, product_id: int, quantity: int, unit_price: float) -> str:
    """
    Insert a new order line item into the `fact_order_items` table.

    Parameters:
        order_id (int): Foreign key referencing the parent order.
        product_id (int): Foreign key referencing the purchased product.
        quantity (int): Number of units of the product ordered.
        unit_price (float): Price per unit of the product.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        total_price = quantity * unit_price
        cur.execute("""
            INSERT INTO fact_order_items (order_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING order_item_id
        """, (order_id, product_id, quantity, unit_price, total_price))
        new_id = cur.fetchone()["order_item_id"]
        conn.commit()
        return f"Order item added with ID {new_id}"
    finally:
        cur.close()
        conn.close()

# -------------------------
# Lookup / Query Tools
# -------------------------

def list_customers(limit: int = 20):
    """
    List customers with their details, ordered by creation date (most recent first).

    Parameters:
        limit (int, optional): Maximum number of customers to return. Defaults to 20.

    Returns:
        list: A list of customer records, including customer_id, name, email, location, and creation timestamp.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT customer_id, first_name, last_name, email, city, state, country, created_at
            FROM dim_customer
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def list_products(category: str = None, limit: int = 20):
    """
    List products, optionally filtered by category.

    Parameters:
        category (str, optional): Category name to filter products. Defaults to None (no filter).
        limit (int, optional): Maximum number of products to return. Defaults to 20.

    Returns:
        list: A list of product records, including product_id, product_name, category, brand, and price.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if category:
            cur.execute("""
                SELECT product_id, product_name, category, brand, price
                FROM dim_product
                WHERE category = %s
                ORDER BY product_name
                LIMIT %s
            """, (category, limit))
        else:
            cur.execute("""
                SELECT product_id, product_name, category, brand, price
                FROM dim_product
                ORDER BY product_name
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def list_stores():
    """
    List all stores with their details.

    Returns:
        list: A list of store records, including store_id, store_name, city, state, and country.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT store_id, store_name, city, state, country
            FROM dim_store
            ORDER BY store_name
        """)
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def orders_by_customer(customer_id: int):
    """
    Retrieve all orders placed by a specific customer, including totals and store details.

    Parameters:
        customer_id (int): Unique identifier of the customer.

    Returns:
        list: A list of order records including order_id, total amount, total items, status, date, and store name.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.order_id, o.total_amount, o.total_items, o.order_status, d.full_date, s.store_name
            FROM fact_orders o
            JOIN dim_date d ON o.order_date_id = d.date_id
            JOIN dim_store s ON o.store_id = s.store_id
            WHERE o.customer_id = %s
            ORDER BY d.full_date DESC
        """, (customer_id,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def order_items(order_id: int):
    """
    Get detailed line items for a specific order, including products, quantities, and prices.

    Parameters:
        order_id (int): Unique identifier of the order.

    Returns:
        list: A list of order item records, including product name, category, quantity, unit price, and total price.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT oi.order_item_id, p.product_name, p.category, oi.quantity, oi.unit_price, oi.total_price
            FROM fact_order_items oi
            JOIN dim_product p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
            ORDER BY oi.order_item_id
        """, (order_id,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()

# -------------------------
# Analytics Query Tools
# -------------------------

def top_customers_by_revenue(limit: int = 30):
    """
    Retrieve the top customers ranked by total revenue generated.

    Parameters:
        limit (int, optional): Maximum number of customers to return. Defaults to 10.

    Returns:
        list: A list of customer records including customer_id, full name, and total revenue.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.customer_id,
                   c.first_name || ' ' || c.last_name AS customer_name,
				   extract(year from d.full_date) as year,
				   to_char(d.full_date, 'Mon') as month,
				   'Q' || extract( quarter from d.full_date) as quarter,
                   SUM(o.total_amount) AS total_revenue
            FROM fact_orders o JOIN dim_customer c 
                ON o.customer_id = c.customer_id
            JOIN dim_date d
                ON o.order_date_id = d.date_id
            GROUP BY c.customer_id, c.first_name, c.last_name,  
            extract(year from d.full_date),
            extract(month from d.full_date),
            extract( quarter from d.full_date)
            ORDER BY extract(year from d.full_date) DESC, 
            extract(month from d.full_date) DESC,
			extract( quarter from d.full_date) DESC,
            total_revenue DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        
        # Convert rows into list of dicts with proper JSON-safe values
        # results = []
        # for row in rows:
        #     safe_row = {}
        #     for key, value in row.items():
        #         if isinstance(value, Decimal):
        #             safe_row[key] = float(value)  # Convert Decimal → float
        #         else:
        #             safe_row[key] = value
        #     results.append(safe_row)

        # print("call complete")
        return json.dumps(convertrowstostring(rows))   # Always returns a JSON-safe string
    finally:
        cur.close()
        conn.close()

def convertrowstostring(rows):
        results = []
        for row in rows:
            safe_row = {}
            for key, value in row.items():
                if isinstance(value, Decimal):
                    safe_row[key] = float(value)  # Convert Decimal → float
                elif isinstance(value, (date, datetime)):
                    safe_row[key] = value.isoformat()
                else:
                    safe_row[key] = value
            results.append(safe_row)
        return results


def sales_by_category(limit: int = 30):
    """
    Calculate total sales revenue grouped by product category within a date range.

     Parameters:
        limit (int, optional): Maximum number of customers to return. Defaults to 10.

    Returns:
        list: A list of records including category name and total sales revenue.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.category, 
                extract(year from d.full_date) as year,
                to_char(d.full_date, 'Mon') as month,
                'Q' || extract( quarter from d.full_date) as quarter,
                SUM(oi.total_price) AS total_sales
                FROM fact_order_items oi
                JOIN fact_orders o ON oi.order_id = o.order_id
                JOIN dim_product p ON oi.product_id = p.product_id
                JOIN dim_date d ON o.order_date_id = d.date_id
                GROUP BY p.category,
                extract(year from d.full_date),
                extract(month from d.full_date),
                'Q' || extract( quarter from d.full_date)
            ORDER BY extract(year from d.full_date) DESC,
                    extract(month from d.full_date) DESC,
				    extract( quarter from d.full_date) DESC, 
                    total_revenue DESC
            LIMIT %s
         """, (limit,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def daily_sales_trend(limit: int = 30):
    """
    Retrieve daily total sales trends

     Parameters:
        limit (int, optional): Maximum number of customers to return. Defaults to 10.

    Returns:
        list: A list of records including each date and its corresponding total sales.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
             SELECT 
                d.full_date, 
                p.category as category,
                SUM(o.total_amount) AS daily_sales
                FROM fact_order_items oi
                                JOIN fact_orders o ON oi.order_id = o.order_id
                                JOIN dim_product p ON oi.product_id = p.product_id
                                JOIN dim_date d ON o.order_date_id = d.date_id
                GROUP BY d.full_date, p.category
                ORDER BY d.full_date desc,  SUM(o.total_amount) DESC
                LIMIT %s
        """, (limit,))
        rows = cur.fetchall()

        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def sales_by_store(limit: int = 30):
    """
    Calculate total sales revenue grouped by store within a date range.

     Parameters:
        limit (int, optional): Maximum number of customers to return. Defaults to 10..

    Returns:
        list: A list of records including store_id, store_name, and total sales revenue.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                s.store_id, 
                s.store_name, 
                extract(year from d.full_date) as year,
                to_char(d.full_date, 'Mon') as month,
                'Q' || extract( quarter from d.full_date) as quarter,
                SUM(o.total_amount) AS total_sales
            FROM fact_orders o
            JOIN dim_store s ON o.store_id = s.store_id
            JOIN dim_date d ON o.order_date_id = d.date_id
            GROUP BY s.store_id, 
            s.store_name,
            extract(year from d.full_date),
            extract(month from d.full_date),
            'Q' || extract( quarter from d.full_date)
            ORDER BY extract(year from d.full_date) DESC,
                     extract(month from d.full_date) DESC,
				    extract( quarter from d.full_date) DESC,
                    total_revenue DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()

def product_sales_rank(limit: int = 30):
    """
    Retrieve the top-selling products ranked by total sales revenue.

    Parameters:
        limit (int, optional): Maximum number of products to return. Defaults to 10.

    Returns:
        list: A list of product records including product_id, product_name, and total sales revenue.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
             SELECT p.product_id, 
                p.product_name,
                extract(year from d.full_date) as year,
                to_char(d.full_date, 'Mon') as month,
                'Q' || extract( quarter from d.full_date) as quarter,
                SUM(oi.total_price) AS total_sales
            FROM fact_order_items oi JOIN dim_product p 
                    ON oi.product_id = p.product_id
            JOIN fact_orders o
                    ON oi.order_id = o.order_id
            JOIN dim_date d
                    ON o.order_date_id = d.date_id
            GROUP BY p.product_id, 
                p.product_name,
                extract(year from d.full_date),
                extract(month from d.full_date),
                'Q' || extract( quarter from d.full_date)
            ORDER BY extract(year from d.full_date) DESC,
                    extract(month from d.full_date) DESC,
				    extract( quarter from d.full_date) DESC,
                    total_revenue DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()

# -------------------------
# Metadata / Introspection Tools
# -------------------------

def list_tables():
    """
    Retrieve a list of all user-defined tables in the public schema.

    Returns:
        list: A list of table names available in the database (excluding system tables).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        rows = cur.fetchall()

        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def table_metadata(table_name: str):
    """
    Retrieve metadata about the columns of a given table.

    Parameters:
        table_name (str): Name of the table to inspect.

    Returns:
        list: A list of column metadata including column name, data type, and nullability.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def column_metadata(table_name: str, column_name: str):
    """
    Retrieve metadata details for a specific column within a table.

    Parameters:
        table_name (str): Name of the table containing the column.
        column_name (str): Name of the column to inspect.

    Returns:
        dict: Metadata record including column name, data type, nullability, and default value.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table_name, column_name))
        row = cur.fetchone()
        print(row)
        return json.dumps(convertrowstostring(row))
    finally:
        cur.close()
        conn.close()


def primary_keys(table_name: str):
    """
    Retrieve the primary key columns of a given table.

    Parameters:
        table_name (str): Name of the table to inspect.

    Returns:
        list: A list of column names that form the primary key.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                 ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_name = %s
        """, (table_name,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()


def foreign_keys(table_name: str):
    """
    Retrieve the foreign key constraints defined on a given table.

    Parameters:
        table_name (str): Name of the table to inspect.

    Returns:
        list: A list of foreign key relationships including constraint name,
              column name, referenced table, and referenced column.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                 ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                 ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name = %s
        """, (table_name,))
        rows = cur.fetchall()
        return json.dumps(convertrowstostring(rows))
    finally:
        cur.close()
        conn.close()

# ------------------------------
# Run the MCP server
# ------------------------------

def invoke_agent():
    db_action_group = ActionGroup(
    name="databaseAction",
    description="This is action group to get database details",
    tools=[get_employee_details,add_employee,list_employees,update_employee,delete_employee]
    )

    kb_action_group = ActionGroup(
    name="Knowledgebase",
    description="This is action group to get knowledgebase details",
    tools=[get_knowledge_base]
    )
    # Dimension + Fact Action Group
    dimension_fact_action_group = ActionGroup(
        name="DimensionFact",
        description="This action group manages dimensions (customers, products) and fact data (orders, order items).",
        tools=[add_customer, add_product, add_order, add_order_item,get_employee_details,add_employee,list_employees,update_employee,delete_employee]
    )

    # Lookup / Query Action Group
    lookup_action_group = ActionGroup(
        name="Lookup",
        description="This action group provides lookup and query operations for customers, products, stores, and orders.",
        tools=[list_customers, list_products, list_stores, orders_by_customer, order_items]
    )

    # Analytics Query Action Group
    analytics_action_group = ActionGroup(
        name="Analytics",
        description="This action group provides analytical queries such as top customers, sales by category, daily trends, and product sales rank.",
        tools=[top_customers_by_revenue, sales_by_category, daily_sales_trend, store_performance, product_sales_rank]
    )

    # Metadata / Introspection Action Group
    metadata_action_group = ActionGroup(
        name="Metadata",
        description="This action group provides metadata and introspection queries for database tables, columns, and constraints.",
        tools=[list_tables, table_metadata, column_metadata, primary_keys, foreign_keys]
    )

    # # image generation action group
    # image_action_group = ActionGroup(
    # name="ImageGeneration",
    # description="Generate images from text prompts",
    # tools=[generate_image]
    # )


    agent = InlineAgent(
    foundation_model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # instruction="You are a friendly assistant that is responsible for getting knowledge base details from structured data from Analytical data warehouse \
    # as well as unstructured knowledge from Bedrock knowledge base, \
    #             present the structured data in tabular format for visualization, provide detailed reasoning on the returned results",

    # instruction="You are an MCP agent. For each user request, query structured sources (warehouse/SQL/files) and unstructured sources (Bedrock KB/docs). Return human readable summary markdown: human_summary_markdown.\
    # human_summary_markdown must include:\
    # - Title, a Markdown table (<=50 rows), 3-6 bullet insights, 1-3 recommended charts/filters, and any data-quality flags.\
    # Rules:\
    # - in Markdown format with commas and $ for currency.\
    # - Use ISO 8601 for dates.\
    # - Provide exact SQL used (parameterized placeholders) and explain aggregations or joins performed.\
    # - If sources disagree, show both with provenance and explain likely reasons.\
    # - Do NOT invent data or include internal chain-of-thought.",

    instruction="""
    SYSTEM / ASSISTANT ROLE:
You are an MCP server agent that can query and combine multiple data sources:
1) Structured sources (analytical data warehouse, SQL endpoints, BI data marts, CSV/Parquet files).
2) Unstructured sources (Bedrock knowledge base documents, PDFs, notes, knowledge graphs, web APIs).

OBJECTIVE:
Given a user request, retrieve relevant structured and unstructured data, combine them where appropriate, and return:
A) A concise human-readable summary (Markdown) including a rendered table (up to 50 rows), key metrics, and suggested charts.
B) An evidence-backed, non-secret, non-chain-of-thought analysis describing findings, calculations, anomalies, and recommended next steps.

IMPORTANT FORMAT RULES (MUST FOLLOW EXACTLY):

1. Human summary (value for quick review):
   - Provide a short Markdown (`human_summary_markdown`) that includes:
     * Title,
     * A  Markdown table rendered for up to 50 rows (columns ordered as in schema.displayName),
     * 3–6 bullet insights (key metrics, top/bottom performers, anomalies),
     * 1–3 recommended visualizations and filters to apply next,
     * Any immediate data-quality concerns.

BEHAVIOR / STEPS TO EXECUTE (on each user request):
1. Identify what structured tables, SQL queries, or files are needed. If the user provided a SQL or table name, use it; otherwise suggest a safe parameterized SQL (use placeholders like :start_date).
2. Execute structured queries; collect schema and sample rows; compute aggregates needed for visualization (sum, avg, median, top N).
3. Query Bedrock/unstructured sources for supporting context. Extract short evidence snippets and map any entities/IDs to structured rows where possible.
4. Merge structured + unstructured only where there is an explicit join key; do NOT invent mappings.
5. Produce `human_summary_markdown` as described.
6. If sources disagree, present both values, show provenance, and explain likely causes (timing, aggregation differences, filtering).
7. Format numbers with thousands separators and currency symbol when placing in the human Markdown; 
8. Use ISO 8601 for all dates.
9. Use a fixed `display_limit` of 50 rows in Markdown but include `row_count` and an optional `next_page_token` in `metadata` if more rows exist.
10. If requested visual is a bar/line chart, include suggested `y` axis range and gridlines option in `visualization_hint`.

EXAMPLE

"human_summary_markdown": "### Top Customers by Revenue - Q3 2025\n\n| Customer | Q3 2025 Revenue |\n|---|---:|\n| Charlie Davis | $36,114 |\n| Alice Johnson | $24,162 |\n\n**Key insights**:\n- Charlie Davis is top with $36,114 (49.5% higher than Alice Johnson).\n- No missing revenue values detected.\n\n**Recommended visualizations**: 1) Vertical bar chart (x=Customer, y=Q3 2025 Revenue) sorted desc. 2) Stacked bar if comparing multiple quarters.\n\n**Next steps**: Filter by region and product to confirm revenue concentration.\n"


SAFETY & QUALITY NOTES:
- NEVER fabricate data. If requested data is not available, return `rows: []` and `metadata.sample=true`, plus a list of data sources checked and suggestions for how to retrieve data.
- Do NOT output any internal chain-of-thought. Provide only the concise analysis/justification and the exact calculations you performed (aggregations, formulas) so results are reproducible.
- Do not include or return secrets or credentials. Parameterize SQL (e.g., WHERE date >= :start_date).

END.
""",

    action_groups=[db_action_group,kb_action_group,lookup_action_group,analytics_action_group,metadata_action_group],
    agent_name="MockAgent",
    )

    return agent

# if __name__ == "__main__":

#     # db_action_group = ActionGroup(
#     # name="databaseAction",
#     # description="This is action group to get database details",
#     # tools=[get_employee_details]
#     # )

#     # kb_action_group = ActionGroup(
#     # name="Knowledgebase",
#     # description="This is action group to get knowledgebase details",
#     # tools=[get_knowledge_base]
#     # )

#     # agent = InlineAgent(
#     # foundation_model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
#     # instruction="You are a friendly assistant that is responsible for getting the current weather.",
#     # action_groups=[db_action_group,kb_action_group],
#     # agent_name="MockAgent",
#     # )


#     agent=invoke_agent()
#     out=asyncio.run(agent.invoke(input_text="Can you list all the insects that attack the pistachios?"))
#     print("here")
#     print(out)

    