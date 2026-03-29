import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from core.ai_analyst import AIAnalyst, AIAnalystError

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")

@pytest.fixture
def sample_payload():
    return {"price_close": 50000, "signal": "VERDE"}

@patch("core.ai_analyst.genai.GenerativeModel")
@patch("builtins.open", new_callable=mock_open, read_data="MOCK PROMPT")
@pytest.mark.asyncio
async def test_ai_analyst_success(mock_file, mock_model_class, mock_env, sample_payload):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "technical": "Tech analysis",
        "onchain": "Onchain analysis",
        "sentiment": "Sentiment analysis",
        "verdict": "Verdict analysis"
    })
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    analyst = AIAnalyst()
    result = await analyst.generate(sample_payload)
    
    assert result["technical"] == "Tech analysis"
    assert result["verdict"] == "Verdict analysis"
    mock_model_instance.generate_content.assert_called_once()

@patch("core.ai_analyst.genai.GenerativeModel")
@patch("builtins.open", new_callable=mock_open, read_data="MOCK PROMPT")
@pytest.mark.asyncio
async def test_ai_analyst_markdown_fallback(mock_file, mock_model_class, mock_env, sample_payload):
    # Setup mock response with markdown block
    mock_response = MagicMock()
    mock_response.text = """```json
{
  "technical": "Tech analysis",
  "onchain": "Onchain analysis",
  "sentiment": "Sentiment analysis",
  "verdict": "Verdict analysis"
}
```"""
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    analyst = AIAnalyst()
    result = await analyst.generate(sample_payload)
    
    assert result["technical"] == "Tech analysis"
    assert result["verdict"] == "Verdict analysis"

@patch("core.ai_analyst.genai.GenerativeModel")
@patch("builtins.open", new_callable=mock_open, read_data="MOCK PROMPT")
@pytest.mark.asyncio
async def test_ai_analyst_missing_fields_retry_then_fallback(mock_file, mock_model_class, mock_env, sample_payload):
    # Setup mock response missing a required field
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "technical": "Tech analysis",
        "onchain": "Onchain analysis",
        # Missing sentiment and verdict
    })
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    analyst = AIAnalyst()
    result = await analyst.generate(sample_payload)
    
    # It should retry 1 time (total 2 calls) and then return the fallback error dict
    assert mock_model_instance.generate_content.call_count == 2
    assert "Falha ao gerar análise" in result["technical"]
    assert "Falha ao gerar análise" in result["verdict"]

@patch("core.ai_analyst.genai.GenerativeModel")
@patch("builtins.open", new_callable=mock_open, read_data="MOCK PROMPT")
@pytest.mark.asyncio
async def test_ai_analyst_api_error_fallback(mock_file, mock_model_class, mock_env, sample_payload):
    # Setup mock to raise exception
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.side_effect = Exception("API Timeout")
    mock_model_class.return_value = mock_model_instance

    analyst = AIAnalyst()
    result = await analyst.generate(sample_payload)
    
    # It should retry 1 time (total 2 calls) and then return the fallback error dict
    assert mock_model_instance.generate_content.call_count == 2
    assert "API Timeout" in result["technical"]
    assert "API Timeout" in result["verdict"]
