-- DDL for Silver Layer (Relational & Cleaned)

CREATE TABLE IF NOT EXISTS silver.categories (
    category_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.products (
    product_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    description TEXT,
    category_id INT REFERENCES silver.categories(category_id),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.product_images (
    image_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES silver.products(product_id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.users (
    user_id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.sales_transactions (
    transaction_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES silver.products(product_id),
    customer_id INT REFERENCES silver.users(user_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
