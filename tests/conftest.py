# backend/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.init_db import Base
from utils.dependencies import get_db  # Import get_db function
from main import app
from models.init_db import Client
from utils.auth import get_password_hash
from dotenv import load_dotenv
import os
from jose import jwt, JWTError

# Load environment variables from .env and .env.prod
load_dotenv()

# Verify that SECRET_KEY is loaded
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

# Configure test database (use a separate test database)
TEST_DATABASE_URL = "sqlite:///./test.db"  # Using SQLite for testing

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create the database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create a new database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def client(db):
    """Create a TestClient that uses the test database."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def test_user(db):
    """Create a test user in the database."""
    user = (
        db.query(Client).filter(Client.email == "testuser@example.com").first()
    )
    if not user:
        user = Client(
            name="Test User",
            email="testuser@example.com",
            phone="1234567890",
            password=get_password_hash("testpassword"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture(scope="session")
def auth_token(client, test_user):
    """Obtain a JWT token for the test user."""
    response = client.post(
        "/token",
        data={"username": test_user.email, "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, "Failed to authenticate test user."
    token = response.json()["access_token"]

    # Decode the token for verification
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert isinstance(payload["sub"], str), "Token 'sub' must be a string."
        assert (
            int(payload["sub"]) == test_user.id
        ), "Token 'sub' claim does not match user ID."
    except (JWTError, ValueError) as e:
        pytest.fail(f"Token decoding failed: {e}")

    return token
