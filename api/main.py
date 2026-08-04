import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.graph.workflow import research_graph
from app.rag.loader import process_file
from app.rag.vector_store import vector_store_manager
from app.database.sqlite import (
    get_all_sessions,
    get_session_by_id,
    delete_all_history,
    save_feedback
)
from app.utils.logger import get_logger

logger = get_logger("API.Main")

app = FastAPI(
    title="ResearchGPT API",
    description="Multi-Agent AI Research Assistant using LangGraph, RAG, ChromaDB & FastAPI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class ChatRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Explain Retrieval-Augmented Generation (RAG)."})
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = ""

# API Endpoints
@app.get("/health", tags=["Health"])
def health_check():
    """Health check returning API status and vector store metric."""
    return {
        "status": "online",
        "service": "ResearchGPT API Engine",
        "vector_store_chunks": vector_store_manager.count(),
        "version": "1.0.0"
    }

@app.post("/chat", tags=["Research"])
def execute_research(request: ChatRequest):
    """
    Executes the multi-agent research workflow for a user query.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Research query cannot be empty.")

    session_id = request.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    initial_state = {
        "session_id": session_id,
        "query": request.query,
        "tasks": [],
        "web_results": [],
        "rag_results": [],
        "aggregated_evidence": {},
        "critic_review": {},
        "final_report": "",
        "revision_count": 0,
        "logs": []
    }

    try:
        logger.info(f"Starting research workflow for session '{session_id}'...")
        final_state = research_graph.invoke(initial_state, config=config)

        return {
            "session_id": session_id,
            "query": request.query,
            "tasks": final_state.get("tasks", []),
            "critic_review": final_state.get("critic_review", {}),
            "final_report": final_state.get("final_report", ""),
            "logs": final_state.get("logs", [])
        }
    except Exception as e:
        logger.error(f"Research workflow failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Research workflow error: {str(e)}")

@app.post("/upload", tags=["RAG Knowledge Store"])
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads PDF, DOCX, or TXT document and embeds chunks into ChromaDB vector store.
    """
    temp_dir = "./data/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingest document
        documents = process_file(temp_path)
        if not documents:
            raise HTTPException(status_code=400, detail="Failed to extract text or empty document.")

        vector_store_manager.add_documents(documents)

        return {
            "filename": file.filename,
            "chunks_created": len(documents),
            "total_vector_chunks": vector_store_manager.count(),
            "message": f"Successfully ingested {file.filename} into RAG Knowledge Store."
        }
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded document: {str(e)}")

@app.get("/sources", tags=["RAG Knowledge Store"])
def get_sources():
    """Returns list of ingested documents in vector store."""
    return {
        "sources": vector_store_manager.get_sources(),
        "total_chunks": vector_store_manager.count()
    }

@app.get("/history", tags=["History"])
def get_history(limit: int = 50):
    """Gets research session history from SQLite database."""
    sessions = get_all_sessions(limit=limit)
    return {"sessions": sessions, "count": len(sessions)}

@app.delete("/history", tags=["History"])
def clear_history():
    """Clears research session history and feedback."""
    delete_all_history()
    return {"message": "Successfully cleared research history."}

@app.post("/feedback", tags=["Feedback"])
def submit_feedback(request: FeedbackRequest):
    """Stores user rating and feedback for a research report."""
    save_feedback(request.session_id, request.rating, request.comments)
    return {"message": "Thank you! Your feedback has been recorded."}
