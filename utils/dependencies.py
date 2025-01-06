# backend/utils/dependencies.py
from models.init_db import SessionLocal
from dotenv import load_dotenv

# Load environment variables from .env.prod
load_dotenv(dotenv_path="../.env.prod")  # Adjust the path if necessary


def get_db():
    """Provides a database session for requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
