import os
import logging
import time
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from cachetools import TTLCache
from fuzzywuzzy import process, fuzz
from dotenv import load_dotenv

load_dotenv()
print("DEBUG: OPENAI_API_KEY in FastAPI is:", os.environ.get("OPENAI_API_KEY"))

# Initialize the router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("No OPENAI_API_KEY found!")
else:
    logger.warning(
        f"Using OpenAI API key: {OPENAI_API_KEY[:6]}...{OPENAI_API_KEY[-4:]}"
    )

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment variables.")
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
RESPONSE_LENGTH = 300  # Maximum number of tokens in the response

# In-memory cache for OpenAI responses
cache = TTLCache(maxsize=100, ttl=3600)  # Cache up to 100 queries for 1 hour


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
    return (
        closest_match[0] if closest_match and closest_match[1] > 85 else None
    )


def stream_openai_response(query: str):
    """
    **Changed to a synchronous generator** that yields text chunks.
    Using `for chunk in ...` because the OpenAI client's `stream=True`
    returns a sync generator.
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

    # The create() call here returns a normal generator when stream=True
    # so we do a plain `for chunk in ...:` loop.
    stream = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": query},
        ],
        stream=True,
        temperature=0.4,
    )

    for chunk in stream:
        logger.debug(f"Stream chunk from OpenAI: {chunk}")
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

@router.post("/assist")
def assist(request: AssistRequest):
    """
    Endpoint to handle AI assistance queries tailored for Lucid Motors.
    Returns a StreamingResponse that streams text from OpenAI.
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
    logger.debug(f"Cached query: {cached_query}, is query in cache? {query in cache}")

    # If a fuzzy match exists or exact query is in cache, return cached response as a stream
    if cached_query or (query in cache):
        query_key = cached_query or query
        logger.info(f"Serving fuzzy cached response for query: {query_key}")

        def cached_gen():
            yield cache[query_key]

        return StreamingResponse(cached_gen(), media_type="text/plain")

    # Otherwise, stream from OpenAI and update the cache once the full response is accumulated
    try:
        def generate_and_cache(user_query: str):
            collected_chunks = []
            for chunk in stream_openai_response(user_query):
                collected_chunks.append(chunk)
                # Stream out each chunk to the client
                yield chunk

            # Once done streaming, cache the full answer
            final_answer = "".join(collected_chunks)
            cache[user_query] = final_answer

        end_time = time.time()
        logger.info(
            f"OpenAI streaming request started for query '{query}' at {start_time:.2f} "
            f"and ended at {end_time:.2f}"
        )

        return StreamingResponse(
            generate_and_cache(query),
            media_type="text/plain"
        )

    except Exception as e:
        logger.error("Error in /assist: %s", e)
        raise HTTPException(500, f"Live chat failed: {e}") from e
