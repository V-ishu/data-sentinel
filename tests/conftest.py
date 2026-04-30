"""Pytest fixtures - shared setup for all tests."""

import os
import tempfile
from pathlib import Path

#IMPORTANT: must be set BEFORE importing app modules so the engine picks it up

TEST_DB = Path(tempfile.gettempdir()) / "data_sentinel_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

import pytest # noqa: E402
from fastapi.testclient import TestClient # noqa: E402

from app.db.base import Base
from app.db.session import engine
from app.main import app

@pytest.fixture(autouse=True)
def reset_db():
    """Wipe + recreate all tables before each test for isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def client():
    return TestClient(app)