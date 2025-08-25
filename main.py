import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP, Context

# Initialize MCP server
mcp = FastMCP("PostgresServer")

# PostgreSQL connection settings
DB_CONFIG = {
    "user": "postgres",         
    "password": "vish3380",
    "dbname": "mcp-demo",
    "host": "localhost",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# ------------------------------
# READ
# ------------------------------
@mcp.tool()
def get_employee_details(ctx: Context, employee_id: int) -> str:
    """Fetch employee details from PostgreSQL by employee_id."""
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

@mcp.tool()
def list_employees(ctx: Context) -> str:
    """Fetch all employees from the employee table."""
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
@mcp.tool()
def add_employee(ctx: Context, name: str, department: str, salary: float) -> str:
    """Insert a new employee record into PostgreSQL."""
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

# ------------------------------
# UPDATE
# ------------------------------
@mcp.tool()
def update_employee(ctx: Context, employee_id: int, name: str = None, department: str = None, salary: float = None) -> str:
    """Update an existing employee record (only provided fields)."""
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

# ------------------------------
# DELETE
# ------------------------------
@mcp.tool()
def delete_employee(ctx: Context, employee_id: int) -> str:
    """Delete an employee record by ID."""
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

# -------------------------
# Dimension Tools
# -------------------------

@mcp.tool()
def add_customer(ctx: Context, first_name: str, last_name: str, email: str, city: str, state: str, country: str, created_at: str) -> str:
    """Insert a new customer into dim_customer."""
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


@mcp.tool()
def add_product(ctx: Context, product_name: str, category: str, brand: str, price: float) -> str:
    """Insert a new product into dim_product."""
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

# -------------------------
# Fact Tools (Orders + Sales)
# -------------------------

@mcp.tool()
def add_order(ctx: Context, customer_id: int, store_id: int, order_date_id: int, total_amount: float, total_items: int, order_status: str) -> str:
    """Insert a new order into fact_orders."""
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


@mcp.tool()
def add_order_item(ctx: Context, order_id: int, product_id: int, quantity: int, unit_price: float) -> str:
    """Insert a new order item into fact_order_items."""
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

@mcp.tool()
def list_customers(ctx: Context, limit: int = 20):
    """List customers (default limit 20)."""
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
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def list_products(ctx: Context, category: str = None, limit: int = 20):
    """List products, optionally filtered by category."""
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
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def list_stores(ctx: Context):
    """List all stores."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT store_id, store_name, city, state, country
            FROM dim_store
            ORDER BY store_name
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def orders_by_customer(ctx: Context, customer_id: int):
    """Get all orders for a specific customer, with totals."""
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
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def order_items(ctx: Context, order_id: int):
    """Get line items for a specific order (products, qty, prices)."""
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
        return rows
    finally:
        cur.close()
        conn.close()

# -------------------------
# Analytics Query Tools
# -------------------------

@mcp.tool()
def top_customers_by_revenue(ctx: Context, limit: int = 5):
    """Return the top N customers by total spend."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.first_name, c.last_name, SUM(o.total_amount) AS spend
            FROM fact_orders o
            JOIN dim_customer c ON o.customer_id = c.customer_id
            GROUP BY c.first_name, c.last_name
            ORDER BY spend DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def sales_by_category(ctx: Context):
    """Return total sales by product category."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.category, SUM(fs.total_amount) AS revenue
            FROM fact_sales fs
            JOIN dim_product p ON fs.product_id = p.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


@mcp.tool()
def orders_by_month(ctx: Context):
    """Return number of orders grouped by year and month."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT d.year, d.month, COUNT(*) AS total_orders
            FROM fact_orders o
            JOIN dim_date d ON o.order_date_id = d.date_id
            GROUP BY d.year, d.month
            ORDER BY d.year, d.month
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


# ------------------------------
# Run the MCP server
# ------------------------------
if __name__ == "__main__":
    mcp.run()