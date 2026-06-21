"""
Pytest configuration and fixtures for FastAPI tests.

This module provides shared fixtures that are available to all tests in the tests/ directory.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provides a TestClient for making requests to the FastAPI app.
    
    Each test function receives a fresh instance of the client connected
    to the app's test state (in-memory activities database).
    
    Usage in tests:
        def test_example(client):
            response = client.get("/activities")
            assert response.status_code == 200
    """
    return TestClient(app)
