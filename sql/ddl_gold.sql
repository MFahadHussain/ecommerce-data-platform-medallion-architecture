-- DDL for Gold Layer (Business KPIs)

CREATE TABLE IF NOT EXISTS gold.kpi_category_performance (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    product_count INT NOT NULL,
    average_price NUMERIC(12, 2) NOT NULL,
    total_quantity_sold INT NOT NULL,
    total_revenue NUMERIC(15, 2) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.kpi_price_segmentation (
    price_segment VARCHAR(50) PRIMARY KEY,
    product_count INT NOT NULL,
    average_price NUMERIC(12, 2) NOT NULL,
    total_revenue NUMERIC(15, 2) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.kpi_user_sales_performance (
    user_id INT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    total_orders INT NOT NULL,
    total_spent NUMERIC(15, 2) NOT NULL,
    average_order_value NUMERIC(12, 2) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
