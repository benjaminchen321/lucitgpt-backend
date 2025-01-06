# backend/routes/assist.py

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import openai
from utils.auth import get_current_user
from utils.dependencies import get_db
from models.init_db import Client

# Initialize the router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment variables.")
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

openai.api_key = OPENAI_API_KEY


# Define the request and response schemas
class AssistRequest(BaseModel):
    query: str


class AssistResponse(BaseModel):
    answer: str


@router.post("/assist", response_model=AssistResponse)
def assist(
    request: AssistRequest,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
):
    """
    Endpoint to handle AI assistance queries.

    Args:
        request (AssistRequest): The user's query.
        db (Session): Database session.
        current_user (Client): The authenticated user.

    Returns:
        AssistResponse: The AI-generated answer.

    Raises:
        HTTPException: If there's an error with the OpenAI API or
        processing the request.
    """
    try:
        # Sanitize and validate the query
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty."
            )

        # Log the incoming query
        logger.info(
            f"User ID {current_user.id} submitted query: {request.query}"
        )

        # Call OpenAI API
        response = openai.Completion.create(
            engine="gpt-4o-mini",
            prompt=request.query,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        answer = response.choices[0].text.strip()

        # Log the response
        logger.info(f"AI response for user ID {current_user.id}: {answer}")

        return AssistResponse(answer=answer)
    except HTTPException:
        # Re-raise HTTPExceptions to be handled by FastAPI
        raise
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error communicating with AI service."
        )
    except Exception as e:
        logger.error(f"Unexpected error in /assist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
