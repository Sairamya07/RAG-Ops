# KnowRAG — AI-Powered Knowledge Assistant

KnowRAG is an end-to-end Retrieval-Augmented Generation (RAG) knowledge assistant designed to answer natural-language questions using a local document knowledge base, dynamically uploaded user documents (.pdf and .txt), and intelligent conversational intent routing. It combines dense semantic retrieval with high-speed LLM generation, enforcing strict factual grounding, page-aware source attribution, conversational greetings, slash commands, and safe refusal of out-of-scope questions.

---

## Features

- **Conversational Greetings & Polite Dialogue**: Recognizes standard greetings (`hello`, `hi`, `hey`, `good morning`, `good evening`, etc.) and casual dialogue (`thanks`, `bye`, `who are you?`, `ok`) with friendly, natural responses without invoking unnecessary vector search.
- **Slash Commands**: Built-in command handling for `/help`, `/show documents`, `/clear`, and `/about`.
- **Brainstorming & Ideation Routing**: Directs open-ended queries (e.g., *"give me cybersecurity project ideas"*) to the conversational LLM while keeping factual document queries strictly grounded.
- **Dynamic Multi-Document Upload**: Upload multiple PDF and TXT documents directly through the Streamlit sidebar.
- **Page-Aware Document Ingestion**: Ingests TXT documents and extracts text page-by-page from PDFs using `pypdf`, tracking page numbers in metadata.
- **Deterministic Duplicate Protection**: Uses SHA-256 content and filename hashing to prevent duplicate chunks in ChromaDB.
- **Incremental ChromaDB Indexing**: Seamlessly embeds and inserts newly uploaded document chunks without deleting or rebuilding existing vectors.
- **Text Chunking**: Splits documents into contextual chunks (chunk size: 512, overlap: 64) with SentenceSplitter, preserving document and page metadata.
- **Semantic Embeddings**: Generates 384-dimensional dense vector embeddings using Hugging Face Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`).
- **Semantic Retrieval**: Retrieves top-k semantically relevant chunks based on cosine similarity across default and uploaded documents.
- **Fast LLM Generation**: Powered by Groq's high-speed inference engine (default: `openai/gpt-oss-20b`).
- **Strict Grounding**: System prompts designed to prevent hallucinations and adhere strictly to retrieved context.
- **Page-Level Source Attribution**: Transparently cites exact source document filenames and page numbers (e.g., `📄 transportation_guidelines.pdf — Page 1`).
- **Out-of-Knowledge-Base Refusal**: Safely rejects unsupported or out-of-domain questions with zero hallucination.
- **Knowledge Base Management UI**: Visual metrics for total documents and chunks, list of uploaded documents, quick action shortcuts, and safe selective clearing.
- **Automated Test Suites**: Includes conversational test suite (`test_conversational_suite.py` - 17/17 PASS), upload verification suite (`test_upload_feature.py` - 6/6 PASS), and baseline regression suite (`evaluate_rag.py` - 6/6 PASS).

---

## Conversational Flow & Architecture

```text
User Input
    ↓
Normalize Input
    ↓
Check Slash Commands (/help, /show documents, /clear, /about)
    ↓
Check Greetings (hello, hi, good morning, etc.)
    ↓
Check Casual Conversation (thanks, bye, who are you?, ok)
    ↓
Check Brainstorming / Ideation Inquiries
    ├── If Brainstorming → Conversational Groq LLM (Direct generation, no RAG context)
    └── If Document Query → RAG Pipeline:
            ↓
          Semantic Similarity Retrieval (ChromaDB top-k)
            ↓
          Retrieved Chunks + Page Metadata
            ↓
          Strictly Grounded Prompt Construction
            ↓
          Groq LLM Generation
            ↓
          Grounded Answer + Page-Level Source Attribution
