# backend/routes/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.init_db import Client, Employee
from utils.auth import get_current_user
from utils.dependencies import get_db

router = APIRouter()


@router.get("/users/me")
def read_current_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Retrieve current authenticated user information.
    """
    if user["role"] == "customer":
        customer = db.query(Client).filter(Client.id == user["id"]).first()
        if customer:
            return {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "role": user["role"],
            }
        else:
            employee = (
                db.query(Employee)
                .filter(Employee.id == user["id"])
                .first()
            )
            if employee:
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "role": user["role"],
                }
            else:
                return {"error": "Employee not found"}
    else:
        return {}
