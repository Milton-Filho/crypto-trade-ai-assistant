from fastapi import APIRouter, HTTPException, Query
from typing import List
from lib.types import DailyAnalysisResponse, ErrorResponse
from integrations.supabase_client import SupabaseClient

router = APIRouter(prefix="/analysis", tags=["Analysis"])
db = SupabaseClient()

@router.get("/today", response_model=DailyAnalysisResponse, responses={404: {"model": ErrorResponse}})
def get_today_analysis():
    """
    Retorna a análise do dia actual.
    
    Exemplo curl:
    curl -X GET http://localhost:8000/analysis/today
    """
    data = db.get_today_analysis()
    if not data:
        raise HTTPException(
            status_code=404, 
            detail={"error": "Análise de hoje não encontrada", "code": "NOT_FOUND"}
        )
    return data

@router.get("/history", response_model=List[DailyAnalysisResponse])
def get_history(days: int = Query(30, ge=1, le=365)):
    """
    Retorna o histórico de análises dos últimos N dias.
    
    Exemplo curl:
    curl -X GET "http://localhost:8000/analysis/history?days=7"
    """
    data = db.get_history(days=days)
    return data
