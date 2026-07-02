import requests
from sqlalchemy import text
import json
from src.config import API_URL
from src.db import engine

# API URL for users is derived by replacing "products" with "users"
API_USERS_URL = API_URL.replace("products", "users")

def extract_products():
    """
    Fetch raw products data from Plazi E-Commerce API and load it
    directly into bronze.raw_products as JSONB objects.
    """
    print(f"Starting ingestion of products from API: {API_URL}")
    
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        products = response.json()
    except Exception as e:
        print(f"Failed to fetch products from API: {e}")
        raise

    if not isinstance(products, list):
        raise ValueError(f"Expected a JSON list of products from API, got {type(products)}")

    print(f"Successfully fetched {len(products)} products from API.")

    query = text("""
        INSERT INTO bronze.raw_products (raw_data)
        VALUES (:raw_data)
    """)

    inserted_count = 0
    with engine.begin() as conn:
        for product in products:
            conn.execute(query, {"raw_data": json.dumps(product)})
            inserted_count += 1

    print(f"Bronze layer: Loaded {inserted_count} raw product records into 'bronze.raw_products'.")
    return inserted_count

def extract_users():
    """
    Fetch raw users data from Plazi E-Commerce API and load it
    directly into bronze.raw_users as JSONB objects.
    """
    print(f"Starting ingestion of users from API: {API_USERS_URL}")
    
    try:
        response = requests.get(API_USERS_URL, timeout=30)
        response.raise_for_status()
        users = response.json()
    except Exception as e:
        print(f"Failed to fetch users from API: {e}")
        raise

    if not isinstance(users, list):
        raise ValueError(f"Expected a JSON list of users from API, got {type(users)}")

    print(f"Successfully fetched {len(users)} users from API.")

    query = text("""
        INSERT INTO bronze.raw_users (raw_data)
        VALUES (:raw_data)
    """)

    inserted_count = 0
    with engine.begin() as conn:
        for user in users:
            conn.execute(query, {"raw_data": json.dumps(user)})
            inserted_count += 1

    print(f"Bronze layer: Loaded {inserted_count} raw user records into 'bronze.raw_users'.")
    return inserted_count

if __name__ == "__main__":
    from src.db import init_schemas
    init_schemas()
    
    # Execute DDL
    with open("sql/ddl_bronze.sql", "r") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
        
    extract_products()
    extract_users()
