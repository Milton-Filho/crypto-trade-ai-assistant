import pytest
from unittest.mock import patch, MagicMock
from engines.technical_engine import TechnicalEngine, TechnicalDataError
from engines.onchain_engine import OnchainEngine, OnchainDataError
from engines.sentiment_engine import SentimentEngine, SentimentDataError

# --- TechnicalEngine Tests ---

@patch("engines.technical_engine.requests.get")
def test_technical_engine_success(mock_get):
    mock_response = MagicMock()
    # Mock 100 klines
    # [open_time, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore]
    mock_klines = [[1600000000000 + i*86400000, "50000", "51000", "49000", str(50000 + i*10), "100", 1600000086400, "5000000", 1000, "50", "2500000", "0"] for i in range(100)]
    mock_response.json.return_value = mock_klines
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    engine = TechnicalEngine()
    data = engine.get_data()
    
    assert "price_close" in data
    assert "rsi_14" in data
    assert "macd_cross_bullish" in data
    assert isinstance(data["macd_cross_bullish"], bool)

@patch("engines.technical_engine.requests.get")
def test_technical_engine_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    engine = TechnicalEngine()
    
    with pytest.raises(TechnicalDataError):
        engine.get_data()

# --- OnchainEngine Tests ---

@patch("engines.onchain_engine.requests.get")
def test_onchain_engine_success(mock_get):
    def side_effect(url, **kwargs):
        mock_resp = MagicMock()
        if "blockchain.info" in url:
            mock_resp.json.return_value = {"hash_rate": 150000000}
        elif "mempool.space" in url:
            mock_resp.json.return_value = {"fastestFee": 20}
        return mock_resp
        
    mock_get.side_effect = side_effect
    
    engine = OnchainEngine()
    data = engine.get_data()
    
    assert data["network_health"] == "SAUDAVEL"
    assert data["fastest_fee"] == 20
    assert data["hashrate_th"] == 150000.0
    assert data["partial"] is False

@patch("engines.onchain_engine.requests.get")
def test_onchain_engine_partial_failure(mock_get):
    def side_effect(url, **kwargs):
        if "blockchain.info" in url:
            raise Exception("Blockchain API Error")
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"fastestFee": 60}
        return mock_resp
        
    mock_get.side_effect = side_effect
    
    engine = OnchainEngine()
    data = engine.get_data()
    
    assert data["network_health"] == "CONGESTIONADA"
    assert data["fastest_fee"] == 60
    assert data["hashrate_th"] == 0.0
    assert data["partial"] is True

@patch("engines.onchain_engine.requests.get")
def test_onchain_engine_total_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    engine = OnchainEngine()
    
    with pytest.raises(OnchainDataError):
        engine.get_data()

# --- SentimentEngine Tests ---

@patch("engines.sentiment_engine.os.getenv")
@patch("engines.sentiment_engine.requests.get")
def test_sentiment_engine_success(mock_get, mock_getenv):
    mock_getenv.return_value = "fake_api_key"
    
    def side_effect(url, **kwargs):
        mock_resp = MagicMock()
        if "alternative.me" in url:
            mock_resp.json.return_value = {"data": [{"value": "75", "value_classification": "Greed"}]}
        elif "newsapi.org" in url:
            mock_resp.json.return_value = {"articles": [{"title": "Bitcoin surges"}, {"title": "Crypto regulation"}, {"title": "ETF approved"}]}
        return mock_resp
        
    mock_get.side_effect = side_effect
    
    engine = SentimentEngine()
    data = engine.get_data()
    
    assert data["fear_greed_score"] == 75
    assert data["fear_greed_classification"] == "Greed"
    assert len(data["top_headlines"]) == 3
    assert data["top_headlines"][0] == "Bitcoin surges"

@patch("engines.sentiment_engine.requests.get")
def test_sentiment_engine_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    engine = SentimentEngine()
    
    with pytest.raises(SentimentDataError):
        engine.get_data()
