from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    company_name: str
