"""
Customer-related API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from models.init_db import Client

router = APIRouter()


@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    """
    Retrieve all customers from the database.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[Dict]: A list of dictionaries containing customer details.

    Raises:
        HTTPException: If no customers are found.
    """
    customers = db.query(Client).all()
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found.")
    return [
        {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}
        for c in customers
    ]
