"""
Tests for main.py - API Server endpoints and configuration
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
import os


class TestMainAPI:
    """Test cases for main API endpoints"""

    def test_health_check_endpoint(self):
        """Test health check endpoint returns correct status"""
        from main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp-orchestrator"
        assert "version" in data

    def test_cors_configuration(self):
        """Test CORS configuration is properly set"""
        from main import app

        # Check that CORS middleware is configured
        assert len(app.user_middleware) > 0

        # Find CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, "cls") and "CORS" in str(middleware.cls):
                cors_middleware = middleware
                break

        assert cors_middleware is not None, (
            "CORS middleware should be configured"
        )

    @patch.dict(
        os.environ,
        {
            "POSTGRES_PASSWORD": "test_password",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
        },
    )
    def test_environment_variables_loaded(self):
        """Test that environment variables are properly loaded"""
        from config import Settings

        settings = Settings()

        # Check that settings can be initialized without errors
        assert settings is not None

    def test_mcp_status_endpoint_when_components_unavailable(self):
        """Test MCP status endpoint when components are not available"""
        from main import app

        client = TestClient(app)
        response = client.get("/mcp/status")

        assert response.status_code == 200
        data = response.json()

        # Should show degraded status when components are not initialized
        assert "status" in data
        assert "registry" in data
        assert "client" in data

    def test_list_servers_endpoint_without_registry(self):
        """Test list servers endpoint when registry is not available"""
        from main import app

        client = TestClient(app)
        response = client.get("/mcp/servers")

        # Should return 503 when registry is not available
        assert response.status_code == 503

    def test_call_tool_endpoint_without_client(self):
        """Test call tool endpoint when client is not available"""
        from main import app

        client = TestClient(app)
        response = client.post("/mcp/call", json={"tool": "test"})

        # Should return 503 when client is not available
        assert response.status_code == 503

    def test_call_tool_endpoint_missing_tool_name(self):
        """Test call tool endpoint with missing tool name"""
        from main import app

        client = TestClient(app)
        response = client.post("/mcp/call", json={})

        # Should return 400 when tool name is missing
        assert response.status_code == 400
        data = response.json()
        assert "Tool name is required" in data["detail"]