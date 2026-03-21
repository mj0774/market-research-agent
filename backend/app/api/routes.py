from fastapi import APIRouter

from app.schemas.analyze import AnalyzeRequest
from app.services import run_market_research_pipeline


router = APIRouter()


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    """마켓 리서치 파이프라인을 실행하고 결과를 반환합니다.

    Args:
        payload: company_name을 담고 있는 요청 본문입니다.

    Returns:
        dict: company_name, search_results, documents, analysis를 포함한 결과입니다.
    """
    # 엔드투엔드 처리(search->filter->scrape->analyze)는 파이프라인 서비스에 위임합니다.
    result = run_market_research_pipeline(payload.company_name)
    return result
