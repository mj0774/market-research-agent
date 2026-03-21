from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """/analyze 엔드포인트 요청 스키마입니다.

    Attributes:
        company_name: 리서치 파이프라인을 실행할 대상 업체명입니다.
    """
    company_name: str
