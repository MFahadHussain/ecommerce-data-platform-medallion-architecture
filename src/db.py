from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_schemas():
    """Ensure medallion architecture schemas exist in the database."""
    schemas = ["bronze", "silver", "gold"]
    with engine.begin() as conn:
        for schema in schemas:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
    print("Database schemas (bronze, silver, gold) checked/created successfully.")
