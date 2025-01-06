# Updated assist.py
import os
import logging
import time
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI

# Initialize the router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment variables.")
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Define the request and response schemas
class AssistRequest(BaseModel):
    query: str


class AssistResponse(BaseModel):
    answer: str


@router.post("/assist", response_model=AssistResponse)
def assist(request: AssistRequest):
    """
    Endpoint to handle AI assistance queries tailored for Lucid Motor.

    Args:
        request (AssistRequest): The user's query.

    Returns:
        AssistResponse: The AI-generated answer.

    Raises:
        HTTPException: If there's an error with the OpenAI API or
        processing the request.
    """
    try:
        start_time = time.time()
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty."
            )

        role = f"""
                You are an advanced AI assistant representing Lucid Motors, a premier brand
                known for redefining luxury electric vehicles. Your goal is to engage
                discerning clientele who value innovation, sustainability, and performance.

                Key areas of expertise include:
                - Articulating the luxurious features, cutting-edge technology, and bespoke
                  customization options of Lucid vehicles.
                - Providing tailored advice on maintenance schedules, optimal performance
                  upkeep, and addressing high-end client concerns.
                - Offering premium support on warranties, concierge services, and
                  seamless issue resolution.
                - Guiding prospective buyers through sales processes, highlighting unique
                  financing options, exclusive dealership experiences, and availability.

                When answering, exude sophistication, professionalism, and a client-centric
                approach. Anticipate the elevated expectations of Lucid Motors clientele by
                delivering responses that are thorough, aspirational, and actionable.

                User Query: {request.query}

                AI Response:
                """

        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": role or "You are helpful."},
                {"role": "user", "content": request.query},
            ],
            max_tokens=600,
            temperature=0.5,
        )
        end_time = time.time()
        logger.info(f"OpenAI API request completed in {end_time - start_time:.2f} seconds")

        answer = response.choices[0].message.content.strip()

        return AssistResponse(answer=answer)
    except Exception as e:
        logger.error("Error in /live-chat: %s", e)
        raise HTTPException(500, f"Live chat failed: {e}") from e
