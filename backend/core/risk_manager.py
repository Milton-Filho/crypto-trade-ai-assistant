import math

class RiskManager:
    """
    Calcula os preços exactos de execução com base no ATR (Gestão de Risco).
    """

    def calculate(self, price_close: float, atr_14: float, signal: str) -> dict:
        """
        Calcula Entrada, Stop-Loss, Take-Profit e R/R Ratio.
        """
        if signal not in ["VERDE", "VERMELHO", "AMARELO"]:
            raise ValueError(f"Sinal inválido: {signal}")

        # Para AMARELO, calculamos como se fosse VERDE apenas para referência no UI
        is_bullish = signal in ["VERDE", "AMARELO"]

        price_entry = price_close

        if is_bullish:
            stop_loss = price_close - (atr_14 * 1.5)
            take_profit = price_close + (atr_14 * 3.0)
        else:
            # VERMELHO (Short)
            stop_loss = price_close + (atr_14 * 1.5)
            take_profit = price_close - (atr_14 * 3.0)

        # Arredondar para 2 casas decimais
        stop_loss = round(stop_loss, 2)
        take_profit = round(take_profit, 2)
        price_entry = round(price_entry, 2)

        # R/R Ratio
        risk = abs(price_entry - stop_loss)
        reward = abs(take_profit - price_entry)
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0.0

        # Percentagens
        sl_percent = round(((stop_loss - price_entry) / price_entry) * 100, 2)
        tp_percent = round(((take_profit - price_entry) / price_entry) * 100, 2)

        return {
            "price_entry": price_entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "rr_ratio": rr_ratio,
            "sl_percent": sl_percent,
            "tp_percent": tp_percent
        }

if __name__ == "__main__":
    rm = RiskManager()
    print(rm.calculate(price_close=100000, atr_14=2000, signal="VERDE"))
