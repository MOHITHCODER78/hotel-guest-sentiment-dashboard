import os
import sys

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.ml_engine import ABSAEngine

TEST_USER_EMAIL = "manager@hotel.com"
TEST_USER_PASSWORD = "password123"


@pytest.fixture
def mock_classifier():
    def classify(text: str):
        lowered = text.lower()
        if any(word in lowered for word in ["dirty", "terrible", "cold", "poor", "slow"]):
            return [{"label": "NEGATIVE", "score": 0.91}]
        return [{"label": "POSITIVE", "score": 0.89}]

    return classify


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session_factory(test_engine):
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def _factory():
        return testing_session_local()

    return _factory


@pytest.fixture
def client(session_factory, mock_classifier, monkeypatch):
    mock_engine = ABSAEngine(classifier=mock_classifier)
    monkeypatch.setattr("app.services.analysis.ml_engine", mock_engine)
    monkeypatch.setattr("app.services.bulk_processor.ml_engine", mock_engine)
    monkeypatch.setattr("app.services.bulk_processor.SessionLocal", session_factory)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": "Hotel Manager",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ml_engine_with_mock(mock_classifier):
    return ABSAEngine(classifier=mock_classifier)
