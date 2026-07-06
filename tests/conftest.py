import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

os.environ["APP_ENV"] = "testing"
os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5432/financecalculator_test")
os.environ["SECRET_KEY"] = "test-secret-key"

from app.database.base import Base
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        os.environ["DATABASE_URL"],
        pool_pre_ping=True,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def auth_headers(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword"},
    )
    if response.status_code == 200:
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}
