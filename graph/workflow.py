import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from app.agents.memory import ResearchState, memory_saver
from app.agents.planner import run_planner
from app.agents.web_search import run_web_search
from app.agents.rag import run_rag_agent
from app.agents.researcher import run_researcher
from app.agents.aggregator import run_evidence_aggregator
from app.agents.critic import run_critic
from app.agents.writer import run_writer
from app.database.sqlite import save_research_session
from app.utils.logger import get_logger

logger = get_logger("Graph.Workflow")

# Node Implementations
def planner_node(state: ResearchState) -> Dict[str, Any]:
    query = state.get("query", "")
    logger.info(f"--- Graph Node: Planner for '{query}' ---")
    tasks = run_planner(query)
    logs = state.get("logs", [])
    logs.append(f"Planner decomposed query into {len(tasks)} subtasks.")
    return {"tasks": tasks, "logs": logs, "revision_count": 0}

def retrieval_node(state: ResearchState) -> Dict[str, Any]:
    query = state.get("query", "")
    tasks = state.get("tasks", [])
    logger.info(f"--- Graph Node: Parallel Retrieval (Web + RAG + Researcher) ---")
    
    web_results = run_web_search(tasks, query)
    rag_results = run_rag_agent(tasks, query)
    research_notes = run_researcher(query, tasks)

    logs = state.get("logs", [])
    logs.append(f"Retrieval complete: {len(web_results)} web items, {len(rag_results)} vector DB items.")
    return {
        "web_results": web_results,
        "rag_results": rag_results,
        "research_notes": research_notes,
        "logs": logs
    }

def aggregator_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("--- Graph Node: Evidence Aggregator ---")
    web_results = state.get("web_results", [])
    rag_results = state.get("rag_results", [])
    research_notes = state.get("research_notes", [])
    tasks = state.get("tasks", [])

    aggregated = run_evidence_aggregator(web_results, rag_results, research_notes, tasks)
    logs = state.get("logs", [])
    logs.append(f"Evidence Aggregator deduplicated {aggregated.get('total_evidence_items', 0)} evidence items.")
    return {"aggregated_evidence": aggregated, "logs": logs}

def critic_node(state: ResearchState) -> Dict[str, Any]:
    query = state.get("query", "")
    aggregated = state.get("aggregated_evidence", {})
    rev_count = state.get("revision_count", 0) + 1

    logger.info(f"--- Graph Node: Critic Agent Audit (Iteration {rev_count}) ---")
    review = run_critic(query, aggregated, rev_count)
    
    logs = state.get("logs", [])
    logs.append(f"Critic Audit: Valid={review.get('is_valid')}, Score={review.get('quality_score')}.")
    return {"critic_review": review, "revision_count": rev_count, "logs": logs}

def writer_node(state: ResearchState) -> Dict[str, Any]:
    query = state.get("query", "")
    tasks = state.get("tasks", [])
    aggregated = state.get("aggregated_evidence", {})
    review = state.get("critic_review", {})
    session_id = state.get("session_id", str(uuid.uuid4()))

    logger.info("--- Graph Node: Writer Agent Synthesis ---")
    final_report = run_writer(query, tasks, aggregated, review)

    # Persist session into SQLite DB
    try:
        save_research_session(
            session_id=session_id,
            query=query,
            plan=tasks,
            final_report=final_report,
            critic_feedback=review.get("feedback", "")
        )
    except Exception as e:
        logger.error(f"Error persisting session to SQLite: {e}")

    logs = state.get("logs", [])
    logs.append("Writer Agent completed final research report.")
    return {"final_report": final_report, "session_id": session_id, "logs": logs}

# Conditional Routing Logic
def should_continue_or_write(state: ResearchState) -> Literal["writer_node", "retrieval_node"]:
    review = state.get("critic_review", {})
    rev_count = state.get("revision_count", 0)
    is_valid = review.get("is_valid", True)

    if is_valid or rev_count >= 2:
        logger.info("Routing from Critic -> Writer Node")
        return "writer_node"
    else:
        logger.info("Routing from Critic -> Re-Retrieval Node for refinement")
        return "retrieval_node"

# Construct LangGraph Workflow
def build_research_workflow():
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("writer", writer_node)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Add Edges
    workflow.add_edge("planner", "retrieval")
    workflow.add_edge("retrieval", "aggregator")
    workflow.add_edge("aggregator", "critic")

    # Add Conditional Edge from Critic
    workflow.add_conditional_edges(
        "critic",
        should_continue_or_write,
        {
            "writer_node": "writer",
            "retrieval_node": "retrieval"
        }
    )

    workflow.add_edge("writer", END)

    # Compile with memory saver checkpointer
    app_graph = workflow.compile(checkpointer=memory_saver)
    return app_graph

# Global Compiled Workflow Instance
research_graph = build_research_workflow()
