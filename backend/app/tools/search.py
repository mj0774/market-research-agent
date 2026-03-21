import os
from typing import Any

from dotenv import load_dotenv
from tavily import TavilyClient


def search_company(query: str) -> list[dict[str, str]]:
    """Tavily를 사용해 업체 관련 웹 검색 결과를 가져옵니다.

    Args:
        query: 업체명 또는 검색어입니다.

    Returns:
        list[dict[str, str]]: title/url/content 형태로 정규화된 검색 결과입니다.
    """
    # 로컬 개발 환경에서 .env의 API 키를 로드합니다.
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set.")

    # 검색 에이전트 역할: 업체 관련 후보 문서를 수집합니다.
    client = TavilyClient(api_key=api_key)
    response: dict[str, Any] = client.search(query=query)
    results = response.get("results", [])

    # 하위 파이프라인에서 재사용하기 쉽도록 응답 형식을 정규화합니다.
    normalized: list[dict[str, str]] = []
    for item in results:
        normalized.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "content": str(item.get("content") or item.get("raw_content", "")),
            }
        )
    return normalized
