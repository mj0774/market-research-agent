import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agents.state import MarketResearchState


def extract_competitor_from_docs_node(state: MarketResearchState) -> dict:
    """문서 본문에서 경쟁사 후보 브랜드명을 추출하는 노드입니다."""
    # 상태에서 업체명과 문서 목록을 가져옵니다.
    company_name = str(state.get("company_name", "")).strip()
    company_name_lower = company_name.lower()
    documents = state.get("documents", [])
    if not isinstance(documents, list):
        documents = []

    # 문서 본문(text)만 추출하여 하나의 텍스트로 합칩니다.
    texts: list[str] = []
    for doc in documents:
        if not isinstance(doc, dict):
            continue
        text = str(doc.get("text", "")).strip()
        if text:
            texts.append(text)

    if not texts:
        return {"competitor_candidates": []}

    merged_text = "\n\n---\n\n".join(texts)

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {"competitor_candidates": []}

    prompt = (
        "너는 시장 조사 분석가다.\n"
        "아래 문서에서 동일 업종의 브랜드 이름만 추출하라.\n\n"
        "조건:\n"
        "- 실제 브랜드명만 추출\n"
        "- 설명 문장 제거\n"
        f"- 기준 업체명('{company_name}')은 제외\n"
        "- 최대 10개\n"
        "- 확실한 것만\n"
        "- 없으면 빈 배열\n\n"
        "출력 JSON 형식:\n"
        '{ "competitor_candidates": ["string"] }\n\n'
        f"문서:\n{merged_text}"
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
        return {"competitor_candidates": []}

    # 파싱 결과를 정제하여 중복 제거, 자기 자신 제외, 최대 10개 제한을 적용합니다.
    candidates_raw = (
        parsed.get("competitor_candidates", []) if isinstance(parsed, dict) else []
    )
    if not isinstance(candidates_raw, list):
        candidates_raw = []

    competitor_candidates: list[str] = []
    seen = set()
    for item in candidates_raw:
        value = str(item).strip()
        if not value:
            continue
        value_lower = value.lower()
        if company_name_lower and value_lower == company_name_lower:
            continue
        if company_name_lower and company_name_lower in value_lower:
            continue
        if value_lower in seen:
            continue
        seen.add(value_lower)
        competitor_candidates.append(value)
        if len(competitor_candidates) >= 10:
            break

    return {
        "competitor_candidates": competitor_candidates,
    }
