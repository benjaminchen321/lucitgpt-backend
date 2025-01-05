import logging
from fastapi import APIRouter, Depends, HTTPException
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

    Returns:
        List[Dict]: A list of dictionaries containing appointment details.

    Raises:
        HTTPException: If no appointments are found or if there is an error
        fetching appointments.
    """
    try:
        appointments = db.query(Appointment).all()
        if not appointments:
            logger.info("No appointments found.")
            raise HTTPException(
                status_code=404, detail="No appointments found."
            )
        return [
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
        ]
    except Exception as e:
        logger.error("Error fetching appointments: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch appointments."
        ) from e
