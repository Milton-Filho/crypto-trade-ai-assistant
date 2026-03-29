import json
import re
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tenacity import retry, stop_after_attempt, wait_fixed
import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)


class AIAnalystError(Exception):
    pass


class AIAnalyst:
    """
    Monta o payload completo, chama o Gemini e recebe o relatório.
    O prompt é carregado de prompts/daily_report_v1.txt — imutável em runtime.
    Fallback: Retorna dict com mensagens de erro para não bloquear o pipeline.
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY não configurada. O AIAnalyst irá falhar se invocado.")

        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def _load_prompt(self) -> str:
        """Carrega o prompt versionado de backend/prompts/daily_report_v1.txt."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts", "daily_report_v1.txt"
        )
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise AIAnalystError(f"Ficheiro de prompt não encontrado: {prompt_path}")
        except Exception as e:
            raise AIAnalystError(f"Falha ao ler prompt: {str(e)}")

    def _parse_response(self, text: str) -> dict:
        """Tenta fazer parse do JSON, lidando com possíveis blocos de markdown."""
        if not text:
            raise ValueError("Resposta vazia do Gemini")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: tentar extrair JSON com regex
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            raise ValueError("Falha ao parsear JSON da resposta do Gemini.")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2), reraise=True)
    def _call_gemini(self, full_prompt: str) -> dict:
        """Chama a API do Gemini com retry embutido."""
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
        except Exception as e:
            raise AIAnalystError(f"Erro ao chamar Gemini API: {str(e)}")

        # Log token usage if available
        try:
            usage = response.usage_metadata
            if usage:
                logger.info(
                    f"Gemini Tokens — Prompt: {usage.prompt_token_count}, "
                    f"Candidates: {usage.candidates_token_count}, "
                    f"Total: {usage.total_token_count}"
                )
        except Exception:
            pass

        report = self._parse_response(response.text)

        # Validar campos obrigatórios
        required_fields = ["technical", "onchain", "sentiment", "verdict"]
        for field in required_fields:
            if field not in report or not str(report[field]).strip():
                raise ValueError(f"Campo obrigatório '{field}' ausente ou vazio na resposta.")

        return report

    async def generate(self, payload: dict) -> dict:
        """
        Gera o relatório diário. Em caso de falha total, retorna dict com
        mensagens de erro para não bloquear o resto do pipeline.

        Output:
        {
            "technical": str,
            "onchain": str,
            "sentiment": str,
            "verdict": str
        }
        """
        try:
            base_prompt = self._load_prompt()
            full_prompt = f"{base_prompt}\n{json.dumps(payload, indent=2)}"

            logger.info(f"A chamar Gemini ({self.model_name})...")
            report = self._call_gemini(full_prompt)
            return report

        except Exception as e:
            logger.error(f"Erro total ao gerar relatório com IA: {str(e)}")
            error_msg = f"Falha ao gerar análise com IA: {str(e)}"
            return {
                "technical": error_msg,
                "onchain": error_msg,
                "sentiment": error_msg,
                "verdict": error_msg,
            }
