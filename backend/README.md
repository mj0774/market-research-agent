# Market Research AI Agent

브랜드를 입력하면 시장 포지션 분석부터 경쟁사 도출, 전략 리포트까지 생성하는 AI 에이전트

---

## 개요

이 프로젝트는 단순 RAG가 아닌, 브랜드의 시장 포지셔닝을 기반으로 경쟁사와 전략을 분석하는 멀티스텝 AI 시스템입니다.

---

## MVP 단계

1. 웹 검색 및 문서 수집
2. 브랜드 요약 및 특징 분석
3. 시장 포지션 정의 (가격대, 타겟, 전략)
4. 포지셔닝 기반 경쟁사 도출 (market_peers / direct_competitors)
5. 강점 / 약점 / 전략 리포트 생성

---

## 핵심 기능

- 웹 검색 + 본문 스크래핑
- 브랜드 요약 및 특징 추출
- 포지셔닝 기반 경쟁사 분석
- 비즈니스 전략 리포트 생성

---

## 구조

search -> scrape -> analyze -> market_keyword -> competitor_discovery -> refine_competitor -> report

- LangGraph 기반 멀티 노드 워크플로우
- 단계별 처리로 정확도 및 안정성 확보

---

## 핵심 설계

경쟁사는 "같은 업종"이 아니라 "같은 포지션" 기준으로 정의

예)
- 메가커피 -> 저가 커피 프랜차이즈
- 스타벅스 제외
- 빽다방 / 컴포즈커피 포함

---

## 출력 예시

```json
{
  "analysis": {
    "direct_competitors": ["..."],
    "market_peers": ["빽다방", "더벤티", "컴포즈커피"]
  },
  "report": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "strategy": ["..."]
  }
}
```

---

## 기술 스택

- FastAPI
- LangGraph
- OpenAI API
- Tavily
- BeautifulSoup

---

## 한 줄 요약

브랜드 포지셔닝 기반 경쟁사 분석 및 전략 리포트 생성 AI 에이전트