```

---

## Available Commands

| Command | Description | Example Output |
| :--- | :--- | :--- |
| `/help` | Display guidance on querying, uploading documents, and available commands | Lists all actions and slash commands |
| `/show documents` | Dynamically display all default and user-uploaded documents in ChromaDB | Shows list of available files & chunk counts |
| `/clear` | Clear the chat history in the current session | `"🧹 Chat history cleared. How can I help you?"` |
| `/about` | Display information about KnowRAG's architecture and RAG pipeline | Overview of chunking, embedding, vector store, and LLM |

---

## Technology Stack

- **Language**: Python 3.10+
- **RAG Framework**: [LlamaIndex](https://www.llamaindex.ai/) (`llama-index-core`)
- **PDF Extraction**: [pypdf](https://pypdf.readthedocs.io/) (`pypdf>=4.0.0`)
- **Embedding Model**: [Sentence Transformers](https://www.sbert.net/) (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) (`chromadb`, `llama-index-vector-stores-chroma`)
- **LLM Provider**: [Groq](https://groq.com/) (`llama-index-llms-groq`)
- **User Interface**: [Streamlit](https://streamlit.io/)
- **Environment Management**: `python-dotenv`

---

## Project Structure

```text
KnowRAG/
├── app.py                            # Streamlit web application with conversational UI & uploader
├── health_api.py                     # FastAPI RAG-Ops operational monitoring & /health endpoint
├── run.py                            # Single documented startup command runner
├── data/                             # Source knowledge-base documents
│   ├── academic_programs.txt         # Baseline university document
│   ├── campus_rules.txt              # Baseline university document
│   ├── library_services.txt          # Baseline university document
│   ├── student_services.txt          # Baseline university document
│   ├── university_overview.txt       # Baseline university document
│   ├── pdfs/                         # Source PDFs for reference
│   └── uploads/                      # Staging directory for user-uploaded files
├── src/                              # Core RAG backend modules
│   ├── conversation.py               # Intent classification, greetings, slash commands, & router
│   ├── ingestion.py                  # Multi-format document loading, PDF extraction, & hashing
│   ├── chunking.py                   # Sentence-aware text splitting preserving metadata
│   ├── embeddings.py                 # SentenceTransformer embedding model initialization
│   ├── vector_store.py               # ChromaDB persistent store, incremental indexing & stats
│   ├── retrieval.py                  # Top-k semantic search & retriever caching
│   ├── llm.py                        # Secure Groq LLM initialization & connectivity
│   └── rag_pipeline.py               # Grounded RAG orchestrator with page-aware citations
├── docs/                             # Deployment, rollback, and presentation documentation
│   ├── rollback.md                   # Disaster recovery & rollback runbook (Docker, Git, ChromaDB)
│   ├── part4-submission.md           # Part 4 submission evidence, live outputs, & verification matrix
│   └── demo-script.md                # Timed 5-minute project demonstration walkthrough
├── tests/                            # Automated testing and evaluation
│   ├── __init__.py
│   ├── test_part4_smoke.py           # RAG-Ops Part 4 end-to-end smoke-test verification suite
│   ├── test_part3_docker.py          # RAG-Ops Part 3 containerization verification suite
│   ├── test_health_and_ops.py        # RAG-Ops Part 1 verification suite (health, env, deps, startup)
│   ├── test_part2_rag_ops.py         # RAG-Ops Part 2 offline unit test suite (chunking, retrieval, API)
│   ├── test_conversational_suite.py  # 17-point comprehensive conversational & functional test suite
│   ├── evaluate_rag.py               # Baseline 6-question automated regression suite
│   └── test_upload_feature.py        # Dynamic upload, deduplication, and page retrieval suite
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD (Pytest test suite + Docker Hub publish)
├── Dockerfile                        # Multi-service container spec (Python 3.11-slim, non-root, healthcheck)
├── .dockerignore                     # Docker build exclusions (secrets, venvs, vector dbs, caches)
├── docker-compose.yml                # Docker Compose orchestration (port maps, persistent volumes)
├── chroma_db/                        # Persistent ChromaDB collection directory
├── requirements.txt                  # Pinned project dependencies (FastAPI, Uvicorn, Streamlit, etc.)
├── README.md                         # Project documentation
├── .gitignore                        # Git exclusion rules (keeps .env and uploads secure)
├── .env.example                      # Safe configuration template with placeholders (no real secrets)
└── .env                              # Local environment variables (DO NOT COMMIT)
```

---

## Setup & Installation

### 1. Clone the Repository & Create Virtual Environment (Windows PowerShell)

```powershell
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### 2. Install Pinned Dependencies

```powershell
pip install -r requirements.txt
```

---

## Environment Variables Configuration

Copy the sanitized template `.env.example` to `.env`:

```powershell
# Windows PowerShell
copy .env.example .env

# Linux / macOS / Bash
cp .env.example .env
```

Open `.env` and configure your API credentials:

