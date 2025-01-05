"""
Customer-related API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from utils.dependencies import get_db
from models.init_db import Client, Vehicle, Appointment
from models.schemas import CustomerResponse, CustomerDetailResponse

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
):
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


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_details(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
):
    """
    Retrieve detailed information for a specific customer.

    Args:
        customer_id (int): ID of the customer.
        db (Session): Database session.

    Returns:
        Dict: Customer details including vehicles and appointments.

    Raises:
        HTTPException: If customer not found.
    """
    customer = db.query(Client).filter(Client.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    vehicles = db.query(Vehicle).filter(Vehicle.client_id == customer_id).all()
    appointments = db.query(Appointment).filter(
        Appointment.vin.in_([v.vin for v in vehicles])
    ).all()

    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
        },
        "vehicles": [
            {
                "vin": vehicle.vin,
                "model": vehicle.model,
                "year": vehicle.year,
                "mileage": vehicle.mileage,
                "warranty_exp": vehicle.warranty_exp,
                "service_plan": vehicle.service_plan,
            }
            for vehicle in vehicles
        ],
        "appointments": [
            {
                "id": appt.id,
                "vin": appt.vin,
                "date": appt.date,
                "time": appt.time,
                "service_type": appt.service_type,
                "status": appt.status,
                "employee_id": appt.employee_id,
            }
            for appt in appointments
        ],
    }
