import pytest
from core.signal_engine import SignalEngine
from core.risk_manager import RiskManager

def test_signal_engine_verde():
    engine = SignalEngine()
    tech = {
        "rsi_14": 30,               # +2
        "price_close": 49000, 
        "bb_lower": 50000,          # +2
        "macd_cross_bullish": True, # +1
        "sma_20": 51000, 
        "sma_50": 50000             # +1
    }
    onchain = {"network_health": "SAUDAVEL"} # +1
    sentiment = {"fear_greed_score": 20}     # +2
    
    # Total score should be 9
    result = engine.calculate(tech, onchain, sentiment)
    assert result["confluence_score"] == 9
    assert result["signal"] == "VERDE"

def test_signal_engine_vermelho():
    engine = SignalEngine()
    tech = {
        "rsi_14": 70,               # 0
        "price_close": 55000, 
        "bb_lower": 50000,          # 0
        "macd_cross_bullish": False,# 0
        "sma_20": 49000, 
        "sma_50": 50000             # 0
    }
    onchain = {"network_health": "CONGESTIONADA"} # 0
    sentiment = {"fear_greed_score": 80}          # 0
    
    # Total score should be 0
    result = engine.calculate(tech, onchain, sentiment)
    assert result["confluence_score"] == 0
    assert result["signal"] == "VERMELHO"

def test_risk_manager_verde():
    rm = RiskManager()
    result = rm.calculate(price_close=100000, atr_14=2000, signal="VERDE")
    
    assert result["price_entry"] == 100000
    assert result["stop_loss"] == 97000      # 100000 - (2000 * 1.5)
    assert result["take_profit"] == 106000   # 100000 + (2000 * 3.0)
    assert result["rr_ratio"] == 2.0
    assert result["sl_percent"] == -3.0
    assert result["tp_percent"] == 6.0

def test_risk_manager_vermelho():
    rm = RiskManager()
    result = rm.calculate(price_close=100000, atr_14=2000, signal="VERMELHO")
    
    assert result["price_entry"] == 100000
    assert result["stop_loss"] == 103000     # 100000 + (2000 * 1.5)
    assert result["take_profit"] == 94000    # 100000 - (2000 * 3.0)
    assert result["rr_ratio"] == 2.0
    assert result["sl_percent"] == 3.0
    assert result["tp_percent"] == -6.0