```env
# Required: Groq Cloud API Key (obtain from https://console.groq.com/keys)
GROQ_API_KEY=your_actual_groq_api_key_here

# Optional: Groq LLM model override (default is openai/gpt-oss-20b)
GROQ_MODEL=openai/gpt-oss-20b

# Optional: Health API host & port (default is 0.0.0.0:8000)
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Streamlit UI port (default is 8501)
STREAMLIT_PORT=8501
```

> **Security Note:** The `.env` file contains secret credentials and must **never** be committed to version control. It is strictly excluded by `.gitignore`. The repository provides `.env.example` as a safe placeholder template.

---

## Running the Application

### Single Documented Startup Command (Recommended)

Run the unified orchestrator to launch both the **FastAPI Health API** and the **Streamlit Interactive UI** concurrently:

```powershell
python run.py
```

This single command automatically starts:
- **RAG-Ops Health Check API**: `http://localhost:8000`
- **KnowRAG Streamlit Assistant**: `http://localhost:8501`

### Verifying the Health Endpoint

Verify that the health check endpoint is operational and returns HTTP 200:

```powershell
# Using curl
curl http://localhost:8000/health

# Output:
# {"status":"ok"}
```

Or using PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
# Output: status: ok
```

### Alternative: Running Services Independently

You can also run the components individually:

- **Health Check API only**:
  ```powershell
  python health_api.py
  # Or: uvicorn health_api:app --host 0.0.0.0 --port 8000
  ```

- **Streamlit Web Application only**:
  ```powershell
  python -m streamlit run app.py
  ```

---

## Docker Containerization & Orchestration (Part 3)

KnowRAG is fully containerized using Docker and Docker Compose to provide consistent, reproducible, and isolated environments across development, testing, staging, and production.

### Multi-Service Architecture in Docker

A single lightweight container orchestrates both core services via `run.py`:
1. **RAG-Ops Health & Monitoring API (FastAPI)**: Exposed on port **`8000`** with `/health`, `/ask`, and OpenAPI docs.
2. **KnowRAG Interactive Assistant (Streamlit)**: Exposed on port **`8501`** for the conversational web interface.

### Security & Optimization Highlights

- **Base Image**: `python:3.11-slim` for minimized image footprint and reduced attack surface.
- **Non-Root Execution**: Runs under a dedicated unprivileged user (`appuser`, UID 1000) rather than `root`.
- **Layer Caching**: `requirements.txt` is copied and installed prior to copying the application source code.
- **Leakage Prevention (`.dockerignore`)**: Excludes `.env`, `.git`, `.venv`, `__pycache__`, local database caches, and editor configurations so credentials and bloat are never baked into images.
- **Integrated Health Check**: Container defines a native Docker `HEALTHCHECK` pinging `http://localhost:8000/health`.
- **Persistent Storage**: Docker Compose mounts `./chroma_db` and `./data` so vector embeddings and uploaded documents survive container destruction and restarts.

### 1. Running with Docker Compose (Recommended)

Start the entire application in detached mode:

```bash
docker compose up -d --build
```

View real-time logs:

```bash
docker compose logs -f
```

Verify service status and healthcheck:

```bash
docker compose ps
```

Stop and remove the container:

```bash
docker compose down
```

### 2. Building & Running with Docker CLI Directly

Build the Docker image:

```bash
docker build -t knowrag:latest .
```

Run the container with your Groq API key:

```bash
docker run -d \
  --name knowrag-service \
  -p 8000:8000 \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_groq_api_key_here" \
  -v "${PWD}/chroma_db:/app/chroma_db" \
  -v "${PWD}/data:/app/data" \
  knowrag:latest
```

### 3. Verifying the Container Health Endpoint

Test the container's operational health endpoint from your host machine:

```bash
# Using curl
curl http://localhost:8000/health

# Output:
# {"status":"ok"}
```

Or in PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
# Output: status: ok
```

Access the web interfaces:
- **Streamlit Assistant UI**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Health & API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. CI/CD Pipeline & Automated Publishing to Docker Hub

The repository includes an automated GitHub Actions workflow at [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml):

1. **Test Job**: Runs the full automated test suite (`tests/test_part2_rag_ops.py`, `tests/test_health_and_ops.py`, `tests/test_part3_docker.py`) across an isolated `ubuntu-latest` runner on Python 3.11.
2. **Build & Publish Job**: Automatically triggers **only after tests pass** on pushes to the `main` branch.
   - Sets up Docker Buildx.
   - Securely logs into Docker Hub using GitHub Encrypted Secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`).
   - Builds the production multi-platform image with GitHub Actions caching (`type=gha`).
   - Tags the image as `latest` and with the commit SHA (`<username>/knowrag:latest`).
   - Pushes the image to Docker Hub with zero hardcoded credentials.

