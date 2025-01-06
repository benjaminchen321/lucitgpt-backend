import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from models.init_db import Client, Vehicle, Appointment
from models.schemas import (
    CustomerResponse,
    CustomerDetailResponse,
    VehicleBase,
    AppointmentBase,
)
from utils.dependencies import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    """
    Retrieve all customers.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[CustomerResponse]: A list of customer details.

    Raises:
        HTTPException: If no customers are found.
    """
    try:
        customers = db.query(Client).all()
        if not customers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No customers found."
            )
        return [
            CustomerResponse.model_validate(customer)
            for customer in customers
        ]
    except Exception as e:
        logger.error(
            f"Unexpected error fetching customers: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customers."
        )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_details(customer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a specific customer.

    Args:
        customer_id (int): ID of the customer.
        db (Session): Database session.

    Returns:
        CustomerDetailResponse: Customer details including vehicles
        and appointments.

    Raises:
        HTTPException: If customer not found.
    """
    try:
        customer = db.query(Client).filter(Client.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found."
            )

        vehicles = (
            db.query(Vehicle)
            .filter(Vehicle.client_id == customer_id)
            .all()
        )
        vins = [v.vin for v in vehicles]
        appointments = (
            db.query(Appointment)
            .filter(Appointment.vin.in_(vins))
            .all()
        )

        return CustomerDetailResponse(
            customer=CustomerResponse.model_validate(customer),
            vehicles=[
                VehicleBase.model_validate(vehicle)
                for vehicle in vehicles
            ],
            appointments=[
                AppointmentBase.model_validate(appointment)
                for appointment in appointments
            ],
        )
    except Exception as e:
        logger.error(
            f"Unexpected error fetching customer details: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer details."
        )
