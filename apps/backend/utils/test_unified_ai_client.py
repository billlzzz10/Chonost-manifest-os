import pytest
from unittest.mock import patch, MagicMock
from .unified_ai_client import GoogleStrategy

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

    # Mock the return value of the GenerativeModel constructor
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_api_response
    mock_generative_model.return_value = mock_model_instance

    strategy = GoogleStrategy(api_key='test_api_key', model='gemini-1.5-flash')
    messages = [{'role': 'user', 'content': 'Hello'}]

    # Call with a different model
    response = strategy.generate_response(messages, model='gemini-pro')

    # Verify that the correct model was used
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
