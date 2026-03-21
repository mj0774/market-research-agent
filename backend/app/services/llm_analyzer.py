import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.analysis import AnalysisResult


def analyze_company_documents(company_name: str, documents: list[str]) -> AnalysisResult:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _fallback_result(company_name)

    merged_documents = "\n\n---\n\n".join(documents)
    if not merged_documents.strip():
        return _fallback_result(company_name)

    prompt = (
        "You are an analyst.\n"
        "Analyze the following documents about the company and extract:\n"
        "1) summary\n"
        "2) core features\n"
        "3) potential competitors\n\n"
        f"Company: {company_name}\n\n"
        "Documents:\n"
        f"{merged_documents}\n\n"
        "Return JSON only with this exact schema:\n"
        '{ "summary": "string", "features": ["string"], "competitors": ["string"] }'
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        return _to_analysis_result(parsed, company_name)
    except Exception:
        return _fallback_result(company_name)


def _to_analysis_result(parsed: Any, company_name: str) -> AnalysisResult:
    if not isinstance(parsed, dict):
        return _fallback_result(company_name)

    features_raw = parsed.get("features", [])
    competitors_raw = parsed.get("competitors", [])
    if not isinstance(features_raw, list):
        features_raw = []
    if not isinstance(competitors_raw, list):
        competitors_raw = []

    summary = str(parsed.get("summary", "")).strip()
    if not summary:
        summary = f"{company_name}에 대한 분석 결과를 생성하지 못했습니다."

    return AnalysisResult(
        summary=summary,
        features=[str(item).strip() for item in features_raw if str(item).strip()],
        competitors=[str(item).strip() for item in competitors_raw if str(item).strip()],
    )


def _fallback_result(company_name: str) -> AnalysisResult:
    return AnalysisResult(
        summary=f"{company_name}에 대한 분석 결과를 생성하지 못했습니다.",
        features=[],
        competitors=[],
    )
