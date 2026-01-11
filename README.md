# MCP Server Presentation

A comprehensive **Model Context Protocol (MCP)** server implementation demonstrating enterprise-grade database operations, analytics, and AI agent integration with PostgreSQL and AWS Bedrock.

## 🎯 Overview

This project showcases two MCP server implementations:
- **Production Server** (`mcpserver.py`) - AWS-based InlineAgent with Aurora PostgreSQL
- **Development Server** (`main.py`) - Local FastMCP server for testing and development
- **Streamlit UI** (`kb.py`) - Interactive web interface for querying the knowledge base

The servers provide a rich set of tools for:
- 📊 **Data Warehouse Operations** - CRUD operations on dimension and fact tables
- 📈 **Analytics Queries** - Revenue analysis, sales trends, customer insights
- 🔍 **Metadata Exploration** - Database schema introspection
- 🤖 **AI Integration** - AWS Bedrock knowledge base queries
- 📦 **ETL Monitoring** - Job status tracking and performance metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Streamlit UI │  │  MCP Client  │  │  Claude Desktop  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │         MCP Server Layer            │
          │  ┌────────────┐  ┌──────────────┐  │
          │  │ mcpserver  │  │  main.py     │  │
          │  │ (Prod)     │  │  (Dev)       │  │
          │  └─────┬──────┘  └──────┬───────┘  │
          └────────┼─────────────────┼──────────┘
                   │                 │
       ┌───────────┴─────────────────┴───────────┐
       │                                          │
       │    🔌 MCP Tools Access Diverse Data      │
       │         Sources & Systems                │
       │                                          │
       ├──────────┬──────────┬──────────┬─────────┤
       ▼          ▼          ▼          ▼         ▼
┌──────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐
│  Aurora  │ │ Bedrock │ │SharePoint│ │Collibra│ │  APIs   │
│PostgreSQL│ │   KB    │ │   Docs   │ │Catalog │ │ & More  │
└──────────┘ └─────────┘ └──────────┘ └────────┘ └─────────┘
   (AWS)        (AWS)     (Microsoft)  (Data Gov)  (Various)
```

**Key Capabilities:**
- 🗄️ **Structured Data** - PostgreSQL, Aurora, data warehouses
- 🤖 **AI Knowledge Bases** - AWS Bedrock, vector databases
- 📄 **Document Repositories** - SharePoint, Confluence, Google Drive
- 📊 **Data Governance** - Collibra, Alation, data catalogs
- 🔌 **REST APIs** - Any HTTP-accessible service
- 📁 **File Systems** - Local files, S3, Azure Blob Storage

---

## 📁 Project Structure

```
mcp-server-presentation/
├── mcpserver.py              # Production MCP server (InlineAgent + AWS)
├── main.py                   # Development MCP server (FastMCP + Local DB)
├── kb.py                     # Streamlit UI for knowledge base queries
├── pyproject.toml            # Project dependencies
├── uv.lock                   # Dependency lock file
├── data/                     # SQL schema and sample data
│   ├── 01_create_schema.sql
│   ├── 02_insert_data.sql
│   ├── 03_create_dim_tables.sql
│   ├── 04_create_fact_tables.sql
│   ├── 05_populate_sample_analytics_data.sql
│   ├── 06_add_additional_data.sql
│   ├── 07_create_etl_metadata_table.sql
│   └── 08_populate_sample_etl_metadata.sql
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (local or AWS Aurora)
- **AWS Account** (for production deployment)
- **uv** package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-server-presentation
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Additional dependencies** (not in pyproject.toml)
   ```bash
   pip install boto3 streamlit matplotlib pandas InlineAgent
   ```

### Database Setup

#### Local Development (PostgreSQL)

1. **Create database**
   ```bash
   createdb mcp-demo
   ```

2. **Run SQL scripts in order**
   ```bash
   psql -d mcp-demo -f data/01_create_schema.sql
   psql -d mcp-demo -f data/02_insert_data.sql
   psql -d mcp-demo -f data/03_create_dim_tables.sql
   psql -d mcp-demo -f data/04_create_fact_tables.sql
   psql -d mcp-demo -f data/05_populate_sample_analytics_data.sql
   psql -d mcp-demo -f data/06_add_additional_data.sql
   psql -d mcp-demo -f data/07_create_etl_metadata_table.sql
   psql -d mcp-demo -f data/08_populate_sample_etl_metadata.sql
   ```

