import logging
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)


class SentimentDataError(Exception):
    pass


class SentimentEngine:
    """
    Engine para colecta de dados de sentimento e notícias do Bitcoin.
    Fontes: Alternative.me Fear & Greed Index + NewsAPI.org.
    Fallback: Lança SentimentDataError após 3 tentativas falhadas.
    """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    def _fetch_fear_greed(self) -> dict:
        """Busca Fear & Greed Index via Alternative.me."""
        url = f"{settings.FEAR_GREED_URL}?limit=1"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise SentimentDataError("Timeout ao chamar Fear & Greed API")
        except requests.exceptions.HTTPError as e:
            raise SentimentDataError(f"HTTP {e.response.status_code} em Fear & Greed API")
        except Exception as e:
            raise SentimentDataError(f"Erro inesperado em Fear & Greed API: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    def _fetch_news(self) -> dict:
        """Busca manchetes relevantes via NewsAPI."""
        if not settings.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY não configurada. Retornando manchetes vazias.")
            return {"articles": []}

        url = f"{settings.NEWS_BASE_URL}/everything"
        params = {
            "q": "Bitcoin OR cryptocurrency OR Federal Reserve",
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5,
            "from": (datetime.now() - timedelta(hours=24)).isoformat(),
            "apiKey": settings.NEWS_API_KEY,
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise SentimentDataError("Timeout ao chamar NewsAPI")
        except requests.exceptions.HTTPError as e:
            raise SentimentDataError(f"HTTP {e.response.status_code} em NewsAPI")
        except Exception as e:
            raise SentimentDataError(f"Erro inesperado em NewsAPI: {str(e)}")

    @staticmethod
    def _classify_fear_greed(score: int) -> str:
        """
        Classifica o score conforme SPECS.md seção 3.3.
        0–24  → COMPRA_HISTORICA
        25–74 → NEUTRO
        75–100 → VENDA_HISTORICA
        """
        if score <= 24:
            return "COMPRA_HISTORICA"
        elif score >= 75:
            return "VENDA_HISTORICA"
        return "NEUTRO"

    def get_data(self) -> dict:
        """
        Retorna dict com dados de sentimento conforme SPECS.md seção 3.3.

        Output:
        {
            "fear_greed_score": int,
            "fear_greed_label": str,
            "fear_greed_context": str,
            "news_headlines": list[str]
        }
        """
        try:
            fng_data = self._fetch_fear_greed()
            news_data = self._fetch_news()

            fng_score = int(fng_data["data"][0]["value"])
            fng_label = fng_data["data"][0]["value_classification"]
            fng_context = self._classify_fear_greed(fng_score)

            articles = news_data.get("articles", [])
            news_headlines = [article["title"] for article in articles[:3] if article.get("title")]

            result = {
                "fear_greed_score": fng_score,
                "fear_greed_label": fng_label,
                "fear_greed_context": fng_context,
                "news_headlines": news_headlines,
            }

            logger.info(f"SentimentEngine: fng={fng_score} ({fng_label}), context={fng_context}, headlines={len(news_headlines)}")
            return result

        except SentimentDataError:
            raise
        except Exception as e:
            raise SentimentDataError(f"Falha ao obter dados de sentimento: {str(e)}")


if __name__ == "__main__":
    engine = SentimentEngine()
    print(engine.get_data())
