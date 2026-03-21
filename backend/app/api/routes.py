from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse

from app.schemas.analyze import AnalyzeRequest
from app.tools.scraper import scrape_article
from app.tools.search import search_company


router = APIRouter()
EXCLUDED_DOMAINS = {
    "instagram.com",
}


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        results = search_company(payload.company_name)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    documents = []
    for item in results:
        url = str(item.get("url", ""))
        if _is_excluded_domain(url):
            continue

        title = str(item.get("title", ""))
        text = scrape_article(url) if url else None
        if not text or len(text) < 80:
            continue

        documents.append(
            {
                "title": title,
                "url": url,
                "text": text,
            }
        )
        if len(documents) >= 3:
            break

    return {
        "company_name": payload.company_name,
        "documents": documents,
    }


def _is_excluded_domain(url: str) -> bool:
    try:
        hostname = urlparse(url).hostname or ""
    except Exception:
        return True
    hostname = hostname.lower()
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in EXCLUDED_DOMAINS)
