import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime, timedelta
import json
import random
from src.db import engine

def clean_datetime(dt_str):
    """Parse API datetime string to datetime object, or return None."""
    if pd.isna(dt_str) or not dt_str:
        return None
    try:
        return pd.to_datetime(dt_str)
    except Exception:
        return None

def transform_silver():
    """
    Reads raw products and users from Bronze layer, cleans, deduplicates,
    normalizes, and loads into silver relational tables.
    Generates simulated transactions with customer references.
    """
    print("Starting Silver Layer Transformation...")

    # ==========================================
    # 1. PROCESS PRODUCTS & CATEGORIES
    # ==========================================
    prod_raw_df = pd.read_sql_query("SELECT id as bronze_id, raw_data FROM bronze.raw_products", con=engine)
    
    if prod_raw_df.empty:
        print("Bronze products layer is empty. Please run extract first.")
        return

    print(f"Loaded {len(prod_raw_df)} raw product records from Bronze.")

    categories_list = []
    products_list = []
    images_list = []

    for idx, row in prod_raw_df.iterrows():
        try:
            prod = row['raw_data']
            if isinstance(prod, str):
                prod = json.loads(prod)
            
            if 'id' not in prod or 'title' not in prod:
                continue

            # Extract category
            cat = prod.get('category', {})
            cat_id = cat.get('id')
            if cat_id is not None:
                categories_list.append({
                    'category_id': int(cat_id),
                    'name': cat.get('name', 'Unknown'),
                    'image_url': cat.get('image', None),
                    'created_at': clean_datetime(cat.get('creationAt')),
                    'updated_at': clean_datetime(cat.get('updatedAt'))
                })

            # Extract product
            products_list.append({
                'product_id': int(prod['id']),
                'title': prod.get('title', 'Unknown Product'),
                'price': float(prod.get('price', 0.0)),
                'description': prod.get('description', ''),
                'category_id': int(cat_id) if cat_id is not None else None,
                'created_at': clean_datetime(prod.get('creationAt')),
                'updated_at': clean_datetime(prod.get('updatedAt'))
            })

            # Extract product images
            images = prod.get('images', [])
            if isinstance(images, list):
                for img_url in images:
                    if isinstance(img_url, str):
                        img_clean = img_url.strip('[]"\' ')
                        if img_clean:
                            images_list.append({
                                'product_id': int(prod['id']),
                                'image_url': img_clean
                            })
        except Exception as e:
            print(f"Error parsing product row {row['bronze_id']}: {e}")
            continue

    # Convert products & categories to DataFrames
    df_cat = pd.DataFrame(categories_list)
    df_prod = pd.DataFrame(products_list)
    df_images = pd.DataFrame(images_list)

    # Clean & Deduplicate Categories
    if not df_cat.empty:
        df_cat = df_cat.sort_values(by=['category_id', 'updated_at'], ascending=[True, False])
        df_cat = df_cat.drop_duplicates(subset=['category_id'], keep='first')
        df_cat['name'] = df_cat['name'].fillna('Unknown Category')
    else:
        df_cat = pd.DataFrame(columns=['category_id', 'name', 'image_url', 'created_at', 'updated_at'])

    # Clean & Deduplicate Products
    if not df_prod.empty:
        df_prod = df_prod.sort_values(by=['product_id', 'updated_at'], ascending=[True, False])
        df_prod = df_prod.drop_duplicates(subset=['product_id'], keep='first')
        df_prod['price'] = df_prod['price'].apply(lambda x: max(0.0, float(x)))
        df_prod['title'] = df_prod['title'].fillna('Unknown Product').str.strip()
        df_prod['description'] = df_prod['description'].fillna('').str.strip()
    else:
        df_prod = pd.DataFrame(columns=['product_id', 'title', 'price', 'description', 'category_id', 'created_at', 'updated_at'])

    # Clean Product Images
    if not df_images.empty:
        df_images = df_images.drop_duplicates()
        df_images = df_images[df_images['product_id'].isin(df_prod['product_id'])]
    else:
        df_images = pd.DataFrame(columns=['product_id', 'image_url'])

    # ==========================================
    # 2. PROCESS USERS
    # ==========================================
    user_raw_df = pd.read_sql_query("SELECT id as bronze_id, raw_data FROM bronze.raw_users", con=engine)
    
    if user_raw_df.empty:
        print("Bronze users layer is empty. Please run extract first.")
        return

    print(f"Loaded {len(user_raw_df)} raw user records from Bronze.")

    users_list = []
    for idx, row in user_raw_df.iterrows():
        try:
            usr = row['raw_data']
            if isinstance(usr, str):
                usr = json.loads(usr)
            
            if 'id' not in usr or 'email' not in usr:
                continue

            users_list.append({
                'user_id': int(usr['id']),
                'email': usr.get('email', ''),
                'name': usr.get('name', 'Unknown User'),
                'role': usr.get('role', 'customer'),
                'avatar_url': usr.get('avatar', ''),
                'created_at': clean_datetime(usr.get('creationAt')),
                'updated_at': clean_datetime(usr.get('updatedAt'))
            })
        except Exception as e:
            print(f"Error parsing user row {row['bronze_id']}: {e}")
            continue

    df_users = pd.DataFrame(users_list)

    # Clean & Deduplicate Users
    if not df_users.empty:
        df_users = df_users.sort_values(by=['user_id', 'updated_at'], ascending=[True, False])
        df_users = df_users.drop_duplicates(subset=['user_id'], keep='first')
        df_users['email'] = df_users['email'].fillna('').str.strip()
        df_users['name'] = df_users['name'].fillna('Unknown User').str.strip()
    else:
        df_users = pd.DataFrame(columns=['user_id', 'email', 'name', 'role', 'avatar_url', 'created_at', 'updated_at'])

    # ==========================================
    # 3. GENERATE SIMULATED TRANSACTIONS
    # ==========================================
    transactions_list = []
    random.seed(42)

    if not df_prod.empty and not df_users.empty:
        current_time = datetime.now()
        user_ids = df_users['user_id'].tolist()
        
        for idx, row in df_prod.iterrows():
            prod_id = row['product_id']
            price = row['price']
            
            if price <= 0:
                continue

            # Simulate between 10 and 100 sales per product
            num_sales = random.randint(10, 100)
            for _ in range(num_sales):
                qty = random.randint(1, 5)
                # Assign to random customer
                cust_id = random.choice(user_ids)
                days_ago = random.uniform(0, 30)
                tx_date = current_time - timedelta(days=days_ago)
                
                transactions_list.append({
                    'product_id': int(prod_id),
                    'customer_id': int(cust_id),
                    'quantity': qty,
                    'unit_price': float(price),
                    'transaction_date': tx_date
                })

    df_sales = pd.DataFrame(transactions_list)

    # ==========================================
    # 4. DATABASE WRITE PROCESS
    # ==========================================
    with engine.begin() as conn:
        print("Truncating old Silver tables...")
        conn.execute(text("TRUNCATE TABLE silver.sales_transactions, silver.product_images, silver.products, silver.users, silver.categories CASCADE;"))

        print("Writing Categories...")
        df_cat.to_sql('categories', con=conn, schema='silver', if_exists='append', index=False)

        print("Writing Users...")
        df_users.to_sql('users', con=conn, schema='silver', if_exists='append', index=False)

        print("Writing Products...")
        df_prod.to_sql('products', con=conn, schema='silver', if_exists='append', index=False)

        print("Writing Product Images...")
        if not df_images.empty:
            df_images.to_sql('product_images', con=conn, schema='silver', if_exists='append', index=False)

        print("Writing Sales Transactions...")
        if not df_sales.empty:
            df_sales.to_sql('sales_transactions', con=conn, schema='silver', if_exists='append', index=False)

    print(f"Silver layer: Loaded {len(df_cat)} categories, {len(df_users)} users, {len(df_prod)} products, {len(df_images)} images, and {len(df_sales)} sales transactions.")

if __name__ == "__main__":
    from src.db import init_schemas
    init_schemas()
    with open("sql/ddl_silver.sql", "r") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
    transform_silver()
