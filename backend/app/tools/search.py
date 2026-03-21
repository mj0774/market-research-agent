import os
from typing import Any

from dotenv import load_dotenv
from tavily import TavilyClient


def search_company(query: str) -> list[dict[str, str]]:
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set.")

    client = TavilyClient(api_key=api_key)
    response: dict[str, Any] = client.search(query=query)
    results = response.get("results", [])

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
