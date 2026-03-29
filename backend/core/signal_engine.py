import logging

logger = logging.getLogger(__name__)


class SignalEngine:
    """
    Calcula o score de confluência (0–9) e determina o sinal final.
    Lógica conforme SPECS.md seção 3.4 e agents.md.
    """

    def calculate(self, tech: dict, onchain: dict, sentiment: dict) -> dict:
        """
        Avalia os dados e retorna o score (0–9), sinal e breakdown.

        Output conforme agents.md:
        {
            "confluence_score": int,
            "signal": str,
            "score_breakdown": {"rsi": int, "bollinger": int, "macd": int, "sma": int, "fear_greed": int, "onchain": int}
        }
        """
        score = 0
        breakdown = {
            "rsi": 0,
            "bollinger": 0,
            "macd": 0,
            "sma": 0,
            "fear_greed": 0,
            "onchain": 0,
        }

        # --- Análise Técnica (máx: 6 pontos) ---

        # RSI < 35 → +2
        if tech.get("rsi_14", 50) < 35:
            score += 2
            breakdown["rsi"] = 2

        # Preço <= Banda Inferior → +2
        if tech.get("price_close", 0) <= tech.get("bb_lower", -1):
            score += 2
            breakdown["bollinger"] = 2

        # MACD Cruzamento Bullish → +1
        if tech.get("macd_cross_bullish", False):
            score += 1
            breakdown["macd"] = 1

        # SMA 20 > SMA 50 → +1
        if tech.get("sma_20", 0) > tech.get("sma_50", 0):
            score += 1
            breakdown["sma"] = 1

        # --- Sentimento (máx: 2 pontos) ---

        # Fear & Greed < 25 → +2
        if sentiment.get("fear_greed_score", 50) < 25:
            score += 2
            breakdown["fear_greed"] = 2

        # --- On-Chain (máx: 1 ponto) ---

        # Network Health == SAUDAVEL → +1
        if onchain.get("network_health") == "SAUDAVEL":
            score += 1
            breakdown["onchain"] = 1

        # --- Determinação do Sinal ---
        if score >= 6:
            signal = "VERDE"
        elif score <= 3:
            signal = "VERMELHO"
        else:
            signal = "AMARELO"

        logger.info(f"SignalEngine: score={score}/9, signal={signal}, breakdown={breakdown}")

        return {
            "confluence_score": score,
            "signal": signal,
            "score_breakdown": breakdown,
        }


if __name__ == "__main__":
    engine = SignalEngine()
    tech_mock = {
        "rsi_14": 30, "price_close": 49000, "bb_lower": 50000,
        "macd_cross_bullish": True, "sma_20": 51000, "sma_50": 50000
    }
    onchain_mock = {"network_health": "SAUDAVEL"}
    sentiment_mock = {"fear_greed_score": 20}
    print(engine.calculate(tech_mock, onchain_mock, sentiment_mock))
