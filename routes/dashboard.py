# backend/routes/dashboard.py

from fastapi import APIRouter, Depends
from utils.auth import get_current_user
from typing import List
from models.init_db import Appointment
from sqlalchemy.orm import Session
from utils.dependencies import get_db

router = APIRouter()


@router.get("/dashboard", response_model=List[Appointment])
def read_dashboard(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Retrieve dashboard data based on user role.
    """
    if user["role"] in ["employee", "superuser"]:
        appointments = db.query(Appointment).all()
        return appointments
    else:
        # Customers should not access dashboard
        return []
