import os
from fastapi.middleware.cors import CORSMiddleware
import time

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from openai import OpenAI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from init_db import Client, Vehicle, ServiceHistory, Appointment
import sentry_sdk

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# SENTRY
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
app.add_middleware(SentryAsgiMiddleware)

# OpenAI Client Initialization
OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# SQLAlchemy Base
Base = declarative_base()

# CORS
origins = ["*"]  # Allow all origins for public access; restrict if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL Connection
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Adjust the DATABASE_URL for psycopg2
if DATABASE_URL.startswith("postgresql+psycopg2"):
    DATABASE_URL = DATABASE_URL.replace("+psycopg2", "")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    raise RuntimeError(f"Failed to connect to the database: {e}")

# Database connection for SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Request Model for Chat Input
class ChatRequest(BaseModel):
    query: str
    user_id: str

@app.post("/chat")
async def chat_with_lucidgpt(request: ChatRequest):
    try:
        start_time = time.time()
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are LucidGPT, the premier virtual assistant with comprehensive knowledge about Lucid's vehicles, services, and policies. Communicate with a commanding and refined tone, articulating responses elegantly to reflect Lucid's commitment to innovation and luxury. Prioritize the customer's experience by providing empathetic and customer-centric assistance. If uncertain about an inquiry, gracefully offer to connect the user with a human representative or suggest a suitable alternative.",
                },
                {"role": "user", "content": request.query},
            ],
        )

        # Extract the full response content
        content = response.choices[0].message.content
        print("Full response from OpenAI:", content)  # Debug log

        # Log response into the database
        response_time = int((time.time() - start_time) * 1000)
        cursor.execute(
            "INSERT INTO chat_logs (user_id, query, response, response_time_ms) VALUES (%s, %s, %s, %s)",
            (request.user_id, request.query, content, response_time),
        )
        conn.commit()

        return {"response": content}

    except Exception as e:
        print("Error in /chat endpoint:", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/history/{user_id}")
async def get_user_history(user_id: str):
    cursor.execute(
        "SELECT query, response, created_at FROM chat_logs WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )
    history = cursor.fetchall()
    return {
        "history": [
            {"query": row[0], "response": row[1], "created_at": row[2]}
            for row in history
        ]
    }

@app.get("/client/metadata/search")
def search_clients(name: str = Query(None), email: str = Query(None), phone: str = Query(None)):
    if not name and not email and not phone:
        raise HTTPException(status_code=400, detail="At least one search parameter (name, email, phone) is required.")

    query = session.query(Client)

    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))
    if phone:
        query = query.filter(Client.phone.ilike(f"%{phone}%"))

    clients = query.all()

    if not clients:
        raise HTTPException(status_code=404, detail="No clients found matching the search criteria.")

    return [{
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone
    } for client in clients]

@app.get("/client/metadata")
def search_client_metadata(
    client_id: int = Query(None),
    email: str = Query(None),
    phone: str = Query(None),
):
    if not client_id and not email and not phone:
        raise HTTPException(status_code=400, detail="At least one search parameter (client_id, email, phone) is required.")

    query = session.query(Client)

    if client_id:
        query = query.filter(Client.id == client_id)
    if email:
        query = query.filter(Client.email == email)
    if phone:
        query = query.filter(Client.phone == phone)

    client = query.first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    vehicle = session.query(Vehicle).filter(Vehicle.client_id == client.id).first()
    if not vehicle:
        return {
            "client": {
                "name": client.name,
                "email": client.email,
                "phone": client.phone,
            },
            "vehicle": None,
            "service_history": [],
            "appointments": [],
            "message": "Vehicle not found for this client",
        }

    service_history = session.query(ServiceHistory).filter(ServiceHistory.vin == vehicle.vin).all()

    appointments = session.query(Appointment).filter(Appointment.vin == vehicle.vin).all()

    return {
        "client": {
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
        },
        "vehicle": {
            "model": vehicle.model,
            "year": vehicle.year,
            "mileage": vehicle.mileage,
            "warranty_exp": vehicle.warranty_exp,
            "service_plan": vehicle.service_plan,
        },
        "service_history": [
            {"date": sh.date, "service_type": sh.service_type, "notes": sh.notes} for sh in service_history
        ],
        "appointments": [
            {"date": appt.date, "time": appt.time, "service_type": appt.service_type, "status": appt.status} for appt in appointments
        ],
    }
