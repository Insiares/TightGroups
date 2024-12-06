import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from API.routes import app, get_db, ini_db
from API.Database.Models import Base, User, Setup, Image, Score, Ammo, Seance
import os
import sys
from API.auth import get_password_hash

sys.path.insert(0,
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../"
                    ) ))

print("==========")
for path in sys.path:
    print(path)
print("==========")
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    


'''    
@pytest.fixture(scope="module", autouse=True)
def clean_db(session):
    session.query(User).delete()
    session.query(Seance).delete()
    session.query(Setup).delete()
    session.query(Image).delete()
    session.query(Score).delete()
    session.commit() '''
'''
@pytest.fixture(scope="function")
def session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    
@pytest.fixture
def create_test_user(session):
    """Create a test user in the database."""
    user = User(email="testuser@example.com", username="testuser", password_hash=get_password_hash("testpassword"))
    session.add(user)
    session.commit()    
    return user '''
