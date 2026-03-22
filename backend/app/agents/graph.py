from langgraph.graph import END, StateGraph

from app.agents.nodes.analyze_node import analyze_node
from app.agents.nodes.competitor_discovery_node import competitor_discovery_node
from app.agents.nodes.market_keyword_node import market_keyword_node
from app.agents.nodes.refine_competitor_node import refine_competitor_node
from app.agents.nodes.report_node import report_node
from app.agents.nodes.scrape_node import scrape_node
from app.agents.nodes.search_node import search_node
from app.agents.state import MarketResearchState


# MarketResearchState를 기반으로 LangGraph 빌더를 생성합니다.
builder = StateGraph(MarketResearchState)

# 각 처리 단계를 노드로 등록합니다.
builder.add_node("search", search_node)
builder.add_node("scrape", scrape_node)
builder.add_node("analyze", analyze_node)
builder.add_node("market_keyword", market_keyword_node)
builder.add_node("competitor_discovery", competitor_discovery_node)
builder.add_node("refine_competitor", refine_competitor_node)
builder.add_node("report", report_node)

# 실행 흐름을 search -> scrape -> analyze -> market_keyword -> competitor_discovery -> refine_competitor -> report -> END로 연결합니다.
builder.add_edge("search", "scrape")
builder.add_edge("scrape", "analyze")
builder.add_edge("analyze", "market_keyword")
builder.add_edge("market_keyword", "competitor_discovery")
builder.add_edge("competitor_discovery", "refine_competitor")
builder.add_edge("refine_competitor", "report")
builder.add_edge("report", END)

# 그래프 시작 노드를 search로 설정합니다.
builder.set_entry_point("search")

# 그래프를 컴파일하여 실행 가능한 객체를 생성합니다.
graph = builder.compile()


def get_graph():
    """컴파일된 LangGraph 객체를 반환합니다."""
    return graph
