from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from lib.types import SuccessResponse, ErrorResponse
from config import settings

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/trigger", response_model=SuccessResponse, responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
def trigger_daily_job(background_tasks: BackgroundTasks, x_dev_key: str = Header(None, alias="X-Dev-Key")):
    """
    Dispara o daily_job manualmente em background.
    Agora permitido em produção para suporte a cron jobs externos (cron-job.org).
    
    Exemplo curl:
    curl -X POST https://sua-api.onrender.com/jobs/trigger \
         -H "X-Dev-Key: sua_chave_secreta"
    """
    if not settings.DEV_API_KEY or x_dev_key != settings.DEV_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail={"error": "API Key inválida ou não fornecida", "code": "UNAUTHORIZED"}
        )
    
    # Importação local para evitar problemas de dependência circular
    from jobs.daily_job import run as run_daily_job
    
    # Adicionar à background task
    background_tasks.add_task(run_daily_job)
    
    return {"success": True, "message": "Daily job disparado em background"}

@router.post("/watcher", response_model=SuccessResponse, responses={401: {"model": ErrorResponse}})
def trigger_watcher_job(background_tasks: BackgroundTasks, x_dev_key: str = Header(None, alias="X-Dev-Key")):
    """
    Dispara o watcher_job (monitoramento intraday) em background via cron externo.
    """
    if not settings.DEV_API_KEY or x_dev_key != settings.DEV_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail={"error": "API Key inválida ou não fornecida", "code": "UNAUTHORIZED"}
        )
    
    from jobs.watcher_job import run as run_watcher_job
    
    # watcher_job não é async nativo, mas usamos as threads do FastAPI
    background_tasks.add_task(run_watcher_job)
    
    return {"success": True, "message": "Watcher job disparado em background"}
