# backend/tests/test_appointments.py

from models.init_db import Appointment, Client, Vehicle, Employee
from datetime import date


def test_get_appointments(client, auth_token, db):
    # Create a test appointment
    test_employee = Employee(
        name="John Doe",
        email="johndoe@example.com",
        phone="0987654321",
        profile_pic_url=None,
    )
    db.add(test_employee)
    db.commit()
    db.refresh(test_employee)

    test_client = (
        db.query(Client).filter(Client.email == "testuser@example.com").first()
    )
    test_vehicle = Vehicle(
        vin="1HGCM82633A004352",
        client_id=test_client.id,
        model="Honda Civic",
        year=2020,
        mileage=15000,
        warranty_exp=date(2023, 12, 31),
        service_plan="Premium",
    )
    db.add(test_vehicle)
    db.commit()
    db.refresh(test_vehicle)

    test_appointment = Appointment(
        vin=test_vehicle.vin,
        date=date.today(),
        time="10:00 AM",
        service_type="Oil Change",
        status="Scheduled",
        employee_id=test_employee.id,
    )
    db.add(test_appointment)
    db.commit()
    db.refresh(test_appointment)

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/appointments", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Response should be a list."
    assert len(data) >= 1, "There should be at least one appointment."
    # Optionally, check for the presence of the test appointment
    assert any(
        appointment["vin"] == test_vehicle.vin for appointment in data
    ), "Test appointment not found in response."
