"""Shared pytest fixtures for API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.database import engine, SessionLocal, init_db
from app.main import app
from app.models import Base
from app.schemas import TodoBase


@pytest.fixture(autouse=True)
def reset_db():
    """Create a fresh in-memory schema before each test and drop after."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """FastAPI test client. `reset_db` runs first (autouse)."""
    with TestClient(app) as c:
        yield c
