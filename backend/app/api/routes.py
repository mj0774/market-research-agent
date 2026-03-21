from fastapi import APIRouter, HTTPException

from app.schemas.analyze import AnalyzeRequest
from app.tools.scraper import scrape_article
from app.tools.search import search_company


router = APIRouter()


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        results = search_company(payload.company_name)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    documents = []
    for item in results[:3]:
        url = str(item.get("url", ""))
        title = str(item.get("title", ""))
        text = scrape_article(url) if url else None

        documents.append(
            {
                "title": title,
                "url": url,
                "text": text,
            }
        )

    return {
        "company_name": payload.company_name,
        "documents": documents,
    }
