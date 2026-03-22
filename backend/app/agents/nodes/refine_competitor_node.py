import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agents.state import MarketResearchState


def refine_competitor_node(state: MarketResearchState) -> dict:
    """경쟁사 후보에서 직접 경쟁사(direct_competitors)만 정제하는 노드입니다."""
    # 상태에서 업체명, 분석 특징, 경쟁사 후보를 가져옵니다.
    company_name = str(state.get("company_name", "")).strip()
    competitor_candidates = state.get("competitor_candidates", [])
    if not isinstance(competitor_candidates, list):
        competitor_candidates = []

    current_analysis = dict(state.get("analysis", {}))
    features = current_analysis.get("features", [])
    if not isinstance(features, list):
        features = []

    # 기존 market_peers는 유지해야 하므로 현재 값을 그대로 보존합니다.
    existing_market_peers = current_analysis.get("market_peers", [])
    if not isinstance(existing_market_peers, list):
        existing_market_peers = []

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        current_analysis["direct_competitors"] = []
        current_analysis["market_peers"] = existing_market_peers
        return {"analysis": current_analysis}

    prompt = (
        "너는 경쟁사 정제 분석가다.\n"
        "아래 competitor_candidates에서 direct_competitors만 추출하라.\n\n"
        "조건:\n"
        "- company_name과 같은 시장 포지션의 브랜드만 선택\n"
        "- 가격대가 다른 브랜드는 제외\n"
        "- 타겟 고객층이 다른 브랜드는 제외\n"
        "- 프리미엄 vs 저가 구분을 반영\n"
        "- 같은 카테고리라도 포지션이 다르면 제외\n"
        "- 최대 5개\n"
        "- 확실한 것만\n\n"
        "예시:\n"
        "- 메가커피 기준이면 저가 커피 프랜차이즈 중심\n"
        "- 스타벅스/투썸/폴바셋 등 포지션 차이가 크면 제외\n\n"
        f"company_name: {company_name}\n"
        f"features: {features}\n"
        f"competitor_candidates: {competitor_candidates}\n\n"
        "아래 JSON 형식으로만 출력:\n"
        '{ "direct_competitors": ["string"] }'
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
            temperature=0.0,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
    except Exception:
        current_analysis["direct_competitors"] = []
        current_analysis["market_peers"] = existing_market_peers
        return {"analysis": current_analysis}

    # JSON 파싱 결과를 정제하여 최대 5개 direct_competitors를 만듭니다.
    direct_raw = parsed.get("direct_competitors", []) if isinstance(parsed, dict) else []
    if not isinstance(direct_raw, list):
        direct_raw = []

    direct_competitors: list[str] = []
    seen = set()
    for item in direct_raw:
        value = str(item).strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        direct_competitors.append(value)
        if len(direct_competitors) >= 5:
            break

    # market_peers는 기존 값을 유지하고 direct_competitors만 갱신합니다.
    current_analysis["direct_competitors"] = direct_competitors
    current_analysis["market_peers"] = existing_market_peers

    return {
        "analysis": current_analysis,
    }
