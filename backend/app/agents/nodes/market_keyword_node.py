import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agents.state import MarketResearchState


def market_keyword_node(state: MarketResearchState) -> dict:
    """분석 결과를 기반으로 경쟁사 탐색용 시장 키워드를 생성하는 노드입니다."""
    # 상태에서 summary/features를 가져와 키워드 생성 입력으로 사용합니다.
    analysis = state.get("analysis", {})
    summary = str(analysis.get("summary", "")).strip() if isinstance(analysis, dict) else ""
    features = analysis.get("features", []) if isinstance(analysis, dict) else []
    if not isinstance(features, list):
        features = []

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {"market_keywords": []}

    prompt = (
        "너는 시장 조사 키워드 생성 도우미다.\n"
        "아래 업체 분석 정보를 기반으로, 같은 시장/카테고리의 경쟁사를 찾기 위한 검색 키워드를 생성하라.\n\n"
        "조건:\n"
        "- '회사명 경쟁사' 같은 단순 키워드 금지\n"
        "- 업종 + 지역 + 특징 기반으로 키워드 생성\n"
        "- 3~5개 생성\n"
        "- 추측 금지\n\n"
        "예시:\n"
        "- 의정부 부대찌개 맛집\n"
        "- 부대찌개 전문점\n"
        "- 부대찌개 프랜차이즈\n\n"
        f"summary: {summary}\n"
        f"features: {features}\n\n"
        "아래 JSON 형식으로만 출력:\n"
        '{ "market_keywords": ["string"] }'
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
        return {"market_keywords": []}

    # 파싱된 키워드를 정제하여 중복 제거 및 최대 5개 제한을 적용합니다.
    keywords_raw = parsed.get("market_keywords", []) if isinstance(parsed, dict) else []
    if not isinstance(keywords_raw, list):
        keywords_raw = []

    market_keywords: list[str] = []
    seen = set()
    for item in keywords_raw:
        keyword = str(item).strip()
        if not keyword:
            continue
        key = keyword.lower()
        if key in seen:
            continue
        seen.add(key)
        market_keywords.append(keyword)
        if len(market_keywords) >= 5:
            break

    return {
        "market_keywords": market_keywords,
    }
