from app.agents.state import MarketResearchState
from app.tools.search import search_company


def competitor_discovery_node(state: MarketResearchState) -> dict:
    """시장 키워드 기반 검색 결과에서 경쟁사 후보를 추출하는 노드입니다."""
    # 상태에서 업체명과 시장 키워드를 가져옵니다.
    company_name = str(state["company_name"]).strip()
    company_name_lower = company_name.lower()
    market_keywords = state.get("market_keywords", [])
    if not isinstance(market_keywords, list):
        market_keywords = []

    # 각 키워드마다 검색 쿼리를 확장합니다.
    queries: list[str] = []
    for keyword in market_keywords:
        keyword_text = str(keyword).strip()
        if not keyword_text:
            continue
        queries.append(f"{keyword_text} 맛집")
        queries.append(f"{keyword_text} 추천")
        queries.append(f"{keyword_text} TOP")

    # 여러 번 검색한 결과를 하나의 리스트로 합칩니다.
    merged_results = []
    for query in queries:
        merged_results.extend(search_company(query))

    competitor_candidates: list[str] = []
    seen = set()

    for item in merged_results:
        title = str(item.get("title", "")).strip()
        if not title:
            continue

        title_lower = title.lower()
        # 핵심 필터: title에 맛집/추천/TOP이 있는 결과만 사용합니다.
        if not ("맛집" in title or "추천" in title or "top" in title_lower):
            continue

        # 후보 추출: 쉼표 기준으로 자르고, 키워드 표현을 제거한 앞부분만 사용합니다.
        candidate = title.split(",")[0].strip()
        candidate = candidate.split("|")[0].strip()
        candidate = candidate.split("-")[0].strip()
        candidate = candidate.replace("맛집", "")
        candidate = candidate.replace("추천", "")
        candidate = candidate.replace("TOP", "")
        candidate = candidate.replace("top", "")
        candidate = candidate.strip(" -:|[]()")
        candidate = " ".join(candidate.split())
        if not candidate:
            continue

        candidate_lower = candidate.lower()
        # 자기 자신(업체명)은 후보에서 제외합니다.
        if candidate_lower == company_name_lower:
            continue
        if company_name_lower and company_name_lower in candidate_lower:
            continue

        # 중복 제거를 유지합니다.
        if candidate_lower in seen:
            continue
        seen.add(candidate_lower)
        competitor_candidates.append(candidate)

        # 최대 5개까지만 유지합니다.
        if len(competitor_candidates) >= 5:
            break

    return {
        "competitor_candidates": competitor_candidates,
    }
