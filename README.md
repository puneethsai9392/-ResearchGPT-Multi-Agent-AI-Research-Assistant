# ResearchGPT — Multi-Agent AI Research Assistant

ResearchGPT is an autonomous multi-agent AI research platform designed to decompose complex queries, perform hybrid RAG vector searches & real-time web retrieval, audit evidence quality with dynamic feedback loops, and synthesize structured, citation-rich research reports.

👉 **[Complete Master Documentation & Interview Q&A Playbook](file:///c:/Users/Hp/Desktop/llmchain/docs/PROJECT_MASTER_DOCUMENTATION.md)**

---

Built with **LangGraph**, **LangChain**, **FastAPI**, **ChromaDB**, **SQLite**, and **Streamlit**.

---

## 🌟 System Architecture

```
                    User Query
                         │
                         ▼
                Planner Agent
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Web Search Agent   RAG Agent      Research Agent
        │                │                │
        └────────────────┼────────────────┘
                         ▼
               Evidence Aggregator
                         │
                         ▼
                Critic Agent
          (Fact Verification & Quality Loop)
                         │
                         ▼
                Writer Agent
                         │
                         ▼
                Final Research Report
                         │
                         ▼
              FastAPI  +  Streamlit
```

---

## 🤖 Agents & Responsibilities

1. **Planner Agent**: Decomposes user research queries into sequential subtasks.
2. **Web Search Agent**: Queries Tavily API / DuckDuckGo for live web snippets & URLs.
3. **RAG Agent**: Performs similarity search over uploaded PDF, DOCX, and TXT documents stored in ChromaDB.
4. **Research Coordinator**: Generates domain analysis notes for each task.
5. **Evidence Aggregator**: Merges, deduplicates, and sectionizes evidence chunks.
6. **Critic Agent**: Audits factual consistency, evaluates quality scores, and triggers refinement loops if necessary.
7. **Writer Agent**: Synthesizes structured markdown research reports with inline bracket citations and references.

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies
```bash
git clone <repository_url>
cd ResearchGPT

# Create Python 3.12 virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Setup
Copy `.env.example` to `.env` and fill in your API keys (optional):
```bash
cp .env.example .env
```

### 3. Run FastAPI Backend
```bash
uvicorn app.api.main:app --reload --port 8000
```
Interactive API documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Streamlit UI
In a separate terminal tab:
```bash
streamlit run frontend/streamlit_app.py
```
Open your browser at: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker Deployment

To launch the full stack (FastAPI Backend + Streamlit Frontend) using Docker Compose:

```bash
docker-compose up --build -d
```
- **Streamlit Web UI**: `http://localhost:8501`
- **FastAPI REST API**: `http://localhost:8000/docs`

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:
```bash
pytest tests/ -v
```

---

## 📡 REST API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/chat` | Runs multi-agent research workflow for a query |
| `POST` | `/upload` | Ingests `.pdf`, `.docx`, `.txt` into ChromaDB vector store |
| `GET` | `/sources` | Lists indexed document sources and vector chunk count |
| `GET` | `/history` | Gets past research session history from SQLite |
| `DELETE`| `/history` | Clears all research history |
| `GET` | `/health` | API health check & vector store metrics |
| `POST` | `/feedback` | Stores user star ratings and comments |

---

## 📄 License
MIT License