#### Required GitHub Secrets Configuration:

| Secret Name | Description |
| :--- | :--- |
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Your Docker Hub Personal Access Token (PAT) with Read/Write permissions |

---

## Deployment, Rollback & Submission (Part 4)

KnowRAG has been deployed and operationalized in a hardened multi-service Docker container running on a Linux engine (`linux/amd64`), thoroughly verified with live operational health and question-answering probes, backed by automated smoke tests, and documented with disaster recovery procedures.

### Operational Verification Summary

- **Live Container Status**: Running on Docker Desktop Linux Engine (`knowrag-service`, `Up ... (healthy)`).
- **Operational Health Probe**: `GET /health` returns `HTTP 200 OK` and `{"status": "ok"}` via Uvicorn.
- **Service Discovery**: `GET /` returns `HTTP 200 OK` and `{"status": "ok", "service": "KnowRAG"}`.
- **RAG Inference**: `POST /ask` returns `HTTP 200 OK` with grounded answer and page-level source citations.
- **Release Version**: Tagged as `v1.0.0` following standard semantic versioning.

### Dedicated Documentation & Runbooks

- **[Deployment Rollback & Disaster Recovery Runbook](docs/rollback.md)**: Actionable, step-by-step PowerShell and Bash commands for container rollbacks, git tag checkouts, ChromaDB vector store snapshots, and health verification gates.
- **[Part 4 Submission & Evidence Report](docs/part4-submission.md)**: Complete deployment evidence, raw command outputs, container inspection logs, and requirement completion matrix.
- **[Five-Minute Demonstration Script](docs/demo-script.md)**: Timed, minute-by-minute presentation walkthrough for evaluators and stakeholders.

---

## Running Automated Evaluation & Tests

### 1. RAG-Ops Part 1 Verification Suite (Health Endpoint, Config, Deps, Startup)

```powershell
python tests\test_health_and_ops.py
```

| Test # | Objective | Result |
| :---: | :--- | :---: |
| **01** | `GET /health` Returns HTTP 200 & `{"status":"ok"}` | **PASS** |
| **02** | `GET /` Root Service Discovery Endpoint | **PASS** |
| **03** | Safe `.env.example` Template & Secret Sanitization | **PASS** |
| **04** | Repository `.gitignore` Protection Rules | **PASS** |
| **05** | Pinned Dependencies in `requirements.txt` | **PASS** |
| **06** | Single Startup Runner (`run.py`) Command Integrity | **PASS** |

**Result**: **6/6 PASS (100%)**

### 2. RAG-Ops Part 2 Offline Pytest Suite (Mocked & Offline Unit Tests)

Execute the offline pytest suite verifying chunking, top-k retrieval, `/health`, Question API schema, and empty-question validation:

```powershell
pytest tests\test_part2_rag_ops.py -v
```

Or run all pytest suites:

```powershell
pytest -v
```

| Test Function | Target Component | Status |
| :--- | :--- | :---: |
| `test_text_chunking_splits_document_and_preserves_metadata` | Text Chunking & Metadata Preservation | **PASS** |
| `test_text_chunking_preserves_single_short_document` | Short Document Chunking Boundary | **PASS** |
| `test_top_k_retrieval_returns_correct_k_nodes` | Top-k Semantic Retrieval with Mock Index | **PASS** |
| `test_top_k_retrieval_respects_custom_k_parameter` | Top-k Retrieval Parameter Flexibility | **PASS** |
| `test_get_health_endpoint_returns_200_and_ok` | `GET /health` HTTP 200 & `{"status":"ok"}` | **PASS** |
| `test_get_root_endpoint_returns_200_and_status` | `GET /` Service Discovery | **PASS** |
| `test_question_api_json_structure` | `POST /ask` Response JSON Schema & Types | **PASS** |
| `test_question_api_aliases_return_consistent_structure` | `POST /question` & `POST /query` Aliases | **PASS** |
| `test_empty_question_handling_empty_string` | `POST /ask` with `""` -> HTTP 400 | **PASS** |
| `test_empty_question_handling_whitespace_only` | `POST /ask` with Whitespace -> HTTP 400 | **PASS** |
| `test_empty_question_handling_missing_payload` | `POST /ask` with Empty Payload -> HTTP 400 | **PASS** |
| `test_empty_question_handling_conversation_module` | Conversational Router Empty Fallback | **PASS** |
| `test_rag_pipeline_offline_with_mocked_llm` | Offline Grounded RAG Generation | **PASS** |

