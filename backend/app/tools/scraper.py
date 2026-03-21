from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


def scrape_article(url: str) -> str | None:
    try:
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
        for tag in soup(["script", "style", "noscript", "header", "footer"]):
            tag.decompose()

        content_root = soup.find("article")
        if not isinstance(content_root, Tag):
            content_root = soup.find("main")
        if not isinstance(content_root, Tag):
            content_root = soup

        text = _clean_text(content_root.get_text(separator=" ", strip=True))
        if not text:
            return None

        return text[:3000]
    except Exception:
        return None


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
