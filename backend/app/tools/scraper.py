from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


def scrape_article(url: str) -> str | None:
    """웹 페이지에서 본문 텍스트를 추출합니다.

    Args:
        url: 대상 페이지 URL입니다.

    Returns:
        str | None: 정제된 본문 텍스트(최대 3000자), 실패 시 None입니다.
    """
    try:
        # 브라우저 유사 User-Agent로 HTML을 가져와 호환성을 높입니다.
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    except Exception:
        return None

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        # 본문과 무관한 태그를 먼저 제거합니다.
        for tag in soup(["script", "style", "noscript", "header", "footer"]):
            tag.decompose()

        # article > main > 전체 문서 순으로 본문 후보를 선택합니다.
        content_root = soup.find("article")
        if not isinstance(content_root, Tag):
            content_root = soup.find("main")
        if not isinstance(content_root, Tag):
            content_root = soup

        text = _clean_text(content_root.get_text(separator=" ", strip=True))
        if not text:
            return None

        # 하위 LLM 토큰/비용 제어를 위해 최대 길이를 제한합니다.
        return text[:3000]
    except Exception:
        return None


def _clean_text(text: str) -> str:
    """추출 텍스트의 공백을 정규화합니다."""
    return re.sub(r"\s+", " ", text).strip()
