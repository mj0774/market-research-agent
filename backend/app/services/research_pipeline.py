from app.schemas.analysis import AnalysisResult
from app.services.llm_analyzer import analyze_company_documents
from app.tools.scraper import scrape_article
from app.tools.search import search_company


def is_allowed_url(url: str) -> bool:
    return "instagram.com" not in url.lower()


def run_market_research_pipeline(company_name: str) -> dict:
    search_results = search_company(company_name)
    filtered_results = [
        item for item in search_results if is_allowed_url(str(item.get("url", "")))
    ]

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

    if not documents:
        return {
            "company_name": company_name,
            "search_results": search_results,
            "documents": [],
            "analysis": AnalysisResult(
                summary="",
                features=[],
                competitors=[],
            ).model_dump(),
        }

    analysis = analyze_company_documents(
        company_name,
        [str(doc["text"]) for doc in documents],
    )

    return {
        "company_name": company_name,
        "search_results": search_results,
        "documents": documents,
        "analysis": analysis.model_dump(),
    }
