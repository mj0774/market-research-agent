import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.analysis import AnalysisResult


def analyze_company_documents(company_name: str, documents: list[str]) -> AnalysisResult:
    """스크래핑된 문서를 기반으로 구조화된 업체 분석 결과를 생성합니다.

    Args:
        company_name: 분석 대상 업체명입니다.
        documents: 분석 입력으로 사용할 문서 본문 목록입니다.

    Returns:
        AnalysisResult: summary/features/competitors 구조의 분석 결과입니다.
    """
    # OPENAI_API_KEY / OPENAI_MODEL 환경변수를 읽기 위해 .env를 로드합니다.
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _fallback_result(company_name)

    # 문서들을 하나의 프롬프트 컨텍스트로 합쳐 LLM을 1회 호출합니다.
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
        # LLM 분석 에이전트 호출: 한 번의 응답에서 구조화된 인사이트를 생성합니다.
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
        # 모델 응답을 JSON으로만 파싱합니다.
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        return _to_analysis_result(parsed, company_name)
    except Exception:
        return _fallback_result(company_name)


def _to_analysis_result(parsed: Any, company_name: str) -> AnalysisResult:
    """파싱된 JSON을 AnalysisResult 스키마로 정규화합니다.

    Args:
        parsed: LLM 응답에서 파싱한 JSON 객체입니다.
        company_name: fallback 요약문에 사용할 업체명입니다.

    Returns:
        AnalysisResult: 정제된 스키마 안전 분석 결과입니다.
    """
    # parsed는 반드시 dict 형태여야 합니다.
    if not isinstance(parsed, dict):
        return _fallback_result(company_name)

    features_raw = parsed.get("features", [])
    competitors_raw = parsed.get("competitors", [])
    if not isinstance(features_raw, list):
        features_raw = []
    if not isinstance(competitors_raw, list):
        competitors_raw = []

    # UI 표시 안정성을 위해 summary는 항상 값이 있도록 보장합니다.
    summary = str(parsed.get("summary", "")).strip()
    if not summary:
        summary = f"{company_name}에 대한 분석 결과를 생성하지 못했습니다."

    # features는 중복 제거 후 최대 5개까지만 유지합니다.
    features: list[str] = []
    for item in features_raw:
        value = str(item).strip()
        if not value or value in features:
            continue
        features.append(value)
        if len(features) >= 5:
            break

    # competitors는 중복 없는 업체명만 유지합니다.
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
    """분석 실패 시 안전한 기본 결과를 반환합니다.

    Args:
        company_name: fallback 요약문에 사용할 업체명입니다.

    Returns:
        AnalysisResult: 빈 features/competitors를 가진 기본 결과입니다.
    """
    return AnalysisResult(
        summary=f"{company_name}에 대한 분석 결과를 생성하지 못했습니다.",
        features=[],
        competitors=[],
    )
