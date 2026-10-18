# KnowRAG — Five-Minute Project Demonstration Script

**Project**: KnowRAG AI-Powered Knowledge Assistant & RAG-Ops  
**Presenter**: Ramya Thangella  
**Repository**: [https://github.com/Sairamya07/RAG-Ops](https://github.com/Sairamya07/RAG-Ops)  
**Total Target Duration**: 5 Minutes (00:00 – 05:00)

---

## 📋 Presenter Pre-Demo Checklist

Before starting the recording or presentation:
- [ ] Docker container is running: `docker compose up -d` (or `python run.py`).
- [ ] Browser Tab 1: KnowRAG Streamlit Assistant at `http://localhost:8501`.
- [ ] Browser Tab 2: RAG-Ops FastAPI OpenAPI documentation at `http://localhost:8000/docs`.
- [ ] Browser Tab 3: GitHub repository at `https://github.com/Sairamya07/RAG-Ops`.
- [ ] Terminal window open in PowerShell at the project root directory.
- [ ] Sample PDF or TXT file on Desktop ready for upload demonstration.

---

## ⏱️ Minute-by-Minute Demonstration Walkthrough

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 00:00 - 01:00 │ Project Overview & RAG Architecture                    │
│ 01:00 - 02:00 │ Single Startup, Health Check & Operational API         │
│ 02:00 - 03:00 │ Conversational Router, Slash Commands & Factual RAG    │
│ 03:00 - 04:00 │ Dynamic Document Upload & Deduplication Protection     │
│ 04:00 - 05:00 │ Containerization, CI/CD Automation & Rollback Runbook  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Minute 1 (00:00 – 01:00): Project Overview & RAG Architecture

#### 🎯 Goal:
Introduce KnowRAG, explain the high-level architecture, and highlight how it solves hallucination and operational monitoring in enterprise AI.

#### 🎙️ Presenter Script:
> *"Hello everyone! Welcome to the demonstration of **KnowRAG**, an enterprise-grade AI knowledge assistant built on modern Retrieval-Augmented Generation and RAG-Ops principles."*
>
> *"Traditional LLMs frequently suffer from hallucinations and lack domain context. KnowRAG addresses this through a robust, multi-layer architecture:
> 1. Dense vector embeddings using Hugging Face Sentence Transformers (`all-MiniLM-L6-v2`),
> 2. Persistent vector storage with ChromaDB,
> 3. LlamaIndex semantic retrieval with strict factual grounding, and
> 4. Fast inference powered by Groq's high-speed cloud engine."*
>
> *"Crucially, KnowRAG is built with operational reliability at its core: featuring dual-service FastAPI and Streamlit orchestration, Docker containerization, comprehensive automated test coverage, and a full rollback runbook."*

#### 🖥️ Visual Action:
- Show GitHub repository README architecture diagram.
- Highlight project layout in VS Code / IDE.

---

### Minute 2 (01:00 – 02:00): Single Startup, Health Check & Operational API

#### 🎯 Goal:
Demonstrate the single documented startup runner (`run.py`), Docker Compose containerization, and the `/health` operational monitoring endpoint.

#### 🎙️ Presenter Script:
> *"Let's examine how easy it is to operate KnowRAG. Rather than requiring engineers to manage disparate background processes, KnowRAG provides a single unified startup runner via `python run.py`, as well as a production-ready `docker-compose.yml`."*
>
> *"Here in the terminal, our multi-service container is already running under an unprivileged user `appuser` on a minimal Python 3.11-slim base image. Both the FastAPI monitoring API on port 8000 and the Streamlit web UI on port 8501 are active."*
>
> *"Now let's check our operational health endpoint. When we send a GET request to `http://localhost:8000/health`, it immediately returns HTTP 200 OK with `{"status": "ok"}`. This endpoint powers our native Docker `HEALTHCHECK` and automated liveness probes."*

#### 🖥️ Visual Action:
- In PowerShell, run:
  ```powershell
  curl.exe -i http://localhost:8000/health
  ```
- Point out `HTTP/1.1 200 OK` and `{"status":"ok"}`.
- Switch to Browser Tab 2 (`http://localhost:8000/docs`) to quickly display the interactive Swagger documentation.

---

### Minute 3 (02:00 – 03:00): Conversational Router, Slash Commands & Grounded RAG

#### 🎯 Goal:
Demonstrate intelligent conversational intent classification, built-in slash commands, strictly grounded answers with page-level citations, and safe out-of-scope refusal.

#### 🎙️ Presenter Script:
> *"Now let's transition to the user experience in our Streamlit web interface on port 8501."*
>
> *"KnowRAG isn't just a basic search box; it features an intelligent conversational router. For example, if I type a greeting like `'hello'`, it recognizes the greeting intent instantly without performing an expensive vector search."*
>
> *"We also support built-in slash commands. Let's type `/show documents` — the system dynamically queries our vector database and displays all indexed knowledge-base files and chunk counts."*
>
> *"Now let's ask a factual domain question: `'What is the mission of the university?'` Notice the response: KnowRAG provides a concise, factually accurate answer grounded strictly in our university overview document, complete with transparent source attribution citing the exact source file."*
>
> *"What happens if we ask an out-of-domain question, like `'What is the capital of Mars?'` KnowRAG safely refuses to hallucinate, stating that the answer cannot be found in the provided knowledge base."*

#### 🖥️ Visual Action:
- In Streamlit UI (`http://localhost:8501`):
  1. Type: `Hello` -> Observe friendly instant greeting.
  2. Type: `/show documents` -> Observe dynamic document table.
  3. Type: `What is the mission of the university?` -> Show grounded answer + source citation `university_overview.txt`.
  4. Type: `What is the capital of Mars?` -> Show safe out-of-scope refusal.

---

### Minute 4 (03:00 – 04:00): Dynamic Document Upload & Deduplication Protection

#### 🎯 Goal:
Demonstrate the Streamlit sidebar document uploader, page-aware text extraction, SHA-256 deduplication hashing, and incremental vector indexing.

#### 🎙️ Presenter Script:
> *"One of KnowRAG's most powerful capabilities is dynamic, runtime knowledge ingestion. Users can upload new PDF and TXT documents directly through the sidebar without stopping or rebuilding the server."*
>
> *"When a document is uploaded, KnowRAG parses it page-by-page using `pypdf`, breaks it into contextual chunks with sentence boundary preservation, and generates embeddings on the fly."*
>
> *"To protect our vector database from bloat and duplicate embeddings, KnowRAG implements deterministic SHA-256 content hashing. If a user attempts to upload the exact same document twice, KnowRAG detects the duplicate and prevents duplicate insertions, keeping our retrieval index clean and fast."*

#### 🖥️ Visual Action:
- In the sidebar, drag and drop a test file (e.g. `data/academic_programs.txt` or a sample PDF).
- Click **"Process & Ingest Document"**.
- Point out the success banner and the updated Total Documents / Total Chunks metrics.
- Re-run `/show documents` in the chat to confirm the newly indexed file appears.

---

### Minute 5 (04:00 – 05:00): Containerization, CI/CD Automation & Rollback Runbook

#### 🎯 Goal:
Highlight engineering maturity: GitHub Actions CI/CD pipeline, automated test suites (Parts 1–4), and the formal rollback runbook (`docs/rollback.md`).

#### 🎙️ Presenter Script:
> *"Finally, let's look at the DevOps and reliability engineering behind KnowRAG. Quality assurance is automated at every level:
> - Part 1 tests verify operational health and configuration safety,
> - Part 2 unit tests verify chunking and retrieval in an offline environment,
> - Part 3 tests verify containerization specifications, and
> - Part 4 tests verify end-to-end smoke testing."*
>
> *"Across all automated test suites, KnowRAG achieves a 100% pass rate with 23 passing unit tests and comprehensive smoke test validation."*
>
> *"Our GitHub Actions workflow in `.github/workflows/ci.yml` enforces test gates on every push, building and publishing multi-platform Docker images to Docker Hub securely via GitHub Encrypted Secrets."*
>
> *"And if an incident ever occurs in production, our newly authored `docs/rollback.md` runbook provides one-click PowerShell and Bash procedures to roll back containers, restore ChromaDB vector snapshots, and verify health."*
>
> *"Thank you for watching the KnowRAG demonstration!"*

#### 🖥️ Visual Action:
- In PowerShell, run the automated test suite to show all passing tests:
  ```powershell
  pytest -v
  ```
- Show `docs/rollback.md` and `docs/part4-submission.md` in the editor.
- Conclude cleanly within the 5-minute window.

---

## 🛠️ Backup Contingency Q&A

| Potential Question / Issue | Prepared Response |
| :--- | :--- |
| **"What happens if Groq API is temporarily unavailable?"** | KnowRAG's conversational module gracefully catches upstream LLM timeouts and presents a clear, polite error notification without leaking API keys or crashing the server. |
| **"How is vector index persistence handled across container restarts?"** | `docker-compose.yml` mounts host volumes `./chroma_db` and `./data` into the container, so all existing vectors and uploaded files persist across container redeployments. |
| **"How are credentials secured?"** | Keys are stored only in local `.env` which is protected by `.gitignore` and `.dockerignore`. Images built by CI/CD receive keys via runtime injection only. |
