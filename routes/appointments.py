import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from models.init_db import Appointment, Client
from models.schemas import AppointmentBase
from utils.auth import get_current_user
from utils.dependencies import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[AppointmentBase])
def get_appointments(
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
):
    """
    Retrieve all appointments from the database.

    Args:
        db (Session): Database session dependency.
        current_user (Client): The authenticated user.

    Returns:
        List[AppointmentBase]: A list of appointment details.

    Raises:
        HTTPException: If no appointments are found or if there is an error
        fetching appointments.
    """
    try:
        # If appointments are user-specific, filter by user
        appointments = (
            db.query(Appointment)
            .filter(Appointment.employee_id == current_user.id)
            .all()
        )

        if not appointments:
            logger.info(
                f"No appointments found for user ID {current_user.id}."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No appointments found."
            )

        logger.info(
            f"Retrieved {len(appointments)} appointments for user ID "
            f"{current_user.id}."
        )
        return appointments
    except HTTPException as e:
        logger.error("HTTP error fetching appointments: %s", e, exc_info=True)
        raise
    except Exception as e:
        logger.error(
            "Unexpected error fetching appointments: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments.",
        ) from e
