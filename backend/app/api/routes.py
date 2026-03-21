from fastapi import APIRouter, HTTPException

from app.schemas.analyze import AnalyzeRequest
from app.tools.search import search_company


router = APIRouter()


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        results = search_company(payload.company_name)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "company_name": payload.company_name,
        "results": results,
    }
