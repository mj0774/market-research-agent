from fastapi import APIRouter

from app.agents.graph import get_graph
from app.schemas.analyze import AnalyzeRequest


router = APIRouter()


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    """LangGraph 워크플로우를 실행하고 최종 상태를 반환합니다.

    Args:
        req: company_name을 담고 있는 요청 본문입니다.

    Returns:
        dict: 그래프 실행 후 상태 전체(company_name, search_results, documents, analysis)입니다.
    """
    # 컴파일된 LangGraph 객체를 가져옵니다.
    graph = get_graph()

    # 그래프 실행을 위한 초기 상태를 구성합니다.
    initial_state = {
        "company_name": req.company_name,
        "search_results": [],
        "documents": [],
        "analysis": {
            "summary": "",
            "features": [],
            "competitors": [],
        },
    }

    # 그래프를 실행하고 최종 상태를 그대로 반환합니다.
    result = graph.invoke(initial_state)
    return result
