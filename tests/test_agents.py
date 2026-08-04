import pytest
from app.agents.planner import run_planner
from app.agents.aggregator import run_evidence_aggregator
from app.agents.critic import run_critic
from app.agents.writer import run_writer
from app.graph.workflow import research_graph

def test_planner_agent():
    query = "Explain Vector Databases and ChromaDB"
    tasks = run_planner(query)
    assert isinstance(tasks, list)
    assert len(tasks) >= 3

def test_evidence_aggregator():
    web_res = [{"title": "Web Title", "snippet": "Vector search uses HNSW indexes.", "url": "https://example.com"}]
    rag_res = [{"snippet": "ChromaDB persists embeddings on disk.", "source": "doc.pdf"}]
    notes = [{"task": "Task 1", "domain_context": "Analysis context"}]
    tasks = ["Define Vector Databases", "Explain HNSW indexing"]

    agg = run_evidence_aggregator(web_res, rag_res, notes, tasks)
    assert agg["total_evidence_items"] >= 2
    assert "sectioned_evidence" in agg

def test_critic_agent():
    query = "Vector Databases"
    aggregated = {
        "total_evidence_items": 2,
        "raw_evidence": [{"source": "doc.pdf", "content": "Sample content for vector search."}]
    }
    critic_res = run_critic(query, aggregated, revision_count=1)
    assert "is_valid" in critic_res
    assert "quality_score" in critic_res

def test_full_graph_execution():
    config = {"configurable": {"thread_id": "test-thread-1"}}
    state = {
        "query": "What is LangGraph?",
        "tasks": [],
        "web_results": [],
        "rag_results": [],
        "aggregated_evidence": {},
        "critic_review": {},
        "final_report": "",
        "revision_count": 0,
        "logs": []
    }

    result = research_graph.invoke(state, config=config)
    assert "final_report" in result
    assert len(result["final_report"]) > 100
    assert "session_id" in result
