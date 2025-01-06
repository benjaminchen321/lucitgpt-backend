"""
Customer-related API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from utils.dependencies import get_db
from models.init_db import Client, Vehicle, Appointment
from models.schemas import (
    CustomerResponse,
    CustomerDetailResponse,
    VehicleBase,
    AppointmentBase,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db), current_user: Client = Depends(get_current_user)
):
    """
    Retrieve all customers associated with the current user.

    Args:
        db (Session): Database session dependency.
        current_user (Client): The authenticated user.

    Returns:
        List[CustomerResponse]: A list of customer details.

    Raises:
        HTTPException: If no customers are found.
    """
    try:
        # Assuming that customers are associated with users, modify the query
        # accordingly. For example, if each customer has a 'user_id' field.
        customers = db.query(Client).filter(Client.id == current_user["id"]).all()

        if not customers:
            logger.info(f"No customers found for user ID {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No customers found."
            )

        logger.info(
            f"Retrieved {len(customers)} customers for user ID "
            f"{current_user['id']}."
        )
        return customers
    except HTTPException as e:
        logger.error(f"HTTP error fetching customers: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching customers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customers.",
        ) from e


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_details(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),
):
    """
    Retrieve detailed information for a specific customer associated
    with the current user.

    Args:
        customer_id (int): ID of the customer.
        db (Session): Database session.
        current_user (Client): The authenticated user.

    Returns:
        CustomerDetailResponse: Customer details including vehicles
        and appointments.

    Raises:
        HTTPException: If customer not found or not associated with the
        current user.
    """
    try:
        customer = (
            db.query(Client)
            .filter(Client.id == customer_id, Client.id == current_user["id"])
            .first()
        )
        if not customer:
            logger.info(
                f"Customer ID {customer_id} not found for user ID "
                f"{current_user.id}."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found."
            )

        vehicles = db.query(Vehicle).filter(Vehicle.client_id == customer_id).all()
        vins = [v.vin for v in vehicles]
        appointments = db.query(Appointment).filter(Appointment.vin.in_(vins)).all()

        logger.info(f"Retrieved details for customer ID {customer_id}.")

        return CustomerDetailResponse(
            customer=customer,
            vehicles=[VehicleBase.from_orm(vehicle) for vehicle in vehicles],
            appointments=[
                AppointmentBase.from_orm(appointment) for appointment in appointments
            ],
        )
    except HTTPException as e:
        logger.error(f"HTTP error fetching customer details: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching customer details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer details.",
        ) from e
