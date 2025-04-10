# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
os.environ["JWT_KEY"] = "test_secret_key"
os.environ["REFRESH_KEY"] = "test_refresh_secret_key"
os.environ["ALGORITHM"] = "HS256"
# Import your app and models
from API.routes import app, get_db
from API.Database.Models import User, Seance, Setup, Ammo, Image

# Constants for testing
SECRET_KEY = "test_secret_key"
REFRESH_SECRET_KEY = "test_refresh_secret_key"
ALGORITHM = "HS256"
#
# @pytest.fixture(autouse=True)
# def mock_env(monkeypatch):
#     monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
#     monkeypatch.setenv("REFRESH_SECRET_KEY", REFRESH_SECRET_KEY)
#     monkeypatch.setenv("ALGORITHM", ALGORITHM)
#


# @pytest.fixture
# def client():
#     return TestClient(app)
@pytest.fixture
def client(mock_db):
    """Get test client with mock database dependency"""

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Reset overrides after test
    app.dependency_overrides = {}


@pytest.fixture
def mock_db():
    mock = MagicMock(spec=Session)
    query_mock = MagicMock()
    mock.query.return_value = query_mock

    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock

    filter_mock.all.return_value = []
    filter_mock.first.return_value = None
    filter_mock.count.return_value = 0
    return mock


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password123",
    )


@pytest.fixture
def access_token(test_user):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": str(test_user.id), "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def refresh_token(test_user):
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode = {"sub": str(test_user.id), "exp": expire}
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def test_setup():
    return Setup(
        id=1,
        user_id=1,
        name="Test Setup",
        gear="Test Gear",
        ammo=1,  # This is an ID referencing the Ammo table
        position="Standing",
        drills="Basic",
    )


@pytest.fixture
def test_ammo():
    return Ammo(id=1, name="Test Ammo")


@pytest.fixture
def test_seance():
    return Seance(
        id=1,
        user_id=1,
        temp_C=25.0,
        wind_speed=10.0,
        wind_gust=15.0,
        wind_dir="North",
        pressure=1013.0,
        precipitation=0.0,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def test_image():
    return Image(
        id=1, seance_id=1, setup_id=1, file_path="./tests/static/test_photo.jpg"
    )


#
# @pytest.fixture(scope="function")
# def db_cleanup(db_session: Session):
#     """Fixture that provides a DB session and cleans up test data after test"""
#     yield db_session
#
#     # After test runs, delete test data
#     # Identify test data (e.g., using a naming convention or test-specific IDs)
#     db_session.execute("DELETE FROM users WHERE email LIKE 'test%@example.com'")
#     # Add more tables as needed
#
#     db_session.commit()

persisted_tokens = {}


@pytest.fixture(autouse=True)
def refresh_tokens_dict():
    """
    Fixture that provides access to a persisted tokens dictionary
    that will remain available across different test functions
    """
    with patch("API.routes.refresh_tokens_dict", persisted_tokens):
        yield
