# backend/mock_data_script.py

import os
from dotenv import load_dotenv

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import random
from models.init_db import (
    Client,
    Vehicle,
    ServiceHistory,
    Appointment,
    Employee,
)  # Import SQLAlchemy models
from utils.auth import get_password_hash

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
            "TRUNCATE TABLE appointments, service_history, vehicles, "
            "employees, clients RESTART IDENTITY CASCADE;"
        )
    )
    session.commit()
    print("Tables wiped clean.")
except Exception as e:
    session.rollback()
    print("Error wiping tables:", e)
    raise

# Insert Super User
print("Creating super user...")
super_user = Employee(
    name="Super User",
    email="superuser@example.com",
    phone="000.000.0000",
    profile_pic_url="https://dummyimage.com/100x100",
    password=get_password_hash("SuperPassword123"),  # Secure password
    is_superuser=True,
)
try:
    session.add(super_user)
    session.commit()
    print("Super user created successfully!")
except Exception as e:
    session.rollback()
    print("Error creating super user:", e)
    raise

# Insert Employees
print("Generating employees...")
employees = []
unique_emp_emails = set()
for _ in range(999):  # Total employees including super user is 1000
    print(f"employee{_}")
    email = fake.unique.email()
    employee = Employee(
        name=fake.name(),
        email=email,
        phone=fake.phone_number(),
        profile_pic_url=fake.image_url(
            width=100, height=100
        ),  # Using placeholder images
        password=get_password_hash("password123"),  # Default password for employees
        is_superuser=False,
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

# Insert Clients
print("Generating clients...")
clients = []
unique_emails = set()  # Track unique emails
for _ in range(5000):  # Increased number of clients
    print(f"client{_}")
    email = fake.unique.email()
    client = Client(
        name=fake.name(),
        email=email,
        phone=fake.phone_number(),
        password=get_password_hash("password123"),  # Default password for clients
    )
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

# Fetch client and employee IDs dynamically
inserted_clients = session.query(Client).all()
inserted_employees = session.query(Employee).all()

# Insert Vehicles
print("Generating vehicles...")
vehicles = []
for _ in range(5000):  # Increased number of vehicles
    print(f"vehicle{_}")
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
for _ in range(2000):  # Increased number of service records
    print(f"record{_}")
    vehicle = random.choice(inserted_vehicles)
    # Super user can be assigned to some service records
    employee = random.choice(inserted_employees + [super_user])
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
for _ in range(3000):  # Increased number of appointments
    print(f"appointment{_}")
    vehicle = random.choice(inserted_vehicles)
    # Super user can be assigned to some appointments
    employee = random.choice(inserted_employees + [super_user])
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
