"""
Main module for the LucidGPT backend application.
"""

import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.appointments import router as appointments_router
from routes.customers import router as customers_router
from routes.token import router as token_router  # Import the token router

load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Configuration
origins = ["*"]  # Use "*" for testing; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(customers_router, prefix="/customers", tags=["Customers"])
app.include_router(
    appointments_router,
    prefix="/appointments",
    tags=["Appointments"]
)
app.include_router(token_router, prefix="", tags=["Authentication"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
