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
        "Analyze the following documents and extract company insights.\n"
        "추측하지 말 것.\n"
        "문서 내용 기반으로만 작성.\n"
        "JSON 이외의 텍스트 출력 금지.\n\n"
        "Rules:\n"
        "- summary: concise company summary based only on documents.\n"
        "- features: only the most important features, max 5 items.\n"
        "- features: remove trivial or duplicate items.\n"
        "- competitors: extract only company names explicitly mentioned in documents.\n"
        "- competitors: if no clear competitor company name exists, return [].\n"
        '- competitors: never output generic categories (e.g., "부대찌개 식당", "한식당").\n\n'
        f"Company: {company_name}\n\n"
        "Documents:\n"
        f"{merged_documents}\n\n"
        "Output must be exactly this JSON schema:\n"
        '{\n'
        '  "summary": "string",\n'
        '  "features": ["string"],\n'
        '  "competitors": ["string"]\n'
        '}'
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

    features: list[str] = []
    for item in features_raw:
        value = str(item).strip()
        if not value or value in features:
            continue
        features.append(value)
        if len(features) >= 5:
            break

    competitors: list[str] = []
    for item in competitors_raw:
        value = str(item).strip()
        if not value or value in competitors:
            continue
        competitors.append(value)

    return AnalysisResult(
        summary=summary,
        features=features,
        competitors=competitors,
    )


def _fallback_result(company_name: str) -> AnalysisResult:
    return AnalysisResult(
        summary=f"{company_name}에 대한 분석 결과를 생성하지 못했습니다.",
        features=[],
        competitors=[],
    )
