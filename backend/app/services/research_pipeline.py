from app.schemas.analysis import AnalysisResult
from app.services.llm_analyzer import analyze_company_documents
from app.tools.scraper import scrape_article
from app.tools.search import search_company


def is_allowed_url(url: str) -> bool:
    """스크래핑 허용 URL인지 확인합니다.

    Args:
        url: 검색 결과에서 가져온 후보 URL입니다.

    Returns:
        bool: 허용 URL이면 True, 차단 도메인이면 False입니다.
    """
    return "instagram.com" not in url.lower()


def run_market_research_pipeline(company_name: str) -> dict:
    """단일 업체에 대해 search -> filter -> scrape -> analyze 파이프라인을 실행합니다.

    Args:
        company_name: 조사 대상 업체명입니다.

    Returns:
        dict: company_name, search_results, documents, analysis를 포함한 결과입니다.
    """
    # 1) Tavily로 후보 문서를 검색합니다.
    search_results = search_company(company_name)
    # 2) 스크래핑 전 차단 도메인을 제외합니다.
    filtered_results = [
        item for item in search_results if is_allowed_url(str(item.get("url", "")))
    ]

    # 3) 유효 문서를 스크래핑하여 최대 3개까지 수집합니다.
    documents = []
    for item in filtered_results:
        url = str(item.get("url", ""))
        title = str(item.get("title", ""))
        # 후보 URL을 하나씩 스크래핑합니다.
        text = scrape_article(url) if url else None

        # 본문 길이가 충분한 문서만 채택합니다.
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

    # 수집된 문서가 없으면 빈 분석 결과를 반환합니다.
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

    # 4) 수집된 문서 텍스트를 기반으로 LLM 분석을 수행합니다.
    analysis = analyze_company_documents(
        company_name,
        # 구조화 분석 입력으로 문서 본문(text)만 전달합니다.
        [str(doc["text"]) for doc in documents],
    )

    return {
        "company_name": company_name,
        "search_results": search_results,
        "documents": documents,
        "analysis": analysis.model_dump(),
    }
