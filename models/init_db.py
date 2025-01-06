# init_db.py
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
    password = Column(String, nullable=False)  # Add password field

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
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    profile_pic_url = Column(String, nullable=True)

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


# Create tables with exception handling
def create_tables():
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    create_tables()
