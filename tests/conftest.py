"""Pytest fixtures for library application tests"""

import os
import tempfile

import pytest

from src.app.main import create_app, init_database


@pytest.fixture
def app():
    """Create application for testing with temporary database"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["LIBRARY_DB_PATH"] = db_path
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    
    with app.app_context():
        init_database()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)
    del os.environ["LIBRARY_DB_PATH"]


@pytest.fixture
def client(app):
    """Test client for HTTP requests"""
    return app.test_client()