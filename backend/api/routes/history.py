from fastapi import APIRouter, HTTPException, Path
from lib.types import UpdateOutcomeRequest, SuccessResponse, ErrorResponse
from integrations.supabase_client import SupabaseClient

router = APIRouter(prefix="/analysis", tags=["History"])
db = SupabaseClient()

@router.patch("/{id}/outcome", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
def update_outcome(id: str = Path(...), payload: UpdateOutcomeRequest = ...):
    """
    Actualiza o resultado (outcome) de uma análise específica.
    
    Exemplo curl:
    curl -X PATCH http://localhost:8000/analysis/123e4567-e89b-12d3-a456-426614174000/outcome \
         -H "Content-Type: application/json" \
         -d '{"outcome": "TP_HIT", "price": 71000.0, "note": "Fechado manualmente"}'
    """
    success = db.update_outcome(
        id=id,
        outcome=payload.outcome,
        price=payload.price,
        note=payload.note,
        source="MANUAL"
    )
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail={"error": "Falha ao actualizar outcome ou registo não encontrado", "code": "UPDATE_FAILED"}
        )
        
    return {"success": True, "message": "Outcome actualizado com sucesso"}
