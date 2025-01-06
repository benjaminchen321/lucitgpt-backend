# backend/models/init_db.py

import os
import logging
from sqlalchemy import (
    create_engine,
    Column,
    Index,
    Integer,
    String,
    Date,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

Base = declarative_base()

# Define necessary tables for the Enhanced Client Assistance Feature


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Password field for authentication

    vehicles = relationship("Vehicle", back_populates="owner")


class Vehicle(Base):
    __tablename__ = "vehicles"
    vin = Column(String, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=False)
    warranty_exp = Column(Date, nullable=False)
    service_plan = Column(String, nullable=False)

    owner = relationship("Client", back_populates="vehicles")
    service_records = relationship("ServiceHistory", back_populates="vehicle")
    appointments = relationship("Appointment", back_populates="vehicle")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    profile_pic_url = Column(String)
    password = Column(String, nullable=False)  # Password field for authentication
    is_superuser = Column(Boolean, default=False)  # Flag to identify super users

    service_records = relationship("ServiceHistory", back_populates="employee")
    appointments = relationship("Appointment", back_populates="employee")


class ServiceHistory(Base):
    __tablename__ = "service_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String, ForeignKey("vehicles.vin"), nullable=False)
    date = Column(Date, nullable=False)
    service_type = Column(String, nullable=False)
    notes = Column(String)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    vehicle = relationship("Vehicle", back_populates="service_records")
    employee = relationship("Employee", back_populates="service_records")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String, ForeignKey("vehicles.vin"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    vehicle = relationship("Vehicle", back_populates="appointments")
    employee = relationship("Employee", back_populates="appointments")


Index("ix_service_history_vin", ServiceHistory.vin)


# Database connection setup
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# Function to drop all tables
def drop_tables():
    try:
        Base.metadata.drop_all(engine)
        logger.info("All tables dropped successfully.")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise


# Function to create all tables
def create_tables():
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    drop_tables()  # Drop existing tables to reset schema
    create_tables()  # Create tables with the updated schema
