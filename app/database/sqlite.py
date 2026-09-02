import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.config import SQLITE_DB_PATH
from app.utils.logger import get_logger

logger = get_logger("Database.SQLite")

def get_db_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables for research history and feedback."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Research Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_sessions (
        session_id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        plan JSON,
        final_report TEXT,
        critic_feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES research_sessions(session_id)
    )
    """)

    conn.commit()
    conn.close()
    logger.info("SQLite database tables initialized.")

def save_research_session(session_id: str, query: str, plan: List[str], final_report: str, critic_feedback: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO research_sessions (session_id, query, plan, final_report, critic_feedback, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, query, json.dumps(plan), final_report, critic_feedback, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

def get_all_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, query, plan, final_report, critic_feedback, created_at FROM research_sessions ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "session_id": r["session_id"],
            "query": r["query"],
            "plan": json.loads(r["plan"]) if r["plan"] else [],
            "final_report": r["final_report"],
            "critic_feedback": r["critic_feedback"],
            "created_at": r["created_at"]
        })
    return results

def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, query, plan, final_report, critic_feedback, created_at FROM research_sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "session_id": row["session_id"],
        "query": row["query"],
        "plan": json.loads(row["plan"]) if row["plan"] else [],
        "final_report": row["final_report"],
        "critic_feedback": row["critic_feedback"],
        "created_at": row["created_at"]
    }

def delete_all_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_feedback")
    cursor.execute("DELETE FROM research_sessions")
    conn.commit()
    conn.close()
    logger.info("Cleared all research history and user feedback.")

def save_feedback(session_id: str, rating: int, comments: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_feedback (session_id, rating, comments, created_at)
    VALUES (?, ?, ?, ?)
    """, (session_id, rating, comments, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

# Initialize DB on module load
init_db()
