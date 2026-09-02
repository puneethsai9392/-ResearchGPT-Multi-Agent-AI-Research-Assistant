import json
from typing import List, Dict, Any
from app.config import OPENAI_API_KEY, GROQ_API_KEY, LLM_MODEL
from app.utils.logger import get_logger

logger = get_logger("Agent.Planner")

def _get_llm():
    if OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL or "gpt-4o-mini", temperature=0.2)
    elif GROQ_API_KEY:
        from langchain_groq import ChatGroq
        return ChatGroq(model_name="llama-3.1-70b-versatile", temperature=0.2)
    return None

def run_planner(query: str) -> List[str]:
    """
    Planner Agent: Decomposes a user query into logical, structured research subtasks.
    """
    logger.info(f"Planner Agent starting for query: '{query}'")
    llm = _get_llm()

    if llm:
        prompt = f"""
You are the Planner Agent of ResearchGPT.
Analyze the user's research topic or question: "{query}"

Decompose this request into 4-6 distinct, logical, and sequential research tasks.
Format your output EXACTLY as a JSON list of string tasks. No preamble or markdown fences.
Example: ["Define topic X", "Explain architecture of X", "List advantages & challenges of X", "Provide practical applications of X", "Summarize latest developments of X"]
"""
        try:
            res = llm.invoke(prompt)
            content = res.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            tasks = json.loads(content)
            if isinstance(tasks, list) and len(tasks) > 0:
                logger.info(f"Planner generated {len(tasks)} tasks using LLM.")
                return tasks
        except Exception as e:
            logger.warning(f"LLM planner parsing failed: {e}. Falling back to rule-based planner.")

    # Rule-based fallback planner
    topic = query.strip()
    return [
        f"Define and provide core concepts of {topic}.",
        f"Explain key architecture, components, and technical principles of {topic}.",
        f"Identify key advantages, trade-offs, and implementation challenges of {topic}.",
        f"List practical real-world applications and use cases for {topic}.",
        f"Synthesize latest research developments and future outlook for {topic}."
    ]
