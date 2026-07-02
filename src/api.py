from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from pathlib import Path
from src.db import engine

app = FastAPI(title="E-Commerce Medallion Analytics API", version="1.0.0")

# Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Expose static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    """Serve the main dashboard page."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_path)

@app.get("/api/kpis")
def get_kpis():
    """Retrieve global platform KPIs from Gold layer."""
    query = """
        SELECT 
            SUM(total_revenue) as total_revenue,
            SUM(total_quantity_sold) as total_units_sold,
            SUM(product_count) as total_products,
            COALESCE(AVG(average_price), 0.0) as average_product_price
        FROM gold.kpi_category_performance;
    """
    
    query_orders = """
        SELECT 
            SUM(total_orders) as total_orders
        FROM gold.kpi_user_sales_performance;
    """

    try:
        with engine.connect() as conn:
            kpi_res = conn.execute(text(query)).mappings().first()
            orders_res = conn.execute(text(query_orders)).mappings().first()
            
            total_rev = float(kpi_res["total_revenue"] or 0)
            total_ord = int(orders_res["total_orders"] or 0)
            
            aov = total_rev / total_ord if total_ord > 0 else 0.0
            
            return {
                "total_revenue": total_rev,
                "total_units_sold": int(kpi_res["total_units_sold"] or 0),
                "total_products": int(kpi_res["total_products"] or 0),
                "average_product_price": float(kpi_res["average_product_price"] or 0),
                "total_orders": total_ord,
                "average_order_value": aov
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/categories")
def get_categories_kpi():
    """Retrieve category performance metrics."""
    query = """
        SELECT category_id, category_name, product_count, average_price, total_quantity_sold, total_revenue
        FROM gold.kpi_category_performance
        ORDER BY total_revenue DESC;
    """
    try:
        with engine.connect() as conn:
            res = conn.execute(text(query)).mappings().all()
            return [dict(row) for row in res]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/price-segments")
def get_price_segment_kpi():
    """Retrieve pricing segmentation metrics."""
    query = """
        SELECT price_segment, product_count, average_price, total_revenue
        FROM gold.kpi_price_segmentation
        ORDER BY total_revenue DESC;
    """
    try:
        with engine.connect() as conn:
            res = conn.execute(text(query)).mappings().all()
            return [dict(row) for row in res]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/top-customers")
def get_top_customers():
    """Retrieve top 10 customers based on total spending."""
    query = """
        SELECT user_id, customer_name, email, role, total_orders, total_spent, average_order_value
        FROM gold.kpi_user_sales_performance
        ORDER BY total_spent DESC
        LIMIT 10;
    """
    try:
        with engine.connect() as conn:
            res = conn.execute(text(query)).mappings().all()
            return [dict(row) for row in res]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
