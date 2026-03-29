import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)


class OnchainDataError(Exception):
    pass


class OnchainEngine:
    """
    Engine para colecta de dados on-chain do Bitcoin.
    Fontes: Blockchain.com API + Mempool.space API.
    Fallback: Retorna dados parciais com flag partial=True.
    """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    def _fetch_blockchain_stats(self) -> dict:
        """Busca stats gerais da rede Bitcoin via Blockchain.com."""
        url = f"{settings.BLOCKCHAIN_BASE_URL}/stats"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise OnchainDataError("Timeout ao chamar Blockchain.com API")
        except requests.exceptions.HTTPError as e:
            raise OnchainDataError(f"HTTP {e.response.status_code} em Blockchain.com API")
        except Exception as e:
            raise OnchainDataError(f"Erro inesperado em Blockchain.com API: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    def _fetch_mempool_fees(self) -> dict:
        """Busca fee rates via Mempool.space."""
        url = f"{settings.MEMPOOL_BASE_URL}/v1/fees/recommended"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise OnchainDataError("Timeout ao chamar Mempool.space API")
        except requests.exceptions.HTTPError as e:
            raise OnchainDataError(f"HTTP {e.response.status_code} em Mempool.space API")
        except Exception as e:
            raise OnchainDataError(f"Erro inesperado em Mempool.space API: {str(e)}")

    def get_data(self) -> dict:
        """
        Retorna dict com dados on-chain conforme SPECS.md seção 3.2.

        Output:
        {
            "tx_volume_btc": float,
            "tx_count": int,
            "hash_rate_th": float,
            "mempool_fee_fastest": int,
            "network_health": str,  # "SAUDAVEL" | "CONGESTAO" | "LENTA" | "DESCONHECIDO"
            "partial": bool
        }
        """
        data = {
            "tx_volume_btc": 0.0,
            "tx_count": 0,
            "hash_rate_th": 0.0,
            "mempool_fee_fastest": 0,
            "network_health": "DESCONHECIDO",
            "partial": False,
        }

        # --- Blockchain.com ---
        try:
            stats = self._fetch_blockchain_stats()
            # trade_volume_btc: volume em BTC nas últimas 24h
            data["tx_volume_btc"] = float(stats.get("trade_volume_btc", 0))
            data["tx_count"] = int(stats.get("n_tx", 0))
            data["hash_rate_th"] = float(stats.get("hash_rate", 0)) / 1e12  # Converter para TH/s
        except Exception as e:
            logger.warning(f"Blockchain.com falhou: {e}. Dados parciais.")
            data["partial"] = True

        # --- Mempool.space ---
        try:
            fees = self._fetch_mempool_fees()
            data["mempool_fee_fastest"] = int(fees.get("fastestFee", 0))
        except Exception as e:
            logger.warning(f"Mempool.space falhou: {e}. network_health = DESCONHECIDO.")
            data["partial"] = True

        # --- Determinação do network_health ---
        # Lógica conforme SPECS.md seção 3.2
        if data["mempool_fee_fastest"] > 80:
            data["network_health"] = "CONGESTAO"
        elif data["hash_rate_th"] > 0 and data["tx_count"] > 250000:
            data["network_health"] = "SAUDAVEL"
        elif data["partial"]:
            data["network_health"] = "DESCONHECIDO"
        else:
            data["network_health"] = "LENTA"

        # Falha total: ambas as fontes falharam
        if data["partial"] and data["hash_rate_th"] == 0.0 and data["mempool_fee_fastest"] == 0:
            raise OnchainDataError("Falha total ao obter dados on-chain (Blockchain.com + Mempool.space).")

        logger.info(f"OnchainEngine: health={data['network_health']}, tx_count={data['tx_count']}, partial={data['partial']}")
        return data


if __name__ == "__main__":
    engine = OnchainEngine()
    print(engine.get_data())
