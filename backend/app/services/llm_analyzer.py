import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.analysis import AnalysisResult


def analyze_company_documents(company_name: str, documents: list[str]) -> AnalysisResult:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _empty_result()

    merged_documents = "\n\n---\n\n".join(documents)
    if not merged_documents.strip():
        return _empty_result()

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
        return AnalysisResult(
            summary=str(parsed.get("summary", "")),
            features=[str(item) for item in parsed.get("features", [])],
            competitors=[str(item) for item in parsed.get("competitors", [])],
        )
    except Exception:
        return _empty_result()


def _empty_result() -> AnalysisResult:
    return AnalysisResult(summary="", features=[], competitors=[])
