from app.agents.state import MarketResearchState
from app.tools.search import search_company


def competitor_discovery_node(state: MarketResearchState) -> dict:
    """업체명 기반 검색으로 경쟁사 후보를 수집하는 노드입니다."""
    # 상태에서 업체명을 가져와 경쟁사 탐색용 검색어 3개를 생성합니다.
    company_name = state["company_name"]
    queries = [
        f"{company_name} 경쟁사",
        f"{company_name} 유사 식당",
        f"{company_name} 맛집",
    ]

    # 각 쿼리별 검색 결과를 하나의 리스트로 합칩니다.
    merged_results = []
    for query in queries:
        merged_results.extend(search_company(query))

    # 제외 키워드/길이 조건으로 title을 필터링하며 경쟁사 후보를 만듭니다.
    excluded_keywords = ["블로그", "후기", "TOP", "추천", "정리"]
    competitor_candidates: list[str] = []
    seen = set()

    for item in merged_results:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        if len(title) >= 30:
            continue
        if any(keyword in title for keyword in excluded_keywords):
            continue
        if not title or title in seen:
            continue
        seen.add(title)
        competitor_candidates.append(title)
        if len(competitor_candidates) >= 5:
            break

    # LangGraph 상태 업데이트 형식에 맞춰 반환합니다.
    return {
        "competitor_candidates": competitor_candidates,
    }
