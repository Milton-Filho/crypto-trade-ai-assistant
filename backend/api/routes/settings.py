from fastapi import APIRouter, HTTPException
from lib.types import SettingsResponse, UpdateSettingsRequest, SuccessResponse, ErrorResponse
from integrations.supabase_client import SupabaseClient

router = APIRouter(prefix="/settings", tags=["Settings"])
db = SupabaseClient()

@router.get("", response_model=SettingsResponse)
def get_settings():
    """
    Retorna as configurações actuais do sistema.
    
    Exemplo curl:
    curl -X GET http://localhost:8000/settings
    """
    data = db.get_settings()
    return data

@router.put("", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}})
def update_settings(payload: UpdateSettingsRequest):
    """
    Actualiza as configurações do sistema.
    
    Exemplo curl:
    curl -X PUT http://localhost:8000/settings \
         -H "Content-Type: application/json" \
         -d '{"intraday_threshold": 5.0, "symbol": "BTCUSDT", "cron_time_utc": "01:00"}'
    """
    # Compatibilidade com Pydantic v1 e v2
    payload_dict = payload.model_dump(exclude_unset=True) if hasattr(payload, 'model_dump') else payload.dict(exclude_unset=True)
    
    success = db.update_settings(payload_dict)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail={"error": "Falha ao actualizar configurações", "code": "UPDATE_FAILED"}
        )
        
    return {"success": True, "message": "Configurações actualizadas com sucesso"}
