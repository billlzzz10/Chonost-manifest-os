import pytest
from unittest.mock import Mock, patch, MagicMock
from pytest_mock import MockerFixture
import redis
from notion_client import Client as NotionClient
import os
import sys
import requests

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestIntegrationMocks:
    """Integration tests with mocks for external service failures (Redis/Notion)."""
    
    @pytest.fixture
    def mock_redis_client(self, mocker: MockerFixture):
        """Mock Redis client for outage scenarios."""
        mock_client = mocker.create_autospec(redis.Redis)
        # Mock successful connection
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        return mock_client
    
    @pytest.fixture
    def mock_notion_client(self, mocker: MockerFixture):
        """Mock Notion client for API failures."""
        mock_client = mocker.create_autospec(NotionClient)
        mock_client.pages.retrieve.return_value = {
            "object": "page",
            "properties": {"title": {"title": [{"text": {"content": "Mock Notion Page"}}]}}
        }
        return mock_client
    
    def test_redis_connection_success(self, mock_redis_client, mocker: MockerFixture):
        """Test successful Redis connection and basic operations."""
        # Mock the redis connection in handlers.py
        with patch('core_services.link_ai_core.handlers.redis_client', mock_redis_client):
            # Import the handler after patching
            from core_services.link_ai_core import handlers
            
            # Test RAG cache get/set
            result = handlers.get_rag_cache("test_query")
            assert result is None  # First time, no cache
            
            # Set cache
            cache_data = {"results": ["mock result"], "timestamp": "2025-01-01"}
            handlers.set_rag_cache("test_query", cache_data)
            
            # Verify cache was set
            mock_redis_client.set.assert_called_once()
            mock_redis_client.get.assert_called_once_with("rag_cache:test_query")
            
            # Get from cache
            cached_result = handlers.get_rag_cache("test_query")
            assert cached_result == cache_data
    
    def test_redis_outage_failure_handling(self, mocker: MockerFixture):
        """Test RAG handler with Redis outage - should fallback to direct query."""
        # Mock Redis connection failure
        mock_redis = mocker.create_autospec(redis.Redis)
        mock_redis.ping.side_effect = redis.ConnectionError("Redis server unavailable")
        
        with patch('core_services.link_ai_core.handlers.redis_client', mock_redis):
            from core_services.link_ai_core import handlers
            
            # Mock direct RAG query as fallback
            mock_direct_query = MagicMock(return_value={"results": ["fallback result"]})
            mocker.patch.object(handlers, 'query_rag_direct', mock_direct_query)
            
            # Test RAG handler with Redis down
            result = handlers.handle_rag_request({"query": "test with redis down"})
            
            # Verify fallback was used
            mock_direct_query.assert_called_once()
            assert "fallback result" in result["results"]
            assert "redis_unavailable" in result.get("warnings", [])
    
    def test_notion_api_success(self, mock_notion_client, mocker: MockerFixture):
        """Test successful Notion API integration for sync."""
        with patch('core_services.link_ai_core.handlers.notion_client', mock_notion_client):
            from core_services.link_ai_core import handlers
            
            # Test Notion page retrieval
            page_id = "mock-page-123"
            result = handlers.retrieve_notion_page(page_id)
            
            # Verify mock was called and response processed
            mock_notion_client.pages.retrieve.assert_called_once_with(page_id)
            assert result["title"] == "Mock Notion Page"
    
    def test_notion_api_500_error(self, mocker: MockerFixture):
        """Test Notion API 500 error handling with retry logic."""
        # Mock Notion client with 500 error
        mock_notion = mocker.create_autospec(NotionClient)
        mock_notion.pages.retrieve.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=500, reason="Internal Server Error")
        )
        
        with patch('core_services.link_ai_core.handlers.notion_client', mock_notion):
            from core_services.link_ai_core import handlers
            
            # Test with retry (assume handlers has retry logic)
            result = handlers.retrieve_notion_page("mock-page-123", max_retries=1)
            
            # Verify error was raised or handled
            assert result is None or "notion_error" in result
            mock_notion.pages.retrieve.assert_called_once()  # No retry on 500 for this test
    
    def test_notion_sync_with_partial_failure(self, mock_notion_client, mocker: MockerFixture):
        """Test Notion sync with some pages failing."""
        # Mock mixed success/failure
        mock_notion_client.pages.retrieve.side_effect = [
            {"object": "page", "properties": {"title": {"title": [{"text": {"content": "Success Page"}}]}}},
            requests.exceptions.HTTPError(response=Mock(status_code=404, reason="Not Found"))
        ]
        
        with patch('core_services.link_ai_core.handlers.notion_client', mock_notion_client):
            from core_services.link_ai_core import handlers
            
            # Test sync multiple pages
            page_ids = ["page1", "page2"]
            sync_result = handlers.sync_notion_pages(page_ids)
            
            # Verify partial success
            assert sync_result["successful"] == 1
            assert sync_result["failed"] == 1
            assert "Success Page" in sync_result["synced_content"]
    
    def test_redis_notion_combined_failure(self, mocker: MockerFixture):
        """Test full RAG flow with both Redis and Notion failures."""
        # Mock Redis outage
        mock_redis = mocker.create_autospec(redis.Redis)
        mock_redis.ping.side_effect = redis.ConnectionError("Redis down")
        
        # Mock Notion 500 error
        mock_notion = mocker.create_autospec(NotionClient)
        mock_notion.pages.retrieve.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=500)
        )
        
        with patch('core_services.link_ai_core.handlers.redis_client', mock_redis), \
             patch('core_services.link_ai_core.handlers.notion_client', mock_notion):
            
            from core_services.link_ai_core import handlers
            
            # Mock ultimate fallback (local cache or default response)
            mock_fallback = MagicMock(return_value={"results": ["emergency fallback"], "status": "degraded"})
            mocker.patch.object(handlers, 'get_emergency_fallback', mock_fallback)
            
            # Test RAG request under dual failure
            result = handlers.handle_rag_request({"query": "dual failure test"})
            
            # Verify emergency fallback used
            mock_fallback.assert_called_once()
            assert result["status"] == "degraded"
            assert len(result["results"]) > 0
            assert "redis_unavailable" in result.get("warnings", [])
            assert "notion_unavailable" in result.get("warnings", [])
    
    @pytest.mark.parametrize("error_type", [
        "redis_timeout",
        "notion_auth_error", 
        "network_unreachable"
    ])
    def test_error_logging_and_metrics(self, error_type, mocker: MockerFixture):
        """Test error logging and metrics collection for different failure types."""
        # Mock logger and metrics
        mock_logger = mocker.patch('core_services.link_ai_core.handlers.logger')
        mock_metrics = mocker.patch('core_services.link_ai_core.handlers.metrics')
        
        # Simulate specific error
        if error_type == "redis_timeout":
            mock_redis = mocker.create_autospec(redis.Redis)
            mock_redis.ping.side_effect = redis.TimeoutError("Connection timeout")
            with patch('core_services.link_ai_core.handlers.redis_client', mock_redis):
                from core_services.link_ai_core import handlers
                handlers.handle_rag_request({"query": "timeout test"})
        elif error_type == "notion_auth_error":
            mock_notion = mocker.create_autospec(NotionClient)
            mock_notion.pages.retrieve.side_effect = requests.exceptions.HTTPError(
                response=Mock(status_code=401, reason="Unauthorized")
            )
            with patch('core_services.link_ai_core.handlers.notion_client', mock_notion):
                from core_services.link_ai_core import handlers
                handlers.retrieve_notion_page("unauth-page")
        else:  # network_unreachable
            mock_requests = mocker.patch('requests.get')
            mock_requests.side_effect = requests.exceptions.RequestException("Network error")
            from core_services.link_ai_core import handlers
            handlers.fetch_external_data("http://unreachable.com")
        
        # Verify logging and metrics were called
        mock_logger.error.assert_called()
        mock_metrics.increment.assert_called_with(f"error_{error_type}")
    
    def test_mocks_cleanup(self, mocker: MockerFixture):
        """Ensure mocks are properly cleaned up after tests."""
        # Test that mocks don't interfere with subsequent tests
        initial_patch = mocker.patch('core_services.link_ai_core.handlers.time')
        initial_patch.time.return_value = 12345
        
        from core_services.link_ai_core import handlers
        assert handlers.get_current_timestamp() == 12345
        
        # Create another mock - should not affect previous
        new_mock = mocker.patch('core_services.link_ai_core.handlers.random')
        new_mock.random.return_value = 0.5
        
        # Verify first mock still works
        assert handlers.get_current_timestamp() == 12345
        assert handlers.generate_cache_key("test") == 0.5  # Assuming random used in key gen

# Run with: pytest tests/integration/test_mocks.py -v --tb=short