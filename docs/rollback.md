# KnowRAG — Deployment Rollback & Disaster Recovery Runbook

This document defines the standardized rollback and recovery procedures for the **KnowRAG** RAG-Ops platform. It provides actionable, step-by-step PowerShell and Bash commands to safely revert deployments, recover vector data, and verify system operational integrity.

---

## 1. Rollback Overview & Trigger Criteria

A rollback must be initiated immediately if any of the following conditions occur post-deployment:

| Trigger Condition | Detection Method | Severity | Action |
| :--- | :--- | :--- | :--- |
| **Health Check Failure** | `GET /health` returns non-200 or times out | **Critical** | Immediate container rollback to prior image |
| **Docker Crash Loop** | `docker ps` shows `Restarting` or `unhealthy` | **Critical** | Revert image & restart container |
| **LLM / Vector Regression** | Semantic retrieval returns corrupted nodes or unhandled exceptions | **High** | Revert code commit & restore vector index |
| **Port / Binding Conflict** | Ports `8000` or `8501` fail to bind or throw EADDRINUSE | **Medium** | Terminate conflicting process or roll back config |

---

## 2. Pre-Rollback Diagnostics

Before rolling back, quickly capture diagnostic evidence to identify the root cause:

### Windows PowerShell

```powershell
# 1. Check container runtime status and health
docker ps -a --filter "name=knowrag-service"

# 2. Inspect Docker healthcheck logs
docker inspect --format='{{json .State.Health}}' knowrag-service

# 3. View the latest 50 lines of container stdout/stderr
docker logs --tail 50 knowrag-service

# 4. Probe the health endpoint directly
curl.exe -i http://localhost:8000/health
```

### Linux / Bash

```bash
# 1. Check container status
docker ps -a --filter "name=knowrag-service"

# 2. Inspect healthcheck
docker inspect --format='{{json .State.Health}}' knowrag-service

# 3. View recent logs
docker logs --tail 50 knowrag-service

# 4. Test health endpoint
curl -i http://localhost:8000/health
```

---

## 3. Docker Container Rollback Procedures

### Strategy A: Rollback Using Docker Compose (Recommended)

If the active deployment was launched via Docker Compose, roll back by pointing to the previous image tag or rolling back the git commit:

#### Windows PowerShell

```powershell
# Step 1: Stop the failing service
docker compose down

# Step 2: Checkout the last known stable commit or tag
git checkout v1.0.0

# Step 3: Rebuild and restart the container in detached mode
docker compose up -d --build

# Step 4: Verify container status and health
docker compose ps
```

#### Linux / Bash

```bash
# Step 1: Stop the failing service
docker compose down

# Step 2: Checkout stable tag
git checkout v1.0.0

# Step 3: Rebuild and start
docker compose up -d --build

# Step 4: Verify status
docker compose ps
```

---

### Strategy B: Rollback Using Standalone Docker CLI

If running standalone Docker containers, roll back to the previously tagged image (`knowrag:stable` or specific Git commit SHA tag):

#### Windows PowerShell

```powershell
# Step 1: Stop and remove the faulty container
docker stop knowrag-service
docker rm knowrag-service

# Step 2: Relaunch using the previous stable image tag
docker run -d `
  --name knowrag-service `
  -p 8000:8000 `
  -p 8501:8501 `
  -e GROQ_API_KEY="$env:GROQ_API_KEY" `
  -v "${PWD}/chroma_db:/app/chroma_db" `
  -v "${PWD}/data:/app/data" `
  knowrag:stable

# Step 3: Wait 5 seconds and test health
Start-Sleep -Seconds 5
curl.exe -i http://localhost:8000/health
```

#### Linux / Bash

```bash
# Step 1: Stop and remove container
docker stop knowrag-service
docker rm knowrag-service

# Step 2: Relaunch with stable image
docker run -d \
  --name knowrag-service \
  -p 8000:8000 \
  -p 8501:8501 \
  -e GROQ_API_KEY="${GROQ_API_KEY}" \
  -v "$(pwd)/chroma_db:/app/chroma_db" \
  -v "$(pwd)/data:/app/data" \
  knowrag:stable

