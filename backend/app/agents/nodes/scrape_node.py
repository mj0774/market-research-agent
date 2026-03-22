from app.agents.state import MarketResearchState
from app.tools.scraper import scrape_article


def is_allowed_url(url: str) -> bool:
    """스크래핑 허용 URL인지 확인합니다."""
    return "instagram.com" not in url.lower()


def scrape_node(state: MarketResearchState) -> dict:
    """검색 결과를 순회하며 문서 본문을 수집하는 노드입니다."""
    # 상태에서 검색 결과를 가져옵니다.
    search_results = state["search_results"]

    # 인스타그램 도메인을 제외한 결과만 남깁니다.
    filtered_results = [
        item for item in search_results if is_allowed_url(str(item.get("url", "")))
    ]

    # 본문 길이가 80자 이상인 문서만 최대 3개까지 수집합니다.
    documents = []
    for item in filtered_results:
        url = str(item.get("url", ""))
        title = str(item.get("title", ""))
        text = scrape_article(url) if url else None

        if text and len(text) >= 80:
            documents.append(
                {
                    "title": title,
                    "url": url,
                    "text": text,
                }
            )

        if len(documents) >= 3:
            break

    # LangGraph 노드 반환 형식에 맞춰 documents만 반환합니다.
    return {
        "documents": documents,
    }
