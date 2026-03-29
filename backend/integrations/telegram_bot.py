import logging
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from config import settings

logger = logging.getLogger(__name__)


class TelegramBotError(Exception):
    pass


class TelegramBot:
    """
    Cliente para envio de alertas via Telegram Bot API.
    Fallback: Loga o erro e retorna False. Nunca bloqueia o pipeline.
    """

    # Rate limiting em memória (tipo_alerta -> timestamp_ultimo_envio)
    _last_sent = {
        "execution": None,
        "intraday": None,
        "error": None
    }

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.dashboard_url = settings.FRONTEND_URL

        if not self.token or not self.chat_id:
            logger.warning("Credenciais do Telegram não configuradas (TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID).")

    def _check_rate_limit(self, alert_type: str) -> bool:
        """Retorna True se puder enviar (não atingiu o rate limit de 1h)."""
        last_sent = self._last_sent.get(alert_type)
        if not last_sent:
            return True

        if datetime.now() - last_sent > timedelta(hours=1):
            return True

        logger.warning(f"Rate limit atingido para alerta tipo '{alert_type}'. Ignorando envio.")
        return False

    def _update_rate_limit(self, alert_type: str):
        self._last_sent[alert_type] = datetime.now()

    def _send_message(self, text: str, alert_type: str) -> bool:
        """Envia mensagem via Telegram Bot API com rate limiting."""
        if not self.token or not self.chat_id:
            logger.error("Telegram não configurado. Impossível enviar mensagem.")
            return False

        if not self._check_rate_limit(alert_type):
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self._update_rate_limit(alert_type)
            logger.info(f"Alerta '{alert_type}' enviado com sucesso.")
            return True
        except requests.exceptions.Timeout:
            logger.error("Timeout ao enviar mensagem Telegram.")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP {e.response.status_code} ao enviar mensagem Telegram.")
            return False
        except Exception as e:
            logger.error(f"Falha ao enviar mensagem Telegram: {str(e)}")
            return False

    def send_execution_alert(self, analysis: dict) -> bool:
        """Envia alerta de sinal Verde ou Vermelho com preços."""
        signal = analysis.get("signal")
        if signal == "AMARELO":
            logger.info("Sinal AMARELO. Nenhum alerta de execução enviado.")
            return False

        logger.info(f"A enviar alerta de execução ({signal})...")

        emoji = "🟢" if signal == "VERDE" else "🔴"
        symbol = settings.SYMBOL

        entry = analysis.get("price_entry", 0)
        sl = analysis.get("stop_loss", 0)
        tp = analysis.get("take_profit", 0)
        sl_pct = ((sl - entry) / entry * 100) if entry else 0
        tp_pct = ((tp - entry) / entry * 100) if entry else 0
        rr = analysis.get("rr_ratio", 0)
        score = analysis.get("confluence_score", 0)

        # Construir resumo do breakdown (agora são ints, não strings)
        breakdown = analysis.get("score_breakdown", {})
        label_map = {
            "rsi": "RSI em zona extrema",
            "bollinger": "Preço na banda Bollinger",
            "macd": "Cruzamento MACD bullish",
            "sma": "Tendência SMA 20 > 50",
            "fear_greed": "Fear & Greed extremo",
            "onchain": "Rede Bitcoin saudável",
        }
        reasons = [label_map[k] for k, v in breakdown.items() if v > 0 and k in label_map]
        reasons_text = "\n  + ".join(reasons) if reasons else "Confluência técnica e on-chain"

        msg = f"""
{emoji} <b>SINAL DE { 'COMPRA' if signal == 'VERDE' else 'VENDA' } — {symbol}</b>

📥 <b>Entrada:</b>     ${entry:,.2f}
🛑 <b>Stop-Loss:</b>   ${sl:,.2f} ({sl_pct:+.1f}%)
🎯 <b>Take-Profit:</b> ${tp:,.2f} ({tp_pct:+.1f}%)
⚖️  <b>R/R:</b> 1:{rr} | <b>Score:</b> {score}/9

→ <b>Confluência:</b>
  + {reasons_text}

Ver relatório completo: <a href="{self.dashboard_url}">{self.dashboard_url}</a>
"""
        return self._send_message(msg.strip(), "execution")

    def send_intraday_alert(self, current_price: float, entry_price: float, change_pct: float) -> bool:
        """Envia alerta leve de variação intraday >= threshold."""
        logger.info("A enviar alerta intraday...")
        symbol = settings.SYMBOL

        direction = "subiu" if change_pct > 0 else "desceu"
        emoji = "🚀" if change_pct > 0 else "🩸"

        msg = f"""
⚠️ <b>ALERTA DE MOVIMENTO — {symbol}</b>

{emoji} O preço <b>{direction} {abs(change_pct):.1f}%</b> desde o sinal de hoje.

<b>Preço atual:</b> ${current_price:,.2f}
<b>Entrada:</b> ${entry_price:,.2f}

Considere rever a posição no <a href="{self.dashboard_url}">Dashboard</a>.
"""
        return self._send_message(msg.strip(), "intraday")

    def send_error_alert(self, message: str) -> bool:
        """Envia alerta de erro do sistema."""
        logger.info("A enviar alerta de erro...")
        msg = f"""
🚨 <b>ERRO NO SISTEMA (Crypto Trade AI)</b>

Ocorreu uma falha crítica:
<code>{message}</code>

Verifique os logs no Render.
"""
        return self._send_message(msg.strip(), "error")
