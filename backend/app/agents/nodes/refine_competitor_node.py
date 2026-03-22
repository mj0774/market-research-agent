import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agents.state import MarketResearchState


def refine_competitor_node(state: MarketResearchState) -> dict:
    """경쟁사 후보를 실제 음식점 이름으로 정제하는 노드입니다."""
    # 상태에서 업체명과 경쟁사 후보를 가져옵니다.
    company_name = state["company_name"]
    competitor_candidates = state.get("competitor_candidates", [])

    # 기존 analysis 값을 유지하면서 competitors만 교체하기 위해 복사합니다.
    current_analysis = dict(state.get("analysis", {}))

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {"analysis": current_analysis}

    prompt = (
        "너는 음식점 경쟁사 정제 도우미다.\n"
        "아래 competitor_candidates를 보고 실제 음식점 이름만 추출하라.\n\n"
        "조건:\n"
        "- 뉴스 제목, 일반 문장, 설명 문구는 제거\n"
        "- 'TOP10', '추천', '기사' 같은 표현은 제거\n"
        "- 같은 업체명은 중복 제거\n"
        "- 최대 5개만 반환\n"
        "- 추측 금지\n\n"
        f"기준 업체명: {company_name}\n"
        f"competitor_candidates: {competitor_candidates}\n\n"
        "아래 JSON 형식으로만 출력:\n"
        '{ "competitors": ["string"] }'
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
        return {"analysis": current_analysis}

    # JSON 파싱 결과에서 competitors를 읽고 형식을 정리합니다.
    competitors_raw = parsed.get("competitors", []) if isinstance(parsed, dict) else []
    if not isinstance(competitors_raw, list):
        competitors_raw = []

    competitors: list[str] = []
    seen = set()
    for item in competitors_raw:
        value = str(item).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        competitors.append(value)
        if len(competitors) >= 5:
            break

    # 기존 analysis는 유지하고 competitors만 정제 결과로 교체합니다.
    current_analysis["competitors"] = competitors
    return {
        "analysis": current_analysis,
    }
