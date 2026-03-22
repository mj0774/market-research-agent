from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """LLM 분석 단계에서 반환되는 구조화 결과 스키마입니다.

    Attributes:
        summary: 업체 요약입니다.
        features: 핵심 특징 목록입니다.
        direct_competitors: 문서에서 실명으로 확인된 직접 경쟁사 목록입니다.
        market_peers: 동일 업종/시장군의 비교 대상 브랜드 목록입니다.
    """

    summary: str
    features: list[str]
    direct_competitors: list[str]
    market_peers: list[str]