3. **Update credentials in `main.py`**
   ```python
   DB_CONFIG = {
       "user": "your_username",
       "password": "your_password",
       "dbname": "mcp-demo",
       "host": "localhost",
       "port": 5432
   }
   ```

#### Production (AWS Aurora)

1. **Create Aurora PostgreSQL cluster** in AWS RDS

2. **Update credentials in `mcpserver.py`**
   ```python
   DB_CONFIG = {
       "user": "masteruser",
       "password": "your_password",
       "dbname": "postgres",
       "host": "your-cluster.region.rds.amazonaws.com",
       "port": 5432
   }
   ```

3. **Run the same SQL scripts** against Aurora

---

## 🎮 Usage

### Running the Development Server (FastMCP)

```bash
# Start the MCP server
python main.py

# Or use with MCP CLI
mcp run main.py
```

### Running the Production Server (InlineAgent)

```python
from mcpserver import invoke_agent
import asyncio

# Create agent instance
agent = invoke_agent()

# Query the agent
response = asyncio.run(agent.invoke("Show me top customers by revenue"))
print(response)
```

### Running the Streamlit UI

```bash
streamlit run kb.py
```

The UI will open at `http://localhost:8501` with:
- Query input for natural language questions
- Integration with AWS Bedrock knowledge base
- Support for pistachio farming knowledge queries

---

## 🛠️ Available Tools

### 📊 Employee Management (CRUD)
- `get_employee_details(employee_id)` - Fetch employee by ID
- `list_employees()` - List all employees
- `add_employee(name, department, salary)` - Create new employee
- `update_employee(employee_id, ...)` - Update employee fields
- `delete_employee(employee_id)` - Delete employee

### 🏪 Dimension Management
- `add_customer(first_name, last_name, email, ...)` - Add customer
- `add_product(product_name, category, brand, price)` - Add product
- `list_customers(limit)` - List customers
- `list_products(category, limit)` - List products
- `list_stores()` - List all stores

### 🛒 Order Management
- `add_order(customer_id, store_id, ...)` - Create order
- `add_order_item(order_id, product_id, ...)` - Add order line item
- `orders_by_customer(customer_id)` - Get customer orders
- `order_items(order_id)` - Get order details
- `orders_by_product(product_id)` - Find orders containing product
- `orders_by_store(store_id)` - Get store orders

### 📈 Analytics Queries
- `top_customers_by_revenue(limit)` - Top customers by spend
- `sales_by_category(limit)` - Sales breakdown by category
- `daily_sales_trend(limit)` - Daily sales trends
- `sales_by_store(limit)` - Store performance metrics
- `product_sales_rank(limit)` - Top-selling products
- `top_products_by_store(store_id, limit)` - Store's best products

### 🔍 Metadata Exploration
- `list_tables()` - List all database tables
- `table_metadata(table_name)` - Get table column info
- `column_metadata(table_name, column_name)` - Column details
- `primary_keys(table_name)` - Get primary keys
- `foreign_keys(table_name)` - Get foreign key relationships

### 📦 ETL Monitoring
- `get_last_failed_jobs()` - Recent failed ETL jobs
- `get_running_jobs()` - Currently running jobs
- `get_avg_load_time()` - Average job duration
- `get_recent_runs(job_name)` - Job execution history
- `get_largest_datasets()` - Largest data loads
- `update_job_status(...)` - Update job status
- `get_sla_breaches(max_minutes)` - Jobs exceeding SLA
- `get_job_success_rate()` - Success rate by job

### 🤖 AI/Knowledge Base
- `get_knowledge_base(user_query)` - Query AWS Bedrock KB for pistachio farming info

---

## 🎨 Key Features

### 1. **Dual Server Architecture**

| Feature | `mcpserver.py` (Production) | `main.py` (Development) |
|---------|---------------------------|------------------------|
| Framework | InlineAgent | FastMCP |
| Database | AWS Aurora PostgreSQL | Local PostgreSQL |
| Return Format | JSON strings | Python objects |
| Data Conversion | Decimal/datetime → JSON | Native types |
| Agent Model | Claude 3.7 Sonnet | N/A |
| Use Case | Production deployment | Local testing |

### 2. **Action Groups** (Production Server)

The production server organizes tools into logical action groups:

