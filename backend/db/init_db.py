"""
Database initialization script
Run this to create all tables
"""
from backend.models import Base
from backend.db.session import engine
from backend.config import settings


def init_db():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Success: Database tables created successfully!")
        print(f"Database URL: {settings.DATABASE_URL}")
    except Exception as e:
        print(f"Error: Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_db()
