import asyncio
import logging
import sys
import os

# Ajustar o path para poder importar os módulos quando executado directamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.technical_engine import TechnicalEngine
from engines.onchain_engine import OnchainEngine
from engines.sentiment_engine import SentimentEngine
from core.signal_engine import SignalEngine
from core.risk_manager import RiskManager
from core.ai_analyst import AIAnalyst
from integrations.supabase_client import SupabaseClient
from integrations.telegram_bot import TelegramBot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("daily_job")

# Exemplo de output esperado:
# 2025-03-29 01:00:00 - daily_job - INFO - Iniciando Daily Job...
# 2025-03-29 01:00:01 - daily_job - INFO - [1/5] Colectando dados das engines...
# 2025-03-29 01:00:03 - daily_job - INFO - [2/5] Calculando sinal e risco...
# 2025-03-29 01:00:03 - daily_job - INFO - Sinal gerado: VERDE (Score: 7/9)
# 2025-03-29 01:00:03 - daily_job - INFO - [3/5] Gerando relatório com IA...
# 2025-03-29 01:00:08 - daily_job - INFO - [4/5] Persistindo no Supabase...
# 2025-03-29 01:00:09 - daily_job - INFO - [5/5] Enviando alerta Telegram...
# 2025-03-29 01:00:10 - daily_job - INFO - Daily Job concluído com sucesso.

async def run():
    logger.info("Iniciando Daily Job...")
    bot = TelegramBot()
    db = SupabaseClient()
    
    error_log = None
    
    try:
        # 1. Coleta de dados
        logger.info("[1/5] Colectando dados das engines...")
        
        tech_engine = TechnicalEngine()
        onchain_engine = OnchainEngine()
        sentiment_engine = SentimentEngine()
        
        # Executar sync (requests não é async por defeito, mas podemos envolver em threads se necessário.
        # Para simplificar e manter a robustez, executamos sequencialmente ou usamos asyncio.to_thread)
        tech_data = await asyncio.to_thread(tech_engine.get_data)
        onchain_data = await asyncio.to_thread(onchain_engine.get_data)
        sentiment_data = await asyncio.to_thread(sentiment_engine.get_data)
        
        # 2. Score e sinal
        logger.info("[2/5] Calculando sinal e risco...")
        signal_engine = SignalEngine()
        signal_result = signal_engine.calculate(tech_data, onchain_data, sentiment_data)
        
        logger.info(f"Sinal gerado: {signal_result['signal']} (Score: {signal_result['confluence_score']}/9)")
        
        # 3. Gestão de risco
        risk_manager = RiskManager()
        risk_result = risk_manager.calculate(
            price_close=tech_data["price_close"],
            atr_14=tech_data["atr_14"],
            signal=signal_result["signal"]
        )
        
        # 4. Relatório da IA
        logger.info("[3/5] Gerando relatório com IA...")
        ai_analyst = AIAnalyst()
        
        # Montar payload para a IA
        ai_payload = {
            **tech_data,
            **onchain_data,
            **sentiment_data,
            **signal_result,
            **risk_result
        }
        
        ai_report = await ai_analyst.generate(ai_payload)
        
        # 5. Persistência
        logger.info("[4/5] Persistindo no Supabase...")
        full_payload = {
            **ai_payload,
            **ai_report,
            "error_log": error_log
        }
        
        record_id = None
        try:
            record_id = db.save_daily_analysis(full_payload)
        except Exception as e:
            logger.error(f"Falha ao persistir no Supabase: {e}")
            error_log = str(e)
            # Não falhamos o job inteiro se o DB falhar, tentamos enviar o Telegram na mesma
            
        # 6. Notificação
        logger.info("[5/5] Enviando alerta Telegram...")
        if signal_result["signal"] != "AMARELO":
            success = bot.send_execution_alert(full_payload)
            if success and record_id:
                db.mark_telegram_sent(record_id)
        else:
            logger.info("Sinal AMARELO. Alerta Telegram ignorado.")
            
        logger.info("Daily Job concluído com sucesso.")
        
    except Exception as e:
        logger.exception("Erro crítico no Daily Job")
        bot.send_error_alert(f"Daily Job falhou: {str(e)}")
        
        # Tentar registar o erro no DB se falhou antes da persistência
        try:
            db.save_daily_analysis({"error_log": str(e), "signal": "AMARELO", "confluence_score": 0})
        except:
            pass

if __name__ == "__main__":
    asyncio.run(run())
