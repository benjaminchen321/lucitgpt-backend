# Updated employees.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from models.init_db import Employee

router = APIRouter()


@router.get("/employees", response_model=list)
def read_employees(db: Session = Depends(get_db)):
    """
    Retrieve all employees.

    Args:
        db (Session): Database session.

    Returns:
        list: List of employees.
    """
    employees = db.query(Employee).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found.")
    return employees
