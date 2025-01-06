# backend/models/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import date


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: str


class CustomerCreate(CustomerBase):
    password: str


class VehicleBase(BaseModel):
    vin: str
    client_id: int
    model: str
    year: int
    mileage: int
    warranty_exp: date
    service_plan: str

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    vin: str
    date: date
    time: str
    service_type: str
    status: str
    employee_id: int

    class Config:
        from_attributes = True


class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class CustomerDetailResponse(BaseModel):
    customer: CustomerResponse
    vehicles: List[VehicleBase]
    appointments: List[AppointmentBase]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    profile_pic_url: str

    class Config:
        from_attributes = True
