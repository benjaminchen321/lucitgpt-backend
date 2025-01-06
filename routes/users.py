# backend/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from models.schemas import UserResponse
from models.init_db import Client
from utils.auth import get_current_user

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: Client = Depends(get_current_user)):
    """
    Retrieve the current authenticated user's information.

    Args:
        current_user (Client): The authenticated user retrieved from the token.

    Returns:
        UserResponse: The current user's data.

    Raises:
        HTTPException: If the user is not found (shouldn't occur if token is
        valid).
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return current_user
