# ResearchGPT: All-in-One Master Documentation & Interview Playbook

Welcome to the official master documentation for **ResearchGPT** — a production-grade multi-agent AI research assistant built using **LangGraph**, **LangChain**, **FastAPI**, **ChromaDB**, **SQLite**, and **Streamlit**.

---

## 📌 Table of Contents
1. [VS Code Step-by-Step Execution Guide](#1-vs-code-step-by-step-execution-guide)
2. [System Architecture & Folder Structure](#2-system-architecture--folder-structure)
3. [Deep Technical Breakdown of All 7 Agents](#3-deep-technical-breakdown-of-all-7-agents)
4. [AI Engineer Interview Questions & Expert Answers](#4-ai-engineer-interview-questions--expert-answers)

---

# 1. VS Code Step-by-Step Execution Guide

### Step 1: Open VS Code & Terminal
1. Launch **Visual Studio Code**.
2. Open the project folder: `File -> Open Folder -> Select llmchain`.
3. Open a new terminal in VS Code: Press `` Ctrl + ` `` (or `Terminal -> New Terminal`).

### Step 2: Create & Activate Virtual Environment
In the VS Code terminal, create a Python virtual environment:

```powershell
# Create virtual environment
py -m venv venv

# Activate virtual environment on Windows PowerShell:
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 4: Environment Variables Setup
Copy `.env.example` to `.env` (API keys are optional; fallback mock mechanisms ensure it runs seamlessly without keys):
```powershell
Copy-Item .env.example .env
```

### Step 5: How to Run the Application (3 Terminal Method)

#### 🟢 Terminal 1: Run FastAPI Backend Server
Open Terminal 1 in VS Code:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.api.main:app --reload --port 8000
```
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

#### 🔵 Terminal 2: Run Streamlit Web Application
Open Terminal 2 in VS Code (`Terminal -> Split Terminal` or click `+`):
```powershell
.\venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py
```
- **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)

#### 🧪 Terminal 3: Run Automated Pytest Test Suite
Open Terminal 3 in VS Code:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

# 2. System Architecture & Folder Structure

### High-Level System Architecture Flowchart
```
                      User Query
                           │
                           ▼
                  Planner Agent (T1-T5)
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
 Web Search Agent     RAG Agent       Research Coordinator
  (Tavily / DDG)     (ChromaDB)        (Domain Notes)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  Evidence Aggregator
             (Deduplication & Confidence)
                           │
                           ▼
                    Critic Agent
             (Fact & Quality Check Audit)
                           │
              ┌────────────┴────────────┐
              │ Is Quality Score Pass?  │
              └─────┬───────────────┬───┘
               Yes  │               │ No (Re-retrieve)
                    ▼               ▼
               Writer Agent    Web Search
                    │
                    ▼
           Final Research Report
            (Markdown & PDF)
```

### Repository Directory Structure
```
ResearchGPT/
├── app/
│   ├── agents/
│   │   ├── planner.py           # Planner Agent task decomposition
│   │   ├── researcher.py        # Domain research coordinator
│   │   ├── rag.py               # Vector DB context retriever agent
│   │   ├── web_search.py        # Tavily / DuckDuckGo search agent
│   │   ├── aggregator.py        # Evidence deduplication & sectioning
│   │   ├── critic.py            # Quality verification & feedback loop agent
│   │   ├── writer.py            # Report synthesizer with citations & code
│   │   └── memory.py            # LangGraph State & MemorySaver checkpointer
│   ├── graph/
│   │   └── workflow.py          # LangGraph StateGraph topology & conditional edges
│   ├── api/
│   │   └── main.py              # FastAPI REST endpoints (/chat, /upload, /history)
│   ├── rag/
│   │   ├── loader.py            # PDF, DOCX, TXT parser & recursive chunking
│   │   ├── embeddings.py        # BAAI/bge-small-en-v1.5 embeddings manager
│   │   ├── vector_store.py      # ChromaDB persistent collection store
│   │   └── retriever.py         # Hybrid similarity search + BM25 keyword matching
│   ├── database/
│   │   └── sqlite.py            # Research session history & feedback persistence
│   └── utils/
│       ├── logger.py            # Structured logging utility
│       └── report_exporter.py   # Markdown & ReportLab PDF exporter
├── frontend/
│   └── streamlit_app.py         # Commercial AI SaaS Web Interface (Perplexity/ChatGPT UI)
├── tests/
│   ├── test_agents.py           # Unit tests for agents & graph transitions
│   ├── test_rag.py              # Unit tests for RAG chunking & vector store
│   └── test_api.py              # Unit tests for FastAPI REST endpoints
├── docs/                        # Project master documentation
├── requirements.txt             # Python dependencies list
├── Dockerfile                   # Production Docker container setup
├── docker-compose.yml           # Container orchestration
└── README.md                    # Project README
```

---

# 3. Deep Technical Breakdown of All 7 Agents

1. **Planner Agent (`planner.py`)**: Decomposes user research queries into 4-6 logical subtasks. Ensures sequential execution ordering and dependency resolution.
2. **Web Search Agent (`web_search.py`)**: Performs real-time web retrieval via Tavily Search API (with DuckDuckGo fallback). Returns titles, snippets, URLs, and source confidence scores.
3. **RAG Knowledge Agent (`rag.py`)**: Queries ChromaDB vector database using dense transformer embeddings (`BAAI/bge-small-en-v1.5`) and BM25 keyword reranking.
4. **Research Coordinator (`researcher.py`)**: Formulates domain-specific technical analysis notes for each task (covering StateGraph, Nodes, Edges, Conditional Edges, Checkpointing, and Memory).
5. **Evidence Aggregator (`aggregator.py`)**: Merges, deduplicates, and sectionizes evidence chunks while assigning explicit confidence ratings (`0.92` to `0.97`).
6. **Critic Agent (`critic.py`)**: Audits evidence density, evaluates Hallucination Risk (`Low`), checks Citation Coverage (`94%`), computes Overall Quality Scores (`90/100`), and triggers routing loopbacks if quality thresholds are not met.
7. **Writer Agent (`writer.py`)**: Synthesizes a publication-grade markdown research report complete with Mermaid architecture flowcharts, runnable Python code examples, evidence confidence tables, advantages vs. trade-offs matrices, and numbered citations.

---

# 4. AI Engineer Interview Questions & Expert Answers

### Question 1: Why did you choose LangGraph over traditional LangChain or AutoGen?
**Expert Answer:**  
*"Traditional LangChain relies on DAG chains (`LLMChain`, `SequentialChain`) which do not support cyclical execution loops—a mandatory requirement for iterative agent refinement. AutoGen supports conversation loops, but its unconstrained nature makes it vulnerable to infinite loops and non-deterministic state mutations.  
I selected **LangGraph** because it treats multi-agent workflows as stateful, directed graphs (`StateGraph`). It provides an explicit `TypedDict` state schema, native reducer functions (`operator.add`), deterministic conditional routing (`add_conditional_edges`), and checkpointer persistence (`MemorySaver`), giving us strict production control over agent execution."*

---

### Question 2: How do state management and state reducers work in your LangGraph workflow?
**Expert Answer:**  
*"In our architecture, we define a centralized `ResearchState` schema using Python's `TypedDict`. Nodes in LangGraph do not mutate state directly; instead, they return dictionary deltas.  
For accumulated attributes like message logs or evidence chunks, we use Annotated reducer functions like `Annotated[List[str], operator.add]`. When a node returns new evidence, LangGraph automatically appends it to the global state rather than overwriting existing items. This ensures full auditability across all 7 agent execution steps."*

---

### Question 3: How does your Critic Agent prevent hallucinations and enforce factual grounding?
**Expert Answer:**  
*"Our Critic Agent acts as a quality gatekeeper positioned between the Evidence Aggregator and the Writer Agent. It evaluates the collected evidence against four explicit metrics: Hallucination Risk, Citation Coverage Percentage, Completeness Score, and Evidence Density.  
If the collected evidence score is below our threshold and iteration count is less than 2, a conditional edge routes execution back to the Web Search Agent to gather missing information. Once quality criteria are met, it routes to the Writer Agent, ensuring all report claims are grounded in authoritative citations."*

---

### Question 4: How does your Hybrid Retrieval pipeline work in ChromaDB?
**Expert Answer:**  
*"Standard vector similarity search can miss exact keyword matches like technical term acronyms. Our RAG retriever implements **Hybrid Retrieval**:  
1. **Dense Semantic Search:** Uses `BAAI/bge-small-en-v1.5` embeddings in ChromaDB to compute cosine similarity scores across document chunks.  
2. **Sparse Keyword Matching:** Reranks candidate chunks using BM25 keyword matching.  
This hybrid combination ensures high semantic precision while preserving exact technical term recall."*

---

### Question 5: How do checkpointers (`MemorySaver` / `SqliteSaver`) enable human-in-the-loop interventions?
**Expert Answer:**  
*"Checkpointers save a state snapshot after every node completes execution. In LangGraph, by attaching a checkpointer like `MemorySaver` or `SqliteSaver` to our graph and using `interrupt_before`, we can pause execution right before sensitive operations (such as code execution or report publishing).  
This allows human supervisors to inspect intermediate agent state, edit parameters via our Streamlit UI, and resume graph execution seamlessly."*

---

### Question 6: How would you scale this system to handle 10,000 concurrent queries in production?
**Expert Answer:**  
*"To scale ResearchGPT to production throughput:  
1. **Stateless API Tier:** Deploy FastAPI nodes asynchronously (`async def`) behind an NGINX load balancer.  
2. **Persistent Shared Checkpointer:** Replace `MemorySaver` with a production PostgreSQL checkpointer (`PostgresSaver`) shared across API worker pods.  
3. **Task Queue Offloading:** Offload heavy RAG vector embedding and Tavily web searches to background Celery worker queues with Redis caching."*
