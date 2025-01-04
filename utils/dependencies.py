"""
Utility functions for database dependencies.
"""

from models.init_db import SessionLocal


def get_db():
    """Provides a database session for requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
