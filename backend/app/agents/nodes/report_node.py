import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agents.state import MarketResearchState


def report_node(state: MarketResearchState) -> dict:
    """분석 결과를 기반으로 비즈니스 리포트를 생성하는 노드입니다."""
    # 상태에서 리포트 생성에 필요한 분석 데이터를 가져옵니다.
    analysis = state.get("analysis", {})
    if not isinstance(analysis, dict):
        analysis = {}

    summary = str(analysis.get("summary", "")).strip()
    features = analysis.get("features", [])
    direct_competitors = analysis.get("direct_competitors", [])
    market_peers = analysis.get("market_peers", [])

    if not isinstance(features, list):
        features = []
    if not isinstance(direct_competitors, list):
        direct_competitors = []
    if not isinstance(market_peers, list):
        market_peers = []

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {"report": _empty_report()}

    prompt = (
        "너는 브랜드 비즈니스 분석 리포트를 작성하는 전략 컨설턴트다.\n"
        "아래 정보를 바탕으로 JSON 형식 리포트를 생성하라.\n\n"
        "목표:\n"
        "- 해당 브랜드의 비즈니스 분석 리포트 생성\n\n"
        "출력 구성:\n"
        "1) strengths (강점): 핵심 경쟁력 3~5개\n"
        "2) weaknesses (약점): 개선 필요 요소/경쟁사 대비 약점 3~5개\n"
        "3) strategy (전략 제안): 마케팅/브랜딩/성장 전략 3~5개\n\n"
        "조건:\n"
        "- features 기반 분석\n"
        "- competitors 비교 포함\n"
        "- 추상적인 말 금지\n"
        "- 구체적으로 작성\n"
        "- JSON 외 텍스트 출력 금지\n\n"
        f"summary: {summary}\n"
        f"features: {features}\n"
        f"direct_competitors: {direct_competitors}\n"
        f"market_peers: {market_peers}\n\n"
        "출력 JSON 형식:\n"
        '{ "strengths": ["string"], "weaknesses": ["string"], "strategy": ["string"] }'
    )

    try:
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
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
    except Exception:
        return {"report": _empty_report()}

    # JSON 파싱 결과를 정제하여 report 구조로 반환합니다.
    report = _normalize_report(parsed)
    return {
        "report": report,
    }


def _normalize_report(parsed: object) -> dict:
    """모델 응답 JSON을 report 스키마(strengths/weaknesses/strategy)로 정규화합니다."""
    if not isinstance(parsed, dict):
        return _empty_report()

    strengths_raw = parsed.get("strengths", [])
    weaknesses_raw = parsed.get("weaknesses", [])
    strategy_raw = parsed.get("strategy", [])

    if not isinstance(strengths_raw, list):
        strengths_raw = []
    if not isinstance(weaknesses_raw, list):
        weaknesses_raw = []
    if not isinstance(strategy_raw, list):
        strategy_raw = []

    return {
        "strengths": _uniq_limit(strengths_raw, 5),
        "weaknesses": _uniq_limit(weaknesses_raw, 5),
        "strategy": _uniq_limit(strategy_raw, 5),
    }


def _uniq_limit(items: list, limit: int) -> list[str]:
    """문자열 리스트를 중복 제거하고 최대 개수를 제한합니다."""
    values: list[str] = []
    seen = set()
    for item in items:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        values.append(value)
        if len(values) >= limit:
            break
    return values


def _empty_report() -> dict:
    """리포트 생성 실패 시 반환할 기본 구조입니다."""
    return {
        "strengths": [],
        "weaknesses": [],
        "strategy": [],
    }
