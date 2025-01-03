import os
from fastapi.middleware.cors import CORSMiddleware
import time

import psycopg2
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException
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
# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
app.add_middleware(SentryAsgiMiddleware)


# OpenAI Client Initialization
OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# SQLAlchemy Base
Base = declarative_base()


# CORS
origins = ["https://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PostgreSQL Connection
conn = psycopg2.connect(
    database="lucidgpt_db",
    user="lucid_user",
    password="lucid_password",
    host="localhost",
    port="5432",
)
cursor = conn.cursor()


# Elasticsearch Connection
es = Elasticsearch(["http://localhost:9200"])


#database connection
DATABASE_URL = os.environ.get("DATABASE_URL")
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


@app.get("/search/{query}")
async def search_faq(query: str):
    try:
        # Search Elasticsearch for FAQs
        results = es.search(index="faqs", body={"query": {"match": {"content": query}}})
        return {"results": results["hits"]["hits"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/client/{client_id}/metadata")
def get_client_metadata(client_id: int):
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    vehicle = session.query(Vehicle).filter(Vehicle.client_id == client_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    service_history = session.query(ServiceHistory).filter(ServiceHistory.vin == vehicle.vin).all()

    appointments = session.query(Appointment).filter(Appointment.vin == vehicle.vin).all()

    return {
        "client": {
            "name": client.name,
            "email": client.email,
            "phone": client.phone
        },
        "vehicle": {
            "model": vehicle.model,
            "year": vehicle.year,
            "mileage": vehicle.mileage,
            "warranty_exp": vehicle.warranty_exp,
            "service_plan": vehicle.service_plan
        },
        "service_history": [
            {"date": sh.date, "service_type": sh.service_type, "notes": sh.notes} for sh in service_history
        ],
        "appointments": [
            {"date": appt.date, "time": appt.time, "service_type": appt.service_type, "status": appt.status} for appt in appointments
        ]
    }

@app.get("/api/customers")
def get_customers():
    try:
        customers = session.query(Client).all()
        return [{"id": customer.id, "name": customer.name, "email": customer.email, "phone": customer.phone} for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch customers")

@app.get("/api/customers/{customer_id}")
def get_customer_details(customer_id: int):
    try:
        customer = session.query(Client).filter(Client.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        vehicles = session.query(Vehicle).filter(Vehicle.client_id == customer_id).all()
        service_history = session.query(ServiceHistory).join(Vehicle).filter(Vehicle.client_id == customer_id).all()
        appointments = session.query(Appointment).join(Vehicle).filter(Vehicle.client_id == customer_id).all()

        return {
            "customer": {"name": customer.name, "email": customer.email, "phone": customer.phone},
            "vehicles": [{"vin": v.vin, "model": v.model, "year": v.year} for v in vehicles],
            "serviceHistory": [{"date": s.date, "service_type": s.service_type, "notes": s.notes} for s in service_history],
            "appointments": [{"date": a.date, "time": a.time, "service_type": a.service_type, "status": a.status} for a in appointments],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch customer details")