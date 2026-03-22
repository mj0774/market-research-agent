from typing import TypedDict


class MarketResearchState(TypedDict):
    """LangGraph에서 사용할 마켓 리서치 상태 스키마입니다."""

    company_name: str
    search_results: list
    documents: list
    # 시장/업종 기반 경쟁사 탐색을 위한 검색 키워드 리스트입니다.
    market_keywords: list
    # 경쟁사 후보 문자열 리스트를 담습니다.
    competitor_candidates: list
    # analysis는 아래 구조를 기본 형태로 사용합니다.
    # {
    #   "summary": "",
    #   "features": [],
    #   "direct_competitors": [],
    #   "market_peers": []
    # }
    analysis: dict
    # report는 아래 구조를 기본 형태로 사용합니다.
    # {
    #   "strengths": [],
    #   "weaknesses": [],
    #   "strategy": []
    # }
    report: dict
