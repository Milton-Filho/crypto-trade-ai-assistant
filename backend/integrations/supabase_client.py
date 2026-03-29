import logging
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)


class SupabaseClientError(Exception):
    pass


class SupabaseClient:
    """
    Cliente para interagir com o Supabase via REST API (supabase-py).
    Fallback: Lança SupabaseClientError com mensagem descritiva.
    """

    def __init__(self):
        url = settings.SUPABASE_URL
        key = settings.supabase_key  # Usa a property que resolve SERVICE_KEY ou SERVICE_ROLE_KEY

        if not url or not key:
            logger.warning("Credenciais do Supabase não configuradas (SUPABASE_URL ou SUPABASE_SERVICE_KEY).")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def _check_client(self):
        if not self.client:
            raise SupabaseClientError("Cliente Supabase não inicializado. Verifique SUPABASE_URL e SUPABASE_SERVICE_KEY.")

    def save_daily_analysis(self, payload: dict) -> str:
        """
        Insere ou actualiza o registo do dia (upsert por data).
        Retorna o UUID do registo.
        """
        self._check_client()

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info(f"A guardar análise diária para {today}...")

        # Mapeamento do payload para o schema do banco (conforme PRD seção 12)
        db_payload = {
            "date": today,
            "symbol": settings.SYMBOL,

            # Preços e Risco
            "price_close": payload.get("price_close"),
            "price_entry": payload.get("price_entry"),
            "stop_loss": payload.get("stop_loss"),
            "take_profit": payload.get("take_profit"),
            "rr_ratio": payload.get("rr_ratio"),
            "sl_percent": payload.get("sl_percent"),
            "tp_percent": payload.get("tp_percent"),
            "atr_14": payload.get("atr_14"),

            # Técnico
            "rsi_14": payload.get("rsi_14"),
            "sma_20": payload.get("sma_20"),
            "sma_50": payload.get("sma_50"),
            "macd_value": payload.get("macd_value"),
            "macd_signal": payload.get("macd_signal"),
            "bb_upper": payload.get("bb_upper"),
            "bb_lower": payload.get("bb_lower"),

            # On-Chain (nomes alinhados com schema SQL)
            "tx_volume": payload.get("tx_volume_btc"),
            "tx_count": payload.get("tx_count"),
            "hash_rate": payload.get("hash_rate_th"),
            "mempool_fee": payload.get("mempool_fee_fastest"),
            "network_health": payload.get("network_health"),

            # Sentimento
            "fear_greed_score": payload.get("fear_greed_score"),
            "fear_greed_label": payload.get("fear_greed_label"),
            "news_headlines": payload.get("news_headlines", []),

            # Sinal
            "confluence_score": payload.get("confluence_score"),
            "signal": payload.get("signal"),
            "score_breakdown": payload.get("score_breakdown"),

            # IA Report
            "ai_report_technical": payload.get("technical"),
            "ai_report_onchain": payload.get("onchain"),
            "ai_report_sentiment": payload.get("sentiment"),
            "ai_report_verdict": payload.get("verdict"),
            "ai_model": settings.GEMINI_MODEL,

            # Estado inicial da operação
            "outcome": "OPEN" if payload.get("signal") != "AMARELO" else "N/A",

            # Sistema
            "error_log": payload.get("error_log"),
        }

        # Remover chaves com valor None para não sobrescrever defaults do DB com nulls indesejados
        db_payload = {k: v for k, v in db_payload.items() if v is not None}

        try:
            # Upsert usando 'date' como chave de conflito (coluna 'date' é UNIQUE no DB)
            response = self.client.table("daily_analysis").upsert(
                db_payload, on_conflict="date"
            ).execute()

            if not response.data:
                raise SupabaseClientError("Nenhum dado retornado após upsert.")

            record_id = response.data[0]["id"]
            logger.info(f"Análise guardada com sucesso. ID: {record_id}")
            return record_id

        except SupabaseClientError:
            raise
        except Exception as e:
            logger.error(f"Erro ao guardar análise no Supabase: {str(e)}")
            raise SupabaseClientError(f"Falha no upsert: {str(e)}")

    def get_today_analysis(self) -> dict | None:
        """Retorna o registo de hoje ou None."""
        self._check_client()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            response = self.client.table("daily_analysis").select("*").eq("date", today).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar análise de hoje: {str(e)}")
            return None

    def get_history(self, days: int = 30) -> list[dict]:
        """Retorna os últimos N dias ordenados por data decrescente."""
        self._check_client()
        try:
            response = self.client.table("daily_analysis").select("*").order("date", desc=True).limit(days).execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {str(e)}")
            return []

    def update_outcome(self, id: str, outcome: str, price: float, note: str, source: str = "AUTO") -> bool:
        """Actualiza o resultado de uma operação (manual ou automático)."""
        self._check_client()
        try:
            payload = {
                "outcome": outcome,
                "outcome_price": price,
                "outcome_note": note,
                "outcome_source": source,
            }
            response = self.client.table("daily_analysis").update(payload).eq("id", id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao actualizar outcome para {id}: {str(e)}")
            return False

    def get_settings(self) -> dict:
        """Retorna as configurações actuais. Cria default se não existir."""
        self._check_client()
        try:
            response = self.client.table("settings").select("*").limit(1).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]

            # Se não existir, cria uma default
            default_settings = {
                "intraday_threshold": 5.0,
                "symbol": settings.SYMBOL,
                "cron_time_utc": "01:00",
            }
            res = self.client.table("settings").insert(default_settings).execute()
            return res.data[0] if res.data else default_settings
        except Exception as e:
            logger.error(f"Erro ao buscar settings: {str(e)}")
            return {"intraday_threshold": 5.0, "symbol": "BTCUSDT", "cron_time_utc": "01:00"}

    def update_settings(self, payload: dict) -> bool:
        """Actualiza as configurações."""
        self._check_client()
        try:
            current_settings = self.get_settings()
            if "id" in current_settings:
                response = self.client.table("settings").update(payload).eq("id", current_settings["id"]).execute()
                return len(response.data) > 0
            return False
        except Exception as e:
            logger.error(f"Erro ao actualizar settings: {str(e)}")
            return False

    def mark_telegram_sent(self, id: str) -> bool:
        """Marca que o alerta do Telegram foi enviado para este registo."""
        self._check_client()
        try:
            self.client.table("daily_analysis").update({"telegram_sent": True}).eq("id", id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar telegram_sent para {id}: {str(e)}")
            return False