**Result**: **13/13 PASS (100% Offline, 0 API Calls)**

### 3. RAG-Ops Part 3 Containerization & Docker Suite (Dockerfile, Compose, Security, CI/CD)

```powershell
python tests\test_part3_docker.py
```

| Test # | Objective | Result |
| :---: | :--- | :---: |
| **01** | Dockerfile Security, `python:3.11-slim`, `appuser`, Ports 8000 & 8501, & `HEALTHCHECK` | **PASS** |
| **02** | `.dockerignore` Security Rules & Secret Isolation (`.env` protected, `!.env.example` retained) | **PASS** |
| **03** | `docker-compose.yml` Specification, Port Mappings, Persistent Volumes, & Healthcheck | **PASS** |
| **04** | GitHub Actions CI/CD Pipeline Docker Build & Publish Workflow with GitHub Secrets | **PASS** |

**Result**: **4/4 PASS (100%)**

### 4. RAG-Ops Part 4 End-to-End Smoke Test Suite

```powershell
python tests\test_part4_smoke.py
```

| Test # | Objective | Result |
| :---: | :--- | :---: |
| **01** | `GET /health` Returns HTTP 200 & `{"status":"ok"}` | **PASS** |
| **02** | `GET /` Root Service Discovery Endpoint | **PASS** |
| **03** | `POST /ask` Empty Input Validation (HTTP 400 Bad Request) | **PASS** |
| **04** | `POST /ask` Greeting Schema & Response Structure | **PASS** |
| **05** | `docs/rollback.md` Integrity & Command Verification | **PASS** |
| **06** | `docs/part4-submission.md` Evidence & Completion Status | **PASS** |
| **07** | `docs/demo-script.md` 5-Minute Timed Walkthrough | **PASS** |

**Result**: **7/7 PASS (100%)**

### 5. Comprehensive Conversational & Functional Test Suite (17 Tests)

```powershell
python tests\test_conversational_suite.py
```

| Test # | Objective | Result |
| :---: | :--- | :---: |
| **01** | Greeting Detection | **PASS** |
| **02** | `"hello"` Response | **PASS** |
| **03** | `"hi"` Response | **PASS** |
| **04** | `/help` Command | **PASS** |
| **05** | `/show documents` Command (Dynamic List) | **PASS** |
| **06** | `/clear` Command Handling | **PASS** |
| **07** | `/about` Command | **PASS** |
| **08** | `"thanks"` Response | **PASS** |
| **09** | `"bye"` Response | **PASS** |
| **10** | Brainstorming / General Question Routing | **PASS** |
| **11** | Existing RAG Question Grounding | **PASS** |
| **12** | Out-of-Knowledge-Base Safe Refusal | **PASS** |
| **13** | PDF Upload & Query | **PASS** |
| **14** | TXT Upload & Query | **PASS** |
| **15** | Duplicate Upload Protection | **PASS** |
| **16** | Source Citation Verification | **PASS** |
| **17** | Missing `GROQ_API_KEY` Graceful Handling | **PASS** |

**Result**: **17/17 PASS (100%)**

### 6. Baseline Regression Suite

```powershell
python tests\evaluate_rag.py
```

**Result**: **6/6 PASS (100%)**

### 7. Dynamic Upload Feature Test Suite

```powershell
python tests\test_upload_feature.py
```

**Result**: **6/6 PASS (100%)**

---

## Security Principles

- **Zero Credential Exposure**: API keys are dynamically loaded via environment variables and never hardcoded or printed.
- **Git Protection**: `.env` and `data/uploads/*` are explicitly ignored in `.gitignore`.
- **UI Sanitization**: Streamlit displays friendly alerts if credentials are missing without leaking stack traces or keys.
- **Closed Knowledge Boundaries**: Grounding prompts strictly restrict the LLM to retrieved context for factual questions.
