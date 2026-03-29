import logging
import sys
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

from integrations.supabase_client import SupabaseClient
from integrations.telegram_bot import TelegramBot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("watcher_job")

# Exemplo de output esperado:
# 2025-03-29 11:00:00 - watcher_job - INFO - Iniciando Watcher Job...
# 2025-03-29 11:00:01 - watcher_job - INFO - Análise de hoje encontrada. Sinal: VERDE.
# 2025-03-29 11:00:02 - watcher_job - INFO - Preço actual: $105000. Variação: +1.74%. Threshold: 5.0%.
# 2025-03-29 11:00:02 - watcher_job - INFO - Variação abaixo do threshold. Nenhuma acção necessária.

def fetch_current_price(symbol: str = "BTCUSDT") -> float:
    """Busca o preço actual via GET simples à Binance ticker endpoint."""
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return float(response.json()["price"])

def is_active_hours() -> bool:
    """Verifica se a hora actual em Lisboa está entre 07:00 e 23:00."""
    now_lisbon = datetime.now(ZoneInfo('Europe/Lisbon'))
    return 7 <= now_lisbon.hour < 23

def run():
    logger.info("Iniciando Watcher Job...")
    
    if not is_active_hours():
        logger.info("Fora do horário activo (07:00-23:00 Lisboa). Watcher suspenso.")
        return

    db = SupabaseClient()
    bot = TelegramBot()
    
    try:
        # 1. Obter análise de hoje
        today_analysis = db.get_today_analysis()
        
        if not today_analysis:
            logger.info("Nenhuma análise encontrada para hoje. Watcher suspenso.")
            return
            
        signal = today_analysis.get("signal")
        if signal == "AMARELO":
            logger.info("Sinal de hoje é AMARELO. Nada a monitorizar.")
            return
            
        outcome = today_analysis.get("outcome")
        if outcome in ["TP_HIT", "SL_HIT", "MANUAL"]:
            logger.info(f"Operação já fechada (Outcome: {outcome}). Watcher suspenso.")
            return

        # 2. Obter configurações e preço actual
        db_settings = db.get_settings()
        threshold = float(db_settings.get("intraday_threshold", 5.0))
        symbol = db_settings.get("symbol", "BTCUSDT")
        
        current_price = fetch_current_price(symbol)
        entry_price = float(today_analysis.get("price_entry", 0))
        take_profit = float(today_analysis.get("take_profit", 0))
        stop_loss = float(today_analysis.get("stop_loss", 0))
        record_id = today_analysis.get("id")
        
        if entry_price == 0:
            logger.warning("Preço de entrada é 0. Abortando.")
            return
            
        change_pct = ((current_price - entry_price) / entry_price) * 100
        
        logger.info(f"Análise de hoje encontrada. Sinal: {signal}.")
        logger.info(f"Preço actual: ${current_price:.2f}. Variação: {change_pct:+.2f}%. Threshold: {threshold}%.")
        
        # 3. Verificar se TP ou SL foi atingido (Auto-update)
        hit_outcome = None
        if signal == "VERDE":
            if current_price >= take_profit:
                hit_outcome = "TP_HIT"
            elif current_price <= stop_loss:
                hit_outcome = "SL_HIT"
        elif signal == "VERMELHO":
            if current_price <= take_profit:
                hit_outcome = "TP_HIT"
            elif current_price >= stop_loss:
                hit_outcome = "SL_HIT"
                
        if hit_outcome:
            logger.info(f"Alvo atingido: {hit_outcome}! Actualizando outcome no banco...")
            db.update_outcome(record_id, hit_outcome, current_price, "Atingido automaticamente", "AUTO")
            bot.send_intraday_alert(current_price, entry_price, change_pct) # Enviar alerta de fecho
            return

        # 4. Verificar variação intraday (Alerta leve)
        if abs(change_pct) >= threshold:
            logger.info(f"Variação >= threshold ({threshold}%). Enviando alerta intraday...")
            bot.send_intraday_alert(current_price, entry_price, change_pct)
        else:
            logger.info("Variação abaixo do threshold. Nenhuma acção necessária.")
            
    except Exception as e:
        logger.exception("Erro crítico no Watcher Job")
        bot.send_error_alert(f"Watcher Job falhou: {str(e)}")

if __name__ == "__main__":
    run()
