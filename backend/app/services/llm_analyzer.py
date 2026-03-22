import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.analysis import AnalysisResult


def analyze_company_documents(company_name: str, documents: list[str]) -> AnalysisResult:
    """스크래핑된 문서를 기반으로 구조화된 업체 분석 결과를 생성합니다."""
    # OPENAI_API_KEY / OPENAI_MODEL 환경변수를 읽기 위해 .env를 로드합니다.
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _fallback_result()

    # 문서들을 하나의 프롬프트 컨텍스트로 합쳐 LLM을 1회 호출합니다.
    merged_documents = "\n\n---\n\n".join(documents)
    if not merged_documents.strip():
        return _fallback_result()

    prompt = (
        "너는 시장 조사 분석가다.\n"
        "아래 문서를 기반으로 업체 분석 결과를 JSON으로만 출력하라.\n\n"
        "[1단계] 시장 포지션 정의:\n"
        "- summary + features를 근거로 해당 브랜드의 시장 포지션을 한 줄로 먼저 내부적으로 정의하라.\n"
        "- 예: '저가 대용량 커피 프랜차이즈', '가성비 중심 커피 체인'\n\n"
        "[2단계] market_peers 생성:\n"
        "- 1단계에서 정의한 포지션과 동일한 브랜드만 market_peers로 선택하라.\n"
        "- 반드시 동일 포지션 기준으로만 선택하라.\n"
        "- 가격대가 다른 브랜드 제외\n"
        "- 고객층이 다른 브랜드 제외\n"
        "- 프리미엄 브랜드 제외\n"
        "- 중가 브랜드도 제외 가능\n"
        "- market_peers 최대 5개\n\n"
        "필드별 조건:\n"
        "- summary: 업체 요약\n"
        "- features: 핵심 특징 5개 이하\n"
        "- direct_competitors: 문서에 실제로 확인되는 실명 경쟁사만 추출, 근거 없으면 []\n"
        "- market_peers: 2단계 규칙을 통과한 동일 포지셔닝 브랜드만\n"
        "- 추측은 최소화\n"
        "- JSON 외 텍스트 출력 금지\n\n"
        "예시 규칙:\n"
        "- 메가커피 기준 market_peers 예시: 컴포즈커피, 빽다방, 더벤티, 매머드커피\n"
        "- 스타벅스, 폴 바셋, 커피빈, 투썸플레이스는 제외\n\n"
        f"기준 업체명: {company_name}\n"
        f"문서:\n{merged_documents}\n\n"
        "출력 JSON 형식:\n"
        "{\n"
        '  "summary": "string",\n'
        '  "features": ["string"],\n'
        '  "direct_competitors": ["string"],\n'
        '  "market_peers": ["string"]\n'
        "}"
    )

    try:
        # LLM 분석 호출: 한 번의 응답에서 구조화된 인사이트를 생성합니다.
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "JSON 이외의 텍스트 출력 금지"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        # 모델 응답을 JSON으로만 파싱합니다.
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        return _to_analysis_result(parsed)
    except Exception:
        return _fallback_result()


def _to_analysis_result(parsed: Any) -> AnalysisResult:
    """파싱된 JSON을 AnalysisResult 스키마로 정규화합니다."""
    if not isinstance(parsed, dict):
        return _fallback_result()

    features_raw = parsed.get("features", [])
    direct_raw = parsed.get("direct_competitors", [])
    peers_raw = parsed.get("market_peers", [])

    if not isinstance(features_raw, list):
        features_raw = []
    if not isinstance(direct_raw, list):
        direct_raw = []
    if not isinstance(peers_raw, list):
        peers_raw = []

    summary = str(parsed.get("summary", "")).strip()

    # features는 중복 제거 후 최대 5개로 제한합니다.
    features: list[str] = []
    seen_features = set()
    for item in features_raw:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen_features:
            continue
        seen_features.add(key)
        features.append(value)
        if len(features) >= 5:
            break

    # direct_competitors는 중복 제거하여 유지합니다.
    direct_competitors: list[str] = []
    seen_direct = set()
    for item in direct_raw:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen_direct:
            continue
        seen_direct.add(key)
        direct_competitors.append(value)

    # market_peers는 중복 제거 후 최대 5개로 제한합니다.
    market_peers: list[str] = []
    seen_peers = set()
    for item in peers_raw:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen_peers:
            continue
        seen_peers.add(key)
        market_peers.append(value)
        if len(market_peers) >= 5:
            break

    return AnalysisResult(
        summary=summary,
        features=features,
        direct_competitors=direct_competitors,
        market_peers=market_peers,
    )


def _fallback_result() -> AnalysisResult:
    """분석 실패 시 안전한 기본 결과를 반환합니다."""
    return AnalysisResult(
        summary="",
        features=[],
        direct_competitors=[],
        market_peers=[],
    )
