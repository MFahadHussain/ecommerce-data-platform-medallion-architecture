import time
from sqlalchemy import text
from src.db import engine, init_schemas
from src.extract import extract_products, extract_users
from src.transform_silver import transform_silver
from src.transform_gold import transform_gold

def execute_ddl(file_path):
    """Read and execute SQL statements from a file."""
    print(f"Applying DDL from: {file_path}")
    with open(file_path, "r") as f:
        ddl = f.read()
    
    with engine.begin() as conn:
        conn.execute(text(ddl))

def main():
    start_time = time.time()
    print("=" * 60)
    print("STARTING E-COMMERCE MEDALLION ETL PIPELINE (WITH USERS)")
    print("=" * 60)

    # Step 1: Initialize Database Schemas
    print("\n--- STEP 1: INITIALIZING SCHEMAS ---")
    init_schemas()

    # Step 2: Initialize Tables using DDL
    print("\n--- STEP 2: CREATING TABLES ---")
    try:
        execute_ddl("sql/ddl_bronze.sql")
        execute_ddl("sql/ddl_silver.sql")
        execute_ddl("sql/ddl_gold.sql")
        print("All DDL schemas/tables successfully created or validated.")
    except Exception as e:
        print(f"Error executing DDL files: {e}")
        return

    # Step 3: Extract from API to Bronze (Raw)
    print("\n--- STEP 3: EXTRACTING API DATA (BRONZE) ---")
    try:
        extract_products()
        extract_users()
    except Exception as e:
        print(f"Pipeline extraction failed: {e}")
        return

    # Step 4: Transform & Clean (Silver)
    print("\n--- STEP 4: CLEANING & STRUCTURING DATA (SILVER) ---")
    try:
        transform_silver()
    except Exception as e:
        print(f"Pipeline silver transformation failed: {e}")
        return

    # Step 5: Business KPIs & Aggregations (Gold)
    print("\n--- STEP 5: CALCULATING BUSINESS KPIS (GOLD) ---")
    try:
        transform_gold()
    except Exception as e:
        print(f"Pipeline gold transformation failed: {e}")
        return

    duration = time.time() - start_time
    print("\n" + "=" * 60)
    print("ETL PIPELINE EXECUTED SUCCESSFULY")
    print(f"Total execution time: {duration:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    main()
