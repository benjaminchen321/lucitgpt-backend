# backend/routes/employees.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from utils.dependencies import get_db
from models.init_db import Employee
from models.schemas import EmployeeResponse

router = APIRouter()


@router.get("/employees/me", response_model=EmployeeResponse)
def read_employee_me(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Retrieve current authenticated employee's details.

    Args:
        current_user (dict): Contains user ID and role.
        db (Session): Database session.

    Returns:
        EmployeeResponse: Employee details.

    Raises:
        HTTPException: If user is not an employee or not found.
    """
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Not an employee.",
        )

    employee = db.query(Employee).filter(Employee.id == current_user["id"]).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return EmployeeResponse(
        id=employee.id,
        name=employee.name,
        email=employee.email,
        phone=employee.phone,
        profile_pic_url=employee.profile_pic_url,
    )
