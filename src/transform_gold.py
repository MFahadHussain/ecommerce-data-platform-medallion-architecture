from sqlalchemy import text
from src.db import engine

def transform_gold():
    """
    Executes SQL queries to compute business KPIs from Silver tables
    and writes results to Gold analytical tables.
    """
    print("Starting Gold Layer Transformation...")

    # Query 1: Category Performance KPI
    query_category_perf = """
        INSERT INTO gold.kpi_category_performance (
            category_id, category_name, product_count, average_price, total_quantity_sold, total_revenue, last_updated
        )
        SELECT 
            c.category_id,
            c.name AS category_name,
            COUNT(DISTINCT p.product_id) AS product_count,
            COALESCE(AVG(p.price), 0.0) AS average_price,
            COALESCE(SUM(t.quantity), 0)::INTEGER AS total_quantity_sold,
            COALESCE(SUM(t.quantity * t.unit_price), 0.0) AS total_revenue,
            CURRENT_TIMESTAMP AS last_updated
        FROM silver.categories c
        LEFT JOIN silver.products p ON c.category_id = p.category_id
        LEFT JOIN silver.sales_transactions t ON p.product_id = t.product_id
        GROUP BY c.category_id, c.name
        ON CONFLICT (category_id) DO UPDATE SET
            category_name = EXCLUDED.category_name,
            product_count = EXCLUDED.product_count,
            average_price = EXCLUDED.average_price,
            total_quantity_sold = EXCLUDED.total_quantity_sold,
            total_revenue = EXCLUDED.total_revenue,
            last_updated = EXCLUDED.last_updated;
    """

    # Query 2: Price Segmentation KPI
    query_price_segment = """
        INSERT INTO gold.kpi_price_segmentation (
            price_segment, product_count, average_price, total_revenue, last_updated
        )
        WITH segmented_products AS (
            SELECT 
                p.product_id,
                p.price,
                CASE 
                    WHEN p.price <= 20.00 THEN 'Budget'
                    WHEN p.price > 20.00 AND p.price <= 100.00 THEN 'Mid-Range'
                    ELSE 'Premium'
                END AS price_segment
            FROM silver.products p
        ),
        segmented_sales AS (
            SELECT 
                sp.price_segment,
                COUNT(DISTINCT sp.product_id)::INTEGER AS product_count,
                COALESCE(AVG(sp.price), 0.0) AS average_price,
                COALESCE(SUM(t.quantity * t.unit_price), 0.0) AS total_revenue
            FROM segmented_products sp
            LEFT JOIN silver.sales_transactions t ON sp.product_id = t.product_id
            GROUP BY sp.price_segment
        )
        SELECT 
            price_segment,
            product_count,
            average_price,
            total_revenue,
            CURRENT_TIMESTAMP AS last_updated
        FROM segmented_sales
        ON CONFLICT (price_segment) DO UPDATE SET
            product_count = EXCLUDED.product_count,
            average_price = EXCLUDED.average_price,
            total_revenue = EXCLUDED.total_revenue,
            last_updated = EXCLUDED.last_updated;
    """

    # Query 3: Customer Value KPI (User Sales Performance)
    query_user_sales_perf = """
        INSERT INTO gold.kpi_user_sales_performance (
            user_id, customer_name, email, role, total_orders, total_spent, average_order_value, last_updated
        )
        SELECT 
            u.user_id,
            u.name AS customer_name,
            u.email,
            u.role,
            COUNT(DISTINCT t.transaction_id)::INTEGER AS total_orders,
            COALESCE(SUM(t.quantity * t.unit_price), 0.0) AS total_spent,
            COALESCE(AVG(t.quantity * t.unit_price), 0.0) AS average_order_value,
            CURRENT_TIMESTAMP AS last_updated
        FROM silver.users u
        INNER JOIN silver.sales_transactions t ON u.user_id = t.customer_id
        GROUP BY u.user_id, u.name, u.email, u.role
        ON CONFLICT (user_id) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            email = EXCLUDED.email,
            role = EXCLUDED.role,
            total_orders = EXCLUDED.total_orders,
            total_spent = EXCLUDED.total_spent,
            average_order_value = EXCLUDED.average_order_value,
            last_updated = EXCLUDED.last_updated;
    """

    with engine.begin() as conn:
        print("Clearing Gold Layer tables...")
        conn.execute(text("TRUNCATE TABLE gold.kpi_category_performance, gold.kpi_price_segmentation, gold.kpi_user_sales_performance;"))
        
        print("Calculating Category Performance KPIs...")
        conn.execute(text(query_category_perf))

        print("Calculating Price Segmentation KPIs...")
        conn.execute(text(query_price_segment))

        print("Calculating Customer Value KPIs...")
        conn.execute(text(query_user_sales_perf))

    print("Gold layer: Aggregated KPIs computed and written to performance tables.")

if __name__ == "__main__":
    from src.db import init_schemas
    init_schemas()
    with open("sql/ddl_gold.sql", "r") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
    transform_gold()
