# E-Commerce Medallion Architecture Data Platform

A production-grade E-Commerce Data Engineering pipeline built on PostgreSQL and Python. This project demonstrates modern **Lakehouse/Medallion Architecture** patterns by transforming raw API ingestion data through sequential quality stages (Bronze, Silver, and Gold) to compute enterprise-level business KPIs.

## 🏗️ Architecture

```mermaid
graph TD
    API_Products[API: /products] -->|Requests| Bronze_Products[Bronze: raw_products]
    API_Users[API: /users] -->|Requests| Bronze_Users[Bronze: raw_users]
    
    Bronze_Products -->|Pandas / SQL| Silver_Products[Silver: products, categories, product_images]
    Bronze_Users -->|Pandas / SQL| Silver_Users[Silver: users]
    
    Silver_Products & Silver_Users -->|Pandas Simulation| Silver_Sales[Silver: sales_transactions]
    
    Silver_Sales & Silver_Products & Silver_Users -->|SQL transformations| Gold[Gold Layer: kpi_category_performance, kpi_price_segmentation, kpi_user_sales_performance]
```

### 🥉 Bronze Layer (Raw Ingest)
- **Ingestion**: Raw JSON payloads fetched directly from the E-Commerce API endpoints (`/products` and `/users`).
- **Transformations**: None. Preserves absolute source fidelity.
- **Metadata**: Ingestion timestamps are appended.
- **Storage**: `bronze.raw_products` and `bronze.raw_users` (PostgreSQL `JSONB` columns).

### 🥈 Silver Layer (Cleaned & Relationalized)
- **Transformations**: Flattened JSON structures, parsed data types, handled missing values, and validated schema constraints.
- **Deduplication**: Records sorted by category, user, and product modification timestamps to deduplicate and persist only the latest snapshots.
- **Data Enrichment**: Simulates transactional customer sales over the past 30 days (`silver.sales_transactions`) by matching items to real customer profiles (`silver.users`).
- **Storage**: Normalized tables:
  - `silver.categories`
  - `silver.users`
  - `silver.products`
  - `silver.product_images`
  - `silver.sales_transactions`

### 🥇 Gold Layer (Business Intelligence / KPIs)
- **Transformations**: Computes aggregations and business metrics directly inside PostgreSQL using high-performance SQL.
- **Storage**:
  - `gold.kpi_category_performance`: Aggregated catalog volume, average pricing, total quantity sold, and total revenue per category.
  - `gold.kpi_price_segmentation`: Distribution of sales metrics grouped by pricing tiers: **Budget** ($\le \$20$), **Mid-Range** ($\$20 < \text{Price} \le \$100$), and **Premium** ($> \$100$).
  - `gold.kpi_user_sales_performance`: Customer value metrics showing total purchases, total spend, and average order value per user.

---

## 🧰 Tech Stack
- **Python**: Ingestion, cleaning, transformation logic, and simulation.
- **PostgreSQL**: Lakehouse storage, relational mapping, schema isolation, and analytical aggregates.
- **SQL / DDL**: Relational schemas, database constraints, indexing, and window functions.
- **Pandas**: Efficient flattening, data type casting, and deduplication logic.
- **SQLAlchemy**: Safe session pool management and connection interface.

---

## 📂 Project Structure
```
├── requirements.txt         # Project package requirements
├── .env                     # Configuration file for Database & API URLs
├── run_pipeline.py          # Orchestration pipeline entrypoint
├── src/
│   ├── config.py            # Configuration loader
│   ├── db.py                # Database engine setup & schema init
│   ├── extract.py           # Ingest API -> Bronze Layer
│   ├── transform_silver.py  # Standardize and Relationalize -> Silver Layer
│   └── transform_gold.py    # Compute analytical KPIs -> Gold Layer
└── sql/
    ├── ddl_bronze.sql       # Bronze DDL schema
    ├── ddl_silver.sql       # Silver DDL schema
    └── ddl_gold.sql         # Gold DDL schema
```

---

## 🚀 How to Run

### 1. Prerequisites
- **Python 3.8+**
- **PostgreSQL instance**

### 2. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Configuration
Create a `.env` file in the root directory (based on `.env.example`):
```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
API_URL=https://api.escuelajs.co/api/v1/products
```

### 4. Run the Pipeline
Execute the pipeline orchestrator:
```bash
python run_pipeline.py
```

---

## 📊 Analytics Results (Gold Layer Sample)

### Category Performance KPI
Provides sales and catalog statistics aggregated by product categories.

| Category ID | Category Name  | Product Count | Average Price ($) | Total Qty Sold | Total Revenue ($) |
| :---------- | :------------- | :------------ | :---------------- | :------------- | :---------------- |
| 1           | Clothes        | 33            | 183.60            | 5,658          | 1,060,271.00      |
| 2           | Electronics    | 9             | 43.58             | 1,202          | 51,759.00         |
| 3           | Furniture      | 5             | 58.20             | 707            | 40,810.00         |
| 4           | Shoes          | 8             | 190.03            | 1,481          | 295,093.00        |
| 5           | Miscellaneous  | 5             | 53.33             | 836            | 44,435.00         |

### Price Segmentation KPI
Categorizes catalog distribution and generated revenue based on product price tiers.

| Price Segment | Product Count | Average Price ($) | Total Revenue ($) |
| :------------ | :------------ | :---------------- | :---------------- |
| Budget        | 12            | 10.58             | 23,408.00         |
| Mid-Range     | 41            | 63.12             | 404,404.00        |
| Premium       | 7             | 819.64            | 1,064,556.00      |

### Customer Value KPI (Top 5 Active Customers)
Tracks total orders, total spending, and average order value.

| User ID | Customer Name | Email | Role | Total Orders | Total Spent ($) | Avg Order Value ($) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Jhon | john@mail.com | customer | 84 | 1,573,142.00 | 18,727.88 |
| 3 | Admin | admin@mail.com | admin | 94 | 1,228,414.00 | 13,068.23 |
| 15 | AITS Test | aits_test@test.com | customer | 89 | 1,279,826.00 | 14,380.07 |
| 16 | hello | hello@gmail.com | customer | 107 | 1,388,962.00 | 12,980.95 |
| 18 | Oliver Henry Brooks | oliver860@gmail.com | customer | 107 | 720,152.00 | 6,730.39 |
