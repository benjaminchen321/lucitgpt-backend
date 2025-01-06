import datetime
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import asc
from sqlalchemy.orm import Session
from models.init_db import Appointment
from models.schemas import AppointmentBase
from utils.dependencies import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[AppointmentBase])
def get_appointments(db: Session = Depends(get_db)):
    """
    Retrieve all appointments from the database.

    Args:
        db (Session): Database session dependency.

    Returns:
        list: A list of appointment details.
    """
    try:
        now = datetime.datetime.now()
        appointments = (
            db.query(Appointment)
            .filter(Appointment.date >= now)
            .order_by(asc(Appointment.date))
            .all()
        )
        if not appointments:
            logger.info("No appointments found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No appointments found."
            )
        return [
            AppointmentBase.model_validate(appointment)
            for appointment in appointments
        ]
    except Exception as e:
        logger.error(
            f"Unexpected error fetching appointments: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments."
        )
