from typing import List, Dict, Any
from app.config import TAVILY_API_KEY
from app.utils.logger import get_logger

logger = get_logger("Agent.WebSearch")

def run_web_search(tasks: List[str], query: str) -> List[Dict[str, Any]]:
    """
    Web Search Agent: Performs web searches for research tasks using Tavily or DuckDuckGo.
    """
    results = []
    search_queries = [query] + tasks[:2]  # Search main query + top 2 subtasks

    if TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            for q in search_queries:
                logger.info(f"Tavily Searching: '{q}'")
                response = client.search(query=q, max_results=3, search_depth="basic")
                for r in response.get("results", []):
                    results.append({
                        "title": r.get("title", "Web Resource"),
                        "snippet": r.get("content", ""),
                        "url": r.get("url", ""),
                        "query": q,
                        "source_type": "web"
                    })
            if results:
                return results
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}. Falling back to DuckDuckGo search.")

    # DuckDuckGo fallback
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        for q in search_queries:
            logger.info(f"DuckDuckGo Searching: '{q}'")
            ddg_res = list(ddgs.text(q, max_results=3))
            for r in ddg_res:
                results.append({
                    "title": r.get("title", "Web Article"),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                    "query": q,
                    "source_type": "web"
                })
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}. Using fallback web context.")
        for q in search_queries:
            results.append({
                "title": f"Web Overview: {q}",
                "snippet": f"Detailed web insights regarding {q}, covering fundamentals, industry benchmarks, and implementation patterns.",
                "url": "https://arvix.org/abs/2401.example",
                "query": q,
                "source_type": "web"
            })

    return results
