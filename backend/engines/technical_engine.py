import logging
import sys
import os

# Permitir import do config quando executado como módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import pandas as pd
import ta
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)


class TechnicalDataError(Exception):
    pass


class TechnicalEngine:
    """
    Engine para colecta e cálculo de dados técnicos do Bitcoin.
    Fonte: Binance API (/api/v3/klines) — gratuita, sem autenticação.
    Fallback: Lança TechnicalDataError após 3 tentativas falhadas.
    """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    def _fetch_klines(self) -> list:
        """Busca 100 velas diárias da Binance. Retry com backoff exponencial."""
        url = f"{settings.BINANCE_BASE_URL}/api/v3/klines"
        params = {
            "symbol": settings.SYMBOL,
            "interval": "1d",
            "limit": 100
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TechnicalDataError(f"Timeout ao chamar Binance API ({url})")
        except requests.exceptions.HTTPError as e:
            raise TechnicalDataError(f"HTTP {e.response.status_code} em Binance API")
        except Exception as e:
            raise TechnicalDataError(f"Erro inesperado em Binance API: {str(e)}")

    def get_data(self) -> dict:
        """
        Retorna dict com todos os indicadores técnicos.
        """
        try:
            klines = self._fetch_klines()

            # DataFrame setup
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)

            # Indicadores usando a biblioteca `ta`
            df["RSI_14"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
            df["SMA_20"] = ta.trend.SMAIndicator(close=df["close"], window=20).sma_indicator()
            df["SMA_50"] = ta.trend.SMAIndicator(close=df["close"], window=50).sma_indicator()
            
            macd = ta.trend.MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
            df["MACD_12_26_9"] = macd.macd()
            df["MACDs_12_26_9"] = macd.macd_signal()
            
            bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
            df["BBU_20_2.0"] = bb.bollinger_hband()
            df["BBL_20_2.0"] = bb.bollinger_lband()
            
            atr = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14)
            df["ATRr_14"] = atr.average_true_range()

            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]

            # Nomes das colunas geradas
            macd_line_col = "MACD_12_26_9"
            macd_signal_col = "MACDs_12_26_9"

            # MACD bullish cross: MACD line cruza acima da Signal line
            macd_cross_bullish = bool(
                prev_row[macd_line_col] < prev_row[macd_signal_col] and
                last_row[macd_line_col] > last_row[macd_signal_col]
            )

            result = {
                "price_close": float(last_row["close"]),
                "rsi_14": float(last_row["RSI_14"]),
                "sma_20": float(last_row["SMA_20"]),
                "sma_50": float(last_row["SMA_50"]),
                "macd_value": float(last_row[macd_line_col]),
                "macd_signal": float(last_row[macd_signal_col]),
                "macd_cross_bullish": macd_cross_bullish,
                "bb_upper": float(last_row["BBU_20_2.0"]),
                "bb_lower": float(last_row["BBL_20_2.0"]),
                "atr_14": float(last_row["ATRr_14"]),
            }

            logger.info(f"TechnicalEngine: price_close={result['price_close']}, rsi={result['rsi_14']:.1f}")
            return result

        except TechnicalDataError:
            raise
        except Exception as e:
            raise TechnicalDataError(f"Falha ao obter dados técnicos: {str(e)}")


if __name__ == "__main__":
    engine = TechnicalEngine()
    print(engine.get_data())
