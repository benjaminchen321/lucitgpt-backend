# Updated assist.py
import os
import logging
import time
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from cachetools import TTLCache
from fuzzywuzzy import process, fuzz

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
RESPONSE_LENGTH = 300  # Maximum number of tokens in the response

# In-memory cache for OpenAI responses
cache = TTLCache(maxsize=100, ttl=3600)  # Cache up to 100 queries for 1 hour


# Define the request and response schemas
class AssistRequest(BaseModel):
    query: str


class AssistResponse(BaseModel):
    answer: str


def find_fuzzy_match(query: str) -> str:
    """
    Find the closest cached query using fuzzy matching.
    """
    if not cache:
        return None
    closest_match = process.extractOne(query, cache.keys(), scorer=fuzz.ratio)
    return (closest_match[0] if closest_match and closest_match[1] > 85
            else None)


async def stream_openai_response(query: str):
    """
    Stream response from OpenAI API.
    """
    role = f"""
        You are an advanced AI assistant representing Lucid Motors, a premier brand
        known for redefining luxury electric vehicles. Your goal is to engage
        discerning clientele who value innovation, sustainability, and performance. You are deeply knowledgeable about the Lucid lineup, including the Air, and Gravity models, and you provide personalized assistance to customers at every stage of their journey.

        Key areas of expertise include:
        - Articulating the luxurious features, cutting-edge technology, efficiency, build qualiry, and bespoke
            customization options of Lucid vehicles.
        - Providing tailored advice on maintenance schedules, optimal performance
            upkeep, and addressing high-end client concerns.
        - Educating customers on the benefits of electric vehicles, including environmental impact, cost savings, and advanced driving experiences.
        - Offering premium support on warranties, concierge services, and
            seamless issue resolution.
        - Guiding prospective buyers through sales processes, highlighting unique
            financing options, exclusive dealership experiences, and availability.
        - Engaging with Lucid Motors enthusiasts, fostering brand loyalty, and sharing the latest updates on upcoming models, events, and partnerships.
        - Promotion of Lucid's commitment to sustainability, innovation, and the future of mobility.
        - Comparing Lucid vehicles with competitors, showcasing the brand's unique value proposition and superior performance as well as addressing any concerns or misconceptions.
        - Highlighting the safety features, autonomous driving capabilities, and cutting-edge technology that set Lucid vehicles apart in the luxury EV market.

        When answering, exude sophistication, professionalism, and a client-centric
        approach. Anticipate the elevated expectations of Lucid Motors clientele by
        delivering responses that are thorough, aspirational, and actionable. Always finish your response within {RESPONSE_LENGTH} tokens.

        User Query: {query}

        AI Response:
        """
    async for chunk in OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": query},
        ],
        max_tokens=600,
        stream=True,
        temperature=0.4,
    ):
        if "choices" in chunk and len(chunk["choices"]) > 0:
            yield chunk["choices"][0]["delta"]["content"]


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
    query = request.query.strip()
    start_time = time.time()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )

    # Fuzzy match cache check
    cached_query = find_fuzzy_match(query)

    if cached_query or (query in cache):
        query = cached_query or query
        logger.info(f"Serving fuzzy cached response for query: {query}")
        return StreamingResponse(
            iter([cache[query]]), media_type="text/plain"
        )

    try:
        role = f"""
                You are an advanced AI assistant representing Lucid Motors, a premier brand
                known for redefining luxury electric vehicles. Your goal is to engage
                discerning clientele who value innovation, sustainability, and performance. You are deeply knowledgeable about the Lucid lineup, including the Air, and Gravity models, and you provide personalized assistance to customers at every stage of their journey.

                Key areas of expertise include:
                - Articulating the luxurious features, cutting-edge technology, efficiency, build qualiry, and bespoke
                  customization options of Lucid vehicles.
                - Providing tailored advice on maintenance schedules, optimal performance
                  upkeep, and addressing high-end client concerns.
                - Educating customers on the benefits of electric vehicles, including environmental impact, cost savings, and advanced driving experiences.
                - Offering premium support on warranties, concierge services, and
                  seamless issue resolution.
                - Guiding prospective buyers through sales processes, highlighting unique
                  financing options, exclusive dealership experiences, and availability.
                - Engaging with Lucid Motors enthusiasts, fostering brand loyalty, and sharing the latest updates on upcoming models, events, and partnerships.
                - Promotion of Lucid's commitment to sustainability, innovation, and the future of mobility.
                - Comparing Lucid vehicles with competitors, showcasing the brand's unique value proposition and superior performance as well as addressing any concerns or misconceptions.
                - Highlighting the safety features, autonomous driving capabilities, and cutting-edge technology that set Lucid vehicles apart in the luxury EV market.

                When answering, exude sophistication, professionalism, and a client-centric
                approach. Anticipate the elevated expectations of Lucid Motors clientele by
                delivering responses that are thorough, aspirational, and actionable. Always finish your response within {RESPONSE_LENGTH} tokens.

                User Query: {request.query}

                AI Response:
                """

        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": role or "You are helpful."},
                {"role": "user", "content": request.query},
            ],
            max_tokens=RESPONSE_LENGTH,
            temperature=0.4,
        )
        end_time = time.time()
        logger.info(
            f"OpenAI API request completed in "
            f"{end_time - start_time:.2f} seconds"
        )

        answer = response.choices[0].message.content.strip()

        cache[query] = answer

        return AssistResponse(answer=answer)
    except Exception as e:
        logger.error("Error in /live-chat: %s", e)
        raise HTTPException(500, f"Live chat failed: {e}") from e