```python
- DatabaseAction: Employee CRUD operations
- KnowledgeBase: AWS Bedrock queries
- DimensionFact: Customer/product/order management
- Lookup: Query operations
- Analytics: Revenue and sales analytics
- Metadata: Schema introspection
```

### 3. **Advanced Analytics**

- **Time-based aggregations** - Year, quarter, month breakdowns
- **Revenue tracking** - Customer, product, store, category
- **Trend analysis** - Daily sales patterns
- **Performance metrics** - Store comparisons, product rankings

### 4. **Data Type Handling**

Production server includes robust data conversion:
```python
def convertrowstostring(rows):
    # Converts Decimal → float
    # Converts date/datetime → ISO format
    # Ensures JSON serialization
```

### 5. **Comprehensive Prompting**

The production agent uses a detailed system prompt that:
- Defines structured + unstructured data sources
- Specifies output format (Markdown tables, insights)
- Enforces data quality checks
- Prevents hallucination
- Provides visualization recommendations

---

## 📊 Database Schema

### Dimension Tables
- `dim_customer` - Customer information
- `dim_product` - Product catalog
- `dim_store` - Store locations
- `dim_date` - Date dimension for time-series analysis

### Fact Tables
- `fact_orders` - Order headers
- `fact_order_items` - Order line items
- `employee` - Employee records

### Metadata Tables
- `etl_load_status` - ETL job monitoring

---

## 🔐 Configuration

### Environment Variables (Recommended)

Create a `.env` file:
```bash
# Database
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mcp-demo

# AWS
AWS_REGION=us-east-1
BEDROCK_AGENT_ID=your_agent_id
BEDROCK_AGENT_ALIAS_ID=your_alias_id
```

### AWS Bedrock Setup

1. Create a Bedrock Agent in AWS Console
2. Configure knowledge base with pistachio farming documents
3. Update agent IDs in `mcpserver.py` and `kb.py`

---

## 🧪 Testing

### Test Employee CRUD
```python
from mcpserver import invoke_agent
import asyncio

agent = invoke_agent()

# Add employee
response = asyncio.run(agent.invoke("Add employee John Doe in Engineering with salary 85000"))

# List employees
response = asyncio.run(agent.invoke("List all employees"))

# Update employee
response = asyncio.run(agent.invoke("Update employee 1 salary to 90000"))
```

### Test Analytics
```python
# Top customers
response = asyncio.run(agent.invoke("Show me top 10 customers by revenue"))

# Sales trends
response = asyncio.run(agent.invoke("What are the daily sales trends?"))

# Store performance
response = asyncio.run(agent.invoke("Compare sales by store"))
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Import Error: `performance` module not found**
   ```bash
   # Create a stub performance.py file
   echo "def store_performance(): pass" > performance.py
   ```

2. **Database Connection Failed**
   - Check PostgreSQL is running: `pg_isready`
   - Verify credentials in DB_CONFIG
   - Ensure database exists: `psql -l`

3. **AWS Bedrock Access Denied**
   - Configure AWS credentials: `aws configure`
   - Verify IAM permissions for Bedrock
   - Check agent IDs are correct

4. **Streamlit UI Not Loading**
   - Install missing dependencies: `pip install streamlit matplotlib pandas`
   - Check if `style/final.css` and `image/` directories exist
   - Create stub files if missing

---

## 📝 Development Notes

### Code Quality
- ✅ All Python files compile without syntax errors
- ✅ Type hints used throughout
- ✅ Comprehensive docstrings
- ✅ Proper error handling with try/finally blocks

### Best Practices
- Connection management with context managers
- Parameterized SQL queries (SQL injection prevention)
- JSON serialization for API compatibility
- Modular action group organization

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is provided as-is for demonstration purposes.

---

## 🙏 Acknowledgments

- **Model Context Protocol (MCP)** - Anthropic
- **FastMCP** - MCP server framework
- **InlineAgent** - AWS Bedrock agent framework
- **PostgreSQL** - Database system
- **AWS Bedrock** - AI/ML services

---

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.

---

## 🗺️ Roadmap

- [ ] Add authentication/authorization
- [ ] Implement caching layer (Redis)
- [ ] Add GraphQL API
- [ ] Create Docker containers
- [ ] Add comprehensive test suite
- [ ] Implement rate limiting
- [ ] Add monitoring/observability (Prometheus/Grafana)
- [ ] Create API documentation (Swagger/OpenAPI)

---

**Built with ❤️ using MCP, PostgreSQL, and AWS Bedrock**
