from app.agents.state import MarketResearchState
from app.tools.search import search_company


def competitor_discovery_node(state: MarketResearchState) -> dict:
    """업체명 기반 검색으로 경쟁사 후보를 수집하는 노드입니다."""
    # 상태에서 업체명을 가져와 경쟁사 탐색용 검색어 3개를 생성합니다.
    company_name = state["company_name"]
    company_name_lower = company_name.strip().lower()
    queries = [
        f"{company_name} 경쟁사",
        f"{company_name} 유사 식당",
        f"{company_name} 맛집",
    ]

    # 각 쿼리 검색 결과를 하나의 리스트로 합칩니다.
    merged_results = []
    for query in queries:
        merged_results.extend(search_company(query))

    # 제외할 키워드 목록입니다.
    excluded_keywords = [
        "오뎅식당",
        "유사 상품",
        "주의 안내",
        "나무위키",
        "기사",
        "뉴스",
        "블로그",
        "후기",
        "top",
        "추천",
        "정리",
    ]

    # 제목 필터링 후 중복 제거하여 최대 5개의 후보를 수집합니다.
    competitor_candidates: list[str] = []
    seen = set()

    for item in merged_results:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        if len(title) > 25:
            continue

        title_lower = title.lower()
        # 회사명이 포함되거나 회사명과 동일한 제목은 제외합니다.
        if company_name_lower and company_name_lower in title_lower:
            continue
        if title_lower == company_name_lower:
            continue

        # 불필요 키워드가 포함된 제목은 제외합니다.
        if any(keyword in title_lower for keyword in excluded_keywords):
            continue

        # 중복 후보는 제외합니다.
        if title_lower in seen:
            continue
        seen.add(title_lower)
        competitor_candidates.append(title)

        if len(competitor_candidates) >= 5:
            break

    # 상태 업데이트 형식에 맞춰 competitor_candidates를 반환합니다.
    return {
        "competitor_candidates": competitor_candidates,
    }
