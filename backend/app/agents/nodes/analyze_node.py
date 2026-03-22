from app.agents.state import MarketResearchState
from app.services.llm_analyzer import analyze_company_documents


def analyze_node(state: MarketResearchState) -> dict:
    """수집된 문서를 기반으로 구조화 분석 결과를 생성하는 노드입니다."""
    # 상태에서 업체명과 문서 목록을 가져옵니다.
    company_name = state["company_name"]
    documents = state["documents"]

    # 문서가 없으면 기본 분석 결과를 반환합니다.
    if not documents:
        return {
            "analysis": {
                "summary": "",
                "features": [],
                "direct_competitors": [],
                "market_peers": [],
            }
        }

    # 각 문서에서 본문(text)만 추출하여 LLM 분석 함수에 전달합니다.
    analysis = analyze_company_documents(
        company_name,
        [str(doc.get("text", "")) for doc in documents if str(doc.get("text", "")).strip()],
    )

    # AnalysisResult 타입을 dict로 변환해 상태 업데이트 형식에 맞춰 반환합니다.
    return {
        "analysis": analysis.model_dump(),
    }
