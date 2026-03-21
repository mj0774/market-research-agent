from pydantic import BaseModel


class AnalysisResult(BaseModel):
    summary: str
    features: list[str]
    competitors: list[str]
