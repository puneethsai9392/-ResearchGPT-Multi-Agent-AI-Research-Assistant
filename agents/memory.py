from typing import List, Dict, Any, Optional, TypedDict
from langgraph.checkpoint.memory import MemorySaver

class ResearchState(TypedDict, total=False):
    session_id: str
    query: str
    tasks: List[str]
    web_results: List[Dict[str, Any]]
    rag_results: List[Dict[str, Any]]
    aggregated_evidence: Dict[str, Any]
    critic_review: Dict[str, Any]
    final_report: str
    revision_count: int
    logs: List[str]

# Global in-memory LangGraph checkpointer
memory_saver = MemorySaver()
