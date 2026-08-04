from typing import List, Dict, Any
from app.utils.logger import get_logger

logger = get_logger("Agent.Aggregator")

def run_evidence_aggregator(
    web_results: List[Dict[str, Any]],
    rag_results: List[Dict[str, Any]],
    research_notes: List[Dict[str, Any]],
    tasks: List[str]
) -> Dict[str, Any]:
    """
    Evidence Aggregator: Merges, deduplicates, assigns confidence scores, and structures evidence.
    """
    all_evidence = []
    seen_content = set()

    # Process RAG vector DB chunks
    for r in rag_results:
        text = r.get("snippet", "").strip()
        if text and text not in seen_content:
            seen_content.add(text)
            all_evidence.append({
                "content": text,
                "source": r.get("source", "Uploaded Document"),
                "type": "vector_db",
                "url": None,
                "confidence": 0.97
            })

    # Process Web Search results
    for w in web_results:
        snippet = w.get("snippet", "").strip()
        if snippet and snippet not in seen_content:
            seen_content.add(snippet)
            all_evidence.append({
                "content": snippet,
                "source": w.get("title", "Web Source"),
                "type": "web",
                "url": w.get("url", None),
                "confidence": 0.95
            })

    # Include domain research notes
    for note in research_notes:
        ctx = note.get("domain_context", "").strip()
        if ctx and ctx not in seen_content:
            seen_content.add(ctx)
            all_evidence.append({
                "content": ctx,
                "source": f"Research Note ({note.get('task_id')})",
                "type": "domain_analysis",
                "url": None,
                "confidence": 0.92
            })

    # Group evidence by planned task categories
    sectioned_evidence = {}
    for idx, task in enumerate(tasks):
        section_key = f"Task_{idx+1}: {task}"
        matched_items = [
            ev for ev in all_evidence 
            if any(word in ev["content"].lower() for word in task.lower().split() if len(word) > 3)
        ]
        if not matched_items and all_evidence:
            matched_items = [all_evidence[idx % len(all_evidence)]]

        sectioned_evidence[section_key] = matched_items

    aggregated = {
        "total_evidence_items": len(all_evidence),
        "raw_evidence": all_evidence,
        "sectioned_evidence": sectioned_evidence,
        "research_notes": research_notes
    }

    logger.info(f"Evidence Aggregator collected {len(all_evidence)} unique evidence items across {len(tasks)} tasks.")
    return aggregated
