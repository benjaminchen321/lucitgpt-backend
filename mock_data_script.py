# mock_data_script.py
import os
from dotenv import load_dotenv

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import random
from backend.models.base import (
    Client,
    Vehicle,
    ServiceHistory,
    Appointment,
    Employee,
)  # Import SQLAlchemy models

print("Loading .env file...")
if not os.path.exists(".env"):
    print("ERROR: .env file not found!")
else:
    print("SUCCESS: .env file found and loaded.")

# Load .env file
print(f"Before loading .env, DATABASE_URL: {os.environ.get('DATABASE_URL')}")
load_dotenv()
print(f"After loading .env, DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Debugging: Print all environment variables
# Commented out to avoid cluttering the output
# print(os.environ)  # Debugging step

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")  # Debugging output
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Initialize Faker
fake = Faker()

# Wipe tables clean
print("Wiping existing data...")
try:
    session.execute(
        text(
            "TRUNCATE TABLE appointments, service_history, vehicles, employees, clients RESTART IDENTITY CASCADE;"
        )
    )
    session.commit()
    print("Tables wiped clean.")
except Exception as e:
    session.rollback()
    print("Error wiping tables:", e)
    raise

# Generate mock data
NUM_CLIENTS = 1000
NUM_VEHICLES = 2000
NUM_EMPLOYEES = 200  # Increased number of employees
NUM_SERVICE_RECORDS = 5000
NUM_APPOINTMENTS = 3000  # Increased number of appointments

# Insert Clients
print("Generating clients...")
clients = []
unique_emails = set()  # Track unique emails
for _ in range(NUM_CLIENTS):
    email = fake.unique.email()
    client = Client(name=fake.name(), email=email, phone=fake.phone_number())
    clients.append(client)

# Insert clients into the database
print("Inserting clients...")
try:
    session.bulk_save_objects(clients)
    session.commit()
    print("Clients inserted successfully!")
except Exception as e:
    session.rollback()
    print("Error inserting clients:", e)
    raise

# Insert Employees
print("Generating employees...")
employees = []
unique_emp_emails = set()
for _ in range(NUM_EMPLOYEES):
    email = fake.unique.email()
    employee = Employee(
        name=fake.name(),
        email=email,
        phone=fake.phone_number(),
        profile_pic_url=fake.image_url(
            width=100, height=100
        ),  # Using placeholder images
    )
    employees.append(employee)

# Insert employees into the database
print("Inserting employees...")
try:
    session.bulk_save_objects(employees)
    session.commit()
    print("Employees inserted successfully!")
except Exception as e:
    session.rollback()
    print("Error inserting employees:", e)
    raise

# Fetch client and employee IDs dynamically
inserted_clients = session.query(Client).all()
inserted_employees = session.query(Employee).all()

# Insert Vehicles
print("Generating vehicles...")
vehicles = []
for _ in range(NUM_VEHICLES):
    vehicle = Vehicle(
        vin=fake.unique.bothify(text="??????#####"),
        client_id=random.choice(inserted_clients).id,
        model=random.choice(["Lucid Air GT", "Lucid Pure", "Lucid Touring"]),
        year=random.randint(2018, 2023),
        mileage=random.randint(0, 150000),  # Increased mileage range
        warranty_exp=fake.date_between(start_date="+1y", end_date="+5y"),
        service_plan=random.choice(["Premium", "Standard", "Elite"]),
    )
    vehicles.append(vehicle)

# Insert vehicles into the database
print("Inserting vehicles...")
try:
    session.bulk_save_objects(vehicles)
    session.commit()
    print("Vehicles inserted successfully!")
except Exception as e:
    session.rollback()
    print("Error inserting vehicles:", e)
    raise

# Fetch all vehicles
inserted_vehicles = session.query(Vehicle).all()

# Insert Service Records
print("Generating service records...")
service_records = []
for _ in range(NUM_SERVICE_RECORDS):
    vehicle = random.choice(inserted_vehicles)
    employee = random.choice(inserted_employees)
    record = ServiceHistory(
        vin=vehicle.vin,
        date=fake.date_between(start_date="-5y", end_date="today"),
        service_type=random.choice(
            [
                "Oil Change",
                "Tire Rotation",
                "Software Update",
                "Battery Replacement",
                "Brake Inspection",
                "Transmission Repair",
            ]
        ),
        notes=fake.sentence(nb_words=10),
        employee_id=employee.id,
    )
    service_records.append(record)

# Insert service records into the database
print("Inserting service records...")
try:
    session.bulk_save_objects(service_records)
    session.commit()
    print("Service records inserted successfully!")
except Exception as e:
    session.rollback()
    print("Error inserting service records:", e)
    raise

# Insert Appointments
print("Generating appointments...")
appointments = []
for _ in range(NUM_APPOINTMENTS):
    vehicle = random.choice(inserted_vehicles)
    employee = random.choice(inserted_employees)
    appointment = Appointment(
        vin=vehicle.vin,
        date=fake.date_between(start_date="today", end_date="+2y"),
        time=fake.time(),
        service_type=random.choice(
            [
                "Battery Check",
                "Brake Inspection",
                "Tire Replacement",
                "Engine Diagnostics",
                "Software Update",
                "Oil Change",
            ]
        ),
        status=random.choice(["Scheduled", "Completed", "Cancelled", "No-show"]),
        employee_id=employee.id,
    )
    appointments.append(appointment)

# Insert appointments into the database
print("Inserting appointments...")
try:
    session.bulk_save_objects(appointments)
    session.commit()
    print("Appointments inserted successfully!")
except Exception as e:
    session.rollback()
    print("Error inserting appointments:", e)
    raise

print("Mock data generation completed successfully!")
