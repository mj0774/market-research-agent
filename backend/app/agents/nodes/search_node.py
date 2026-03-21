from app.agents.state import MarketResearchState
from app.tools.search import search_company


def search_node(state: MarketResearchState) -> dict:
    """업체명을 기반으로 검색 결과를 상태에 추가할 데이터를 생성합니다."""
    # 상태에서 업체명을 읽어 검색 함수를 호출합니다.
    company_name = state["company_name"]
    search_results = search_company(company_name)

    # LangGraph 노드 반환 형식에 맞춰 search_results만 반환합니다.
    return {
        "search_results": search_results,
    }
