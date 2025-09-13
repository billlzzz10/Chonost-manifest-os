import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'backend')))

from src.main import app

client = TestClient(app)

def test_root():
    """
    Tests the root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["message"] == "Chonost Manuscript OS API"
    assert "version" in json_response

def test_health_check():
    """
    Tests the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert json_response["service"] == "chonost-api"
