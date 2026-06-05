"""Pytest fixtures for library application tests"""

import os
import tempfile

import pytest


# Set DB path BEFORE importing library_db_core
# library_db_core.config reads DB_PATH at import time, not at runtime.
# We must set the env var before any import from src.app or library_db_core.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["LIBRARY_DB_PATH"] = _db_path

# Now safe to import modules that read LIBRARY_DB_PATH at import time
from src.app.main import create_app, init_database


def _cleanup_test_db():
    """Remove temporary test database after session"""
    os.close(_db_fd)
    os.unlink(_db_path)


@pytest.fixture(scope="session", autouse=True)
def _session_cleanup(request):
    """Register cleanup to run after all tests"""
    request.addfinalizer(_cleanup_test_db)


@pytest.fixture
def app():
    """Create application for testing with temporary database"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    
    with app.app_context():
        init_database()
    
    yield app


@pytest.fixture
def client(app):
    """Test client for HTTP requests"""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Client authenticated as reader"""
    client.post("/login", data={
        "action": "login",
        "email": "reader@lib.ru",
        "password": "123456",
    })
    return client


@pytest.fixture
def librarian_client(client):
    """Client authenticated as librarian"""
    client.post("/login", data={
        "action": "login",
        "email": "ivanova@lib.ru",
        "password": "123456",
    })
    return client


@pytest.fixture
def admin_client(client):
    """Client authenticated as admin"""
    client.post("/login", data={
        "action": "login",
        "email": "admin@lib.ru",
        "password": "admin",
    })
    return client