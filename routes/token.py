# backend/routes/token.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from utils.auth import verify_password, create_access_token
from utils.dependencies import get_db
from models.init_db import Client, Employee

router = APIRouter()


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and provide JWT token with role.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.
        db (Session): Database session.

    Returns:
        dict: Contains access_token and token_type.

    Raises:
        HTTPException: If authentication fails.
    """
    # Attempt to find user in Client (Customer) table
    user = db.query(Client).filter(Client.email == form_data.username).first()
    role = "customer"
    if not user:
        # Attempt to find user in Employee table
        user = db.query(Employee).filter(Employee.email == form_data.username).first()
        role = "employee"
        if not user:
            # User not found in either table
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token with role
    access_token = create_access_token(data={"sub": user.id, "role": role})

    return {"access_token": access_token, "token_type": "bearer"}
