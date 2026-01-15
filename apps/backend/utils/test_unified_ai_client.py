import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

# Import the module to be tested and its components
from .unified_ai_client import UnifiedAIClient, GoogleStrategy, get_client
from . import unified_ai_client as client_module # Import the module for patching

# --- GoogleStrategy Tests ---
@patch('google.generativeai.configure')
def test_google_strategy_initialization(mock_configure):
    """Tests that the GoogleStrategy initializes correctly."""
    strategy = GoogleStrategy(api_key='test_api_key')
    mock_configure.assert_called_once_with(api_key='test_api_key')
    assert strategy.model is not None

@patch('google.generativeai.GenerativeModel')
@patch('google.generativeai.configure')
def test_google_strategy_generate_response_success(mock_configure, mock_generative_model):
    """Tests a successful generate_response call with a per-request model."""
    mock_api_response = MagicMock()
    mock_api_response.text = 'Test response'
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_api_response
    mock_generative_model.return_value = mock_model_instance
    strategy = GoogleStrategy(api_key='test_api_key', model='gemini-1.5-flash')
    messages = [{'role': 'user', 'content': 'Hello'}]
    response = strategy.generate_response(messages, model='gemini-pro')
    mock_generative_model.assert_called_with('gemini-pro')
    assert response['success'] is True
    assert response['provider'] == 'google'
    assert response['content'] == 'Test response'
    assert response['metadata']['model'] == 'gemini-pro'

@patch('google.generativeai.GenerativeModel')
@patch('google.generativeai.configure')
def test_google_strategy_generate_response_error(mock_configure, mock_model):
    """Tests error handling in the generate_response method."""
    mock_model.return_value.generate_content.side_effect = Exception('API Error')
    strategy = GoogleStrategy(api_key='test_api_key', model='gemini-1.5-flash')
    messages = [{'role': 'user', 'content': 'Hello'}]
    response = strategy.generate_response(messages)
    assert response['success'] is False
    assert response['error'] == 'API Error'

@patch('google.generativeai.embed_content')
@patch('google.generativeai.configure')
def test_google_strategy_embed_success(mock_configure, mock_embed_content):
    """Tests a successful embed call."""
    mock_embed_content.return_value = {'embedding': [0.1, 0.2, 0.3]}
    strategy = GoogleStrategy(api_key='test_api_key')
    response = strategy.embed('some text')
    assert response['success'] is True
    assert response['provider'] == 'google'
    assert response['embedding'] == [0.1, 0.2, 0.3]

@patch('google.generativeai.embed_content')
@patch('google.generativeai.configure')
def test_google_strategy_embed_error(mock_configure, mock_embed_content):
    """Tests error handling in the embed method."""
    mock_embed_content.side_effect = Exception('Embedding Error')
    strategy = GoogleStrategy(api_key='test_api_key')
    response = strategy.embed('some text')
    assert response['success'] is False
    assert response['error'] == 'Embedding Error'


# --- 🛡️ Guardian: Final Revised Test Suite for UnifiedAIClient ---

@pytest.fixture
def mock_settings():
    """Provides a simple mock settings object for dependency injection."""
    return SimpleNamespace(
        openai_api_key=None,
        google_api_key=None,
        openrouter_api_key=None,
        anthropic_api_key=None,
        deepseek_api_key=None,
        mistral_api_key=None,
        openai_base_url=None,
        ollama_base_url="http://mock-ollama:11434"
    )

@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensures the singleton instance is reset before each test."""
    client_module._client_instance = None
    yield
    client_module._client_instance = None

class TestUnifiedAIClient:

    def test_client_initialization_with_di(self, mock_settings):
        """Client initializes correctly with injected settings."""
        client = UnifiedAIClient(settings_override=mock_settings)
        assert client.settings is mock_settings
        assert not client._strategies

    @patch.object(client_module, 'OpenAIStrategy')
    def test_get_provider_lazy_initialization_and_caching(self, MockOpenAIStrategy, mock_settings):
        """Provider is initialized on first use and cached."""
        mock_settings.openai_api_key = "fake_key"
        client = UnifiedAIClient(settings_override=mock_settings)

        # First call should instantiate and cache the strategy
        provider1 = client.get_provider('openai')
        assert provider1 is not None
        MockOpenAIStrategy.assert_called_once_with(api_key="fake_key", base_url=None)

        # Second call should return the cached instance
        provider2 = client.get_provider('openai')
        assert provider1 is provider2
        MockOpenAIStrategy.assert_called_once() # Should NOT be called again

    def test_get_provider_unconfigured(self, mock_settings):
        """get_provider returns None for a provider with no API key."""
        client = UnifiedAIClient(settings_override=mock_settings)
        assert client.get_provider('openai') is None
        assert not client._strategies

    @patch.object(client_module, 'GoogleStrategy')
    def test_generate_response_success(self, MockGoogleStrategy, mock_settings):
        """generate_response dispatches correctly to the configured provider."""
        mock_settings.google_api_key = "fake_google_key"
        client = UnifiedAIClient(settings_override=mock_settings)

        mock_strategy_instance = MockGoogleStrategy.return_value
        mock_strategy_instance.generate_response.return_value = {'success': True, 'content': 'google says hi'}

        # The 'messages' list must not be empty for the Google API call
        response = client.generate_response(provider='google', messages=[{'role': 'user', 'content': 'test'}])

        assert response['content'] == 'google says hi'
        MockGoogleStrategy.assert_called_once_with(api_key="fake_google_key")
        mock_strategy_instance.generate_response.assert_called_once()

    def test_generate_response_unconfigured_provider(self, mock_settings):
        """generate_response raises ValueError for an unconfigured provider."""
        client = UnifiedAIClient(settings_override=mock_settings)
        with pytest.raises(ValueError, match="Provider 'google' is not supported or configured."):
            client.generate_response(provider='google', messages=[])

    @patch.object(client_module, 'UnifiedAIClient')
    def test_singleton_behavior_of_get_client(self, MockUnifiedAIClient, mock_settings):
        """get_client() factory returns a singleton instance."""
        # This test ensures the global factory function works as expected.
        # It doesn't use the DI constructor directly.

        # Call get_client twice
        client1 = get_client()
        client2 = get_client()

        # Assert that the same instance is returned
        assert client1 is client2
        # Assert that the UnifiedAIClient constructor was only called once
        MockUnifiedAIClient.assert_called_once()
