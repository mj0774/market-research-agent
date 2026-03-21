from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """LLM 분석 단계에서 반환되는 구조화 결과 스키마입니다.

    Attributes:
        summary: 업체 요약입니다.
        features: 핵심 특징 목록입니다.
        competitors: 문서에서 언급된 경쟁사 업체명 목록입니다.
    """
    summary: str
    features: list[str]
    competitors: list[str]
