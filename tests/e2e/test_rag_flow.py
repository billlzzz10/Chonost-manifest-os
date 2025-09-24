import pytest
from playwright.sync_api import Page, expect
from pytest_mock import MockerFixture
import os
import sys

# Add project root to path for imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:3000"  # Assume React dev server port for ai_chat_interface

@pytest.fixture
def page(page: Page, base_url):
    page.goto(base_url)
    return page

def test_e2e_login_flow(page: Page):
    """Test login flow in ai_chat_interface.tsx."""
    # Fill login form (assume username/password fields)
    page.fill("input[name='username']", "testuser")
    page.fill("input[name='password']", "testpass")
    page.click("button[type='submit']")
    
    # Verify login success - redirect or welcome message
    expect(page.locator(".welcome-message")).to_be_visible()
    expect(page.url).to_contain("/dashboard")

def test_e2e_rag_query_flow(page: Page, mocker: MockerFixture):
    """E2E test for RAG query in chat interface with Notion mock."""
    # Mock Notion API call (assume handler in core-services/link-ai-core/handlers.py calls this)
    mock_notion_response = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "properties": {
                    "title": {
                        "title": [{"text": {"content": "Sample Notion Document for RAG"}}]
                    },
                    "content": {
                        "rich_text": [{"text": {"content": "This is test content for retrieval augmented generation."}}]
                    }
                }
            }
        ]
    }
    
    # Patch the Notion client call (assume import notion_client in handlers.py)
    mocker.patch(
        "core_services.link_ai_core.handlers.notion_client.pages.retrieve",
        return_value=mock_notion_response
    )
    
    # Navigate to chat interface
    page.goto("http://localhost:3000/chat")
    
    # Enter RAG query
    query_input = page.locator("textarea.chat-input")
    query_input.fill("What is in the sample document?")
    page.click("button.send-query")
    
    # Wait for RAG response
    expect(page.locator(".rag-response")).to_be_visible()
    response_text = page.locator(".rag-response").inner_text()
    assert "Sample Notion Document for RAG" in response_text
    assert "retrieval augmented generation" in response_text.lower()

def test_e2e_mcp_response_flow(page: Page):
    """Test MCP response verification after RAG query."""
    # Assume after RAG, MCP orchestrates response
    page.goto("http://localhost:3000/chat")
    
    # Simulate query that triggers MCP
    page.fill("textarea.chat-input", "Generate MCP tool response")
    page.click("button.send-query")
    
    # Verify MCP response appears (assume .mcp-output class)
    expect(page.locator(".mcp-output")).to_be_visible()
    mcp_text = page.locator(".mcp-output").inner_text()
    assert "MCP tool executed successfully" in mcp_text or "Response from MCP orchestrator" in mcp_text
    
    # Check for error absence
    expect(page.locator(".error-message")).not_to_be_visible()

def test_e2e_full_notion_sync_rag_mcp(page: Page, mocker: MockerFixture):
    """Full E2E flow: Notion sync -> RAG query -> MCP response with mocks."""
    # Mock Notion sync API
    mock_sync_data = {"status": "synced", "pages": 1, "message": "Notion data synced successfully"}
    mocker.patch(
        "core_services.link_ai_core.handlers.sync_notion_data",
        return_value=mock_sync_data
    )
    
    # Mock Redis for RAG retrieval (assume redis_client.get in handlers)
    mock_rag_docs = '[{"content": "Synced Notion test doc", "metadata": {"source": "notion"}}]'
    mocker.patch(
        "core_services.link_ai_core.handlers.redis_client.get",
        return_value=mock_rag_docs
    )
    
    # Mock MCP response
    mock_mcp_result = {"tool": "rag_query", "result": "Processed synced data"}
    mocker.patch(
        "chonost_unified.backend.mcp.MCPOrchestratorClient.execute",
        return_value=mock_mcp_result
    )
    
    # Start from login
    page.goto("http://localhost:3000")
    page.fill("input[name='username']", "testuser")
    page.fill("input[name='password']", "testpass")
    page.click("button[type='submit']")
    
    # Trigger Notion sync (assume button in UI)
    page.click(".sync-notion-btn")
    expect(page.locator(".sync-status")).to_contain_text("synced")
    
    # Query RAG
    page.click(".chat-tab")
    page.fill("textarea.chat-input", "Query synced Notion data")
    page.click("button.send-query")
    
    # Verify full flow
    expect(page.locator(".rag-response")).to_contain_text("Synced Notion test doc")
    expect(page.locator(".mcp-output")).to_contain_text("Processed synced data")
    
    # Assert no errors
    expect(page.locator(".error")).not_to_be_visible()

@pytest.mark.asyncio
async def test_e2e_failure_scenarios(page: Page, mocker: MockerFixture):
    """Test failure handling in E2E flow."""
    # Mock Notion 500 error
    mocker.patch(
        "core_services.link_ai_core.handlers.notion_client.pages.retrieve",
        side_effect=Exception("Notion API 500 error")
    )
    
    page.goto("http://localhost:3000/chat")
    page.fill("textarea.chat-input", "Query with Notion failure")
    page.click("button.send-query")
    
    # Verify error handling in UI
    expect(page.locator(".error-message")).to_be_visible()
    assert "Notion API unavailable" in page.locator(".error-message").inner_text()

# Run playwright install if needed (headless by default)
def test_playwright_setup():
    """Ensure Playwright browsers are installed."""
    import subprocess
    result = subprocess.run(["playwright", "install"], capture_output=True)
    assert result.returncode == 0, "Playwright browsers installation failed"