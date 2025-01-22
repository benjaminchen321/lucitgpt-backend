# Updated main.py
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.appointments import router as appointments_router
from routes.customers import router as customers_router
from routes.assist import router as assist_router
from routes.employees import router as employees_router

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Middleware to log raw incoming requests
@app.middleware("http")
async def log_request(request: Request, call_next):
    body = await request.body()
    logger.info(
        f"Incoming Request: {request.method} {request.url} "
        f"Body: {body.decode('utf-8')}"
    )
    response = await call_next(request)
    return response


# CORS Configuration
origins = ["https://localhost:3000", "https://lucidgpt.netlify.app"]
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
app.include_router(assist_router, prefix="", tags=["Assistance"])
app.include_router(employees_router, prefix="/employees", tags=["Employees"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check accessed.")
    return {"status": "ok"}