# Step 3: Verify health
sleep 5
curl -i http://localhost:8000/health
```

---

## 4. Git Version Control Rollback

When a deployment failure is caused by an erroneous code commit, revert the code using Git:

### Option 1: Non-Destructive Revert (Recommended for shared branches)

Creates an inverse commit that undoes changes while preserving commit history:

```powershell
# Revert the most recent commit on main
git revert HEAD --no-edit

# Or revert a specific faulty commit SHA
git revert <faulty-commit-sha> --no-edit
```

### Option 2: Checkout Previous Stable Tag

Safely switch execution to an immutable release tag:

```powershell
# Fetch all remote tags
git fetch --tags

# Switch to stable release tag v1.0.0
git checkout tags/v1.0.0 -b hotfix-rollback
```

### Option 3: Hard Reset (Local Recovery Only)

> [!CAUTION]
> Only use `git reset --hard` if changes have **not** been pushed to remote or if you are resetting a dedicated staging server:

```powershell
# Reset local branch to the previous commit
git reset --hard HEAD~1
```

---

## 5. Vector Store & Database Recovery (ChromaDB)

KnowRAG persists vector embeddings in `./chroma_db/`. If the database becomes corrupted or inconsistent during an ingestion incident, follow this recovery workflow:

### Step 1: Automated Backup Creation (Scheduled / Pre-Deploy)

Run before any major migration or ingestion batch:

```powershell
# Windows PowerShell
$backupName = "chroma_db_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path ".\chroma_db" -Destination ".\$backupName" -Recurse
Write-Host "Created ChromaDB backup at: $backupName"
```

### Step 2: Restoring from Snapshot

```powershell
# Stop services
docker compose down

# Replace damaged collection with backup
Remove-Item -Path ".\chroma_db" -Recurse -Force
Copy-Item -Path ".\chroma_db_backup_<timestamp>" -Destination ".\chroma_db" -Recurse

# Restart service
docker compose up -d
```

### Step 3: Fresh Index Rebuild (Cold Recovery)

If no snapshot exists, KnowRAG can deterministically rebuild its vector store from baseline documents:

```powershell
# 1. Clear corrupted vector store
Remove-Item -Path ".\chroma_db" -Recurse -Force

# 2. Run application to trigger automatic re-indexing of data/*.txt and data/pdfs/*
.\.venv\Scripts\python.exe run.py --api-only
```

---

## 6. Post-Rollback Verification Gate

After executing a rollback, verify operational health before returning the system to active status:

| # | Check | Verification Command | Expected Output |
| :-: | :--- | :--- | :--- |
| **1** | **Container State** | `docker ps --filter "name=knowrag-service"` | `Up ... (healthy)` |
| **2** | **HTTP /health Probe** | `curl.exe -i http://localhost:8000/health` | `HTTP/1.1 200 OK` + `{"status":"ok"}` |
| **3** | **Service Discovery** | `curl.exe -i http://localhost:8000/` | `HTTP/1.1 200 OK` + `service: KnowRAG` |
| **4** | **RAG Inference** | PowerShell `Invoke-RestMethod` to `/ask` | Valid JSON answer with source citations |
| **5** | **Streamlit UI** | `curl.exe -i http://localhost:8501/healthz` | `HTTP/1.1 200 OK` |
| **6** | **Automated Tests** | `pytest tests/test_part4_smoke.py -v` | `7 passed (100%)` |

### One-Click PowerShell Verification Snippet

```powershell
Write-Host "Verifying Rollback..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
if ($health.status -eq "ok") {
    Write-Host "[SUCCESS] Service rolled back and healthy!" -ForegroundColor Green
} else {
    Write-Host "[FAILURE] Health check returned: $($health | ConvertTo-Json)" -ForegroundColor Red
}
```

---

## 7. Incident Escalation & Post-Mortem Checklist

Following a successful rollback:

1. **Log Collection**: Save container logs (`docker logs knowrag-service > incident_log.txt`).
2. **Issue Tracking**: Create a GitHub issue on [https://github.com/Sairamya07/RAG-Ops/issues](https://github.com/Sairamya07/RAG-Ops/issues) documenting the error stack and trigger condition.
3. **Environment Audit**: Ensure `.env` was not accidentally wiped or overwritten with invalid keys.
4. **Tagging Update**: Mark any faulty releases in GitHub as deprecated or delete bad pre-release tags.
