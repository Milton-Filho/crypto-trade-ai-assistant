from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from lib.types import SuccessResponse, ErrorResponse
from config import settings

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/trigger", response_model=SuccessResponse, responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
def trigger_daily_job(background_tasks: BackgroundTasks, x_dev_key: str = Header(None, alias="X-Dev-Key")):
    """
    Dispara o daily_job manualmente em background. Apenas para desenvolvimento.
    
    Exemplo curl:
    curl -X POST http://localhost:8000/jobs/trigger \
         -H "X-Dev-Key: sua_chave_secreta"
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403, 
            detail={"error": "Endpoint desabilitado em produção", "code": "FORBIDDEN"}
        )
    
    if not settings.DEV_API_KEY or x_dev_key != settings.DEV_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail={"error": "API Key inválida ou não fornecida", "code": "UNAUTHORIZED"}
        )
    
    # Importação local para evitar problemas de dependência circular ou carregamento
    from jobs.daily_job import run as run_daily_job
    
    # Adicionar à background task (FastAPI suporta funções async nativamente)
    background_tasks.add_task(run_daily_job)
    
    return {"success": True, "message": "Daily job disparado em background"}
