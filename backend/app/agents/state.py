from typing import TypedDict


class MarketResearchState(TypedDict):
    """LangGraph에서 사용할 마켓 리서치 상태 스키마."""

    company_name: str
    search_results: list
    documents: list
    # analysis는 아래 구조를 기본 형태로 사용할 예정입니다.
    # {
    #   "summary": "",
    #   "features": [],
    #   "competitors": []
    # }
    analysis: dict
