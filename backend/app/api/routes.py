from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest
from app.services import run_market_research_pipeline


router = APIRouter()


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    result = run_market_research_pipeline(payload.company_name)
    return result
