from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Análise não encontrada")
    code: str = Field(..., example="NOT_FOUND")

class DailyAnalysisResponse(BaseModel):
    id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    date: str = Field(..., example="2025-03-29")
    symbol: str = Field(..., example="BTCUSDT")
    price_close: float = Field(..., example=65000.0)
    price_entry: float = Field(..., example=65000.0)
    stop_loss: float = Field(..., example=62000.0)
    take_profit: float = Field(..., example=71000.0)
    rr_ratio: float = Field(..., example=2.0)
    atr_14: float = Field(..., example=2000.0)
    rsi_14: float = Field(..., example=45.5)
    sma_20: float = Field(..., example=64000.0)
    sma_50: float = Field(..., example=60000.0)
    macd_value: Optional[float] = Field(None, example=150.0)
    macd_signal: Optional[float] = Field(None, example=100.0)
    bb_upper: float = Field(..., example=68000.0)
    bb_lower: float = Field(..., example=60000.0)
    tx_volume: float = Field(..., example=150000.0)
    tx_count: int = Field(..., example=350000)
    hash_rate: float = Field(..., example=600.5)
    mempool_fee: float = Field(..., example=15.0)
    fear_greed_score: int = Field(..., example=75)
    fear_greed_label: str = Field(..., example="Greed")
    news_headlines: List[str] = Field(..., example=["Bitcoin hits new high", "ETF inflows surge"])
    confluence_score: int = Field(..., example=7)
    signal: str = Field(..., example="VERDE")
    ai_report_technical: str = Field(..., example="O RSI está neutro...")
    ai_report_onchain: str = Field(..., example="A rede está saudável...")
    ai_report_sentiment: str = Field(..., example="O mercado está otimista...")
    ai_report_verdict: str = Field(..., example="Sinal de compra confirmado...")
    outcome: str = Field(..., example="OPEN")
    outcome_price: Optional[float] = Field(None, example=None)
    outcome_note: Optional[str] = Field(None, example=None)
    outcome_source: Optional[str] = Field(None, example=None)
    error_log: Optional[str] = Field(None, example=None)
    telegram_sent: Optional[bool] = Field(False, example=True)

class UpdateOutcomeRequest(BaseModel):
    outcome: Literal["TP_HIT", "SL_HIT", "MANUAL"] = Field(..., example="TP_HIT")
    price: float = Field(..., example=71000.0)
    note: str = Field(..., example="Fechado manualmente com lucro")

class SettingsResponse(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    intraday_threshold: float = Field(..., example=5.0)
    symbol: str = Field(..., example="BTCUSDT")
    cron_time_utc: str = Field(..., example="01:00")

class UpdateSettingsRequest(BaseModel):
    intraday_threshold: float = Field(..., example=5.0, ge=1.0, le=20.0)
    symbol: str = Field(..., example="BTCUSDT", pattern=r"^[A-Z0-9]+USDT$")
    cron_time_utc: Optional[str] = Field("01:00", example="01:00")

class SuccessResponse(BaseModel):
    success: bool = Field(..., example=True)
    message: Optional[str] = Field(None, example="Operação realizada com sucesso")
