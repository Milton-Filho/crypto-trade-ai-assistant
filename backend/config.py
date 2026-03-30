"""
Configuração centralizada do backend via Pydantic Settings.
Valida todas as variáveis de ambiente no startup.

Uso: from config import settings
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Variáveis de ambiente do Crypto Trade AI Assistant."""

    # --- Binance ---
    BINANCE_BASE_URL: str = Field(
        default="https://api.binance.com",
        description="URL base da Binance API"
    )

    # --- Blockchain.com ---
    BLOCKCHAIN_BASE_URL: str = Field(
        default="https://api.blockchain.info",
        description="URL base da Blockchain.com API"
    )

    # --- Mempool.space ---
    MEMPOOL_BASE_URL: str = Field(
        default="https://mempool.space/api",
        description="URL base da Mempool.space API"
    )

    # --- Fear & Greed ---
    FEAR_GREED_URL: str = Field(
        default="https://api.alternative.me/fng/",
        description="URL da Alternative.me Fear & Greed API"
    )

    # --- NewsAPI ---
    NEWS_API_KEY: str = Field(
        default="",
        description="Chave da NewsAPI.org"
    )
    NEWS_BASE_URL: str = Field(
        default="https://newsapi.org/v2",
        description="URL base da NewsAPI"
    )

    # --- Google Gemini ---
    GEMINI_API_KEY: str = Field(
        default="",
        description="Chave da Google AI Studio"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Modelo Gemini a utilizar"
    )

    # --- Supabase ---
    RAW_SUPABASE_URL: str = Field(
        default="",
        alias="SUPABASE_URL",
        description="URL do projecto Supabase"
    )
    SUPABASE_SERVICE_KEY: str = Field(
        default="",
        description="Service role key do Supabase (nunca a anon key)"
    )

    @property
    def SUPABASE_URL(self) -> str:
        return self.RAW_SUPABASE_URL.strip() if self.RAW_SUPABASE_URL else ""

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str = Field(
        default="",
        description="Token do Telegram Bot"
    )
    TELEGRAM_CHAT_ID: str = Field(
        default="",
        description="Chat ID pessoal do Telegram"
    )

    # --- App ---
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="URL de produção do frontend Vercel (para CORS)"
    )
    SYMBOL: str = Field(
        default="BTCUSDT",
        description="Par de moeda a analisar"
    )
    INTRADAY_THRESHOLD: float = Field(
        default=5.0,
        description="Threshold de variação intraday para alerta (%)"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Ambiente: development | production"
    )
    DEV_API_KEY: str = Field(
        default="",
        description="Chave para o endpoint /jobs/trigger (dev only)"
    )

    # Fallback: permite ler de .env se SUPABASE_SERVICE_ROLE_KEY estiver definida
    # mas SUPABASE_SERVICE_KEY não
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="",
        description="Alias alternativo para SUPABASE_SERVICE_KEY"
    )

    @property
    def supabase_key(self) -> str:
        """Retorna a service key, priorizando SUPABASE_SERVICE_KEY."""
        key = self.SUPABASE_SERVICE_KEY or self.SUPABASE_SERVICE_ROLE_KEY
        return key.strip() if key else ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Instância global — importar como: from config import settings
settings = Settings()
