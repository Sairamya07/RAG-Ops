# ==============================================================================
# KnowRAG — Docker Containerization Specification
# Multi-Service RAG-Ops Container (FastAPI Health/API + Streamlit Web UI)
# ==============================================================================

# Base image: Official Python 3.11 slim variant for security & reduced attack surface
FROM python:3.11-slim

# Container metadata
LABEL maintainer="KnowRAG Engineering" \
      description="KnowRAG AI Knowledge Assistant & RAG-Ops Service" \
      version="1.0.0"

# Python runtime configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    STREAMLIT_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install minimal OS dependencies required for runtime & health checking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set standard working directory
WORKDIR /app

# Create a dedicated non-root application user for container security
RUN useradd -m -u 1000 appuser

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install pinned Python dependencies
# Pre-install CPU variant of PyTorch to prevent downloading 6GB+ CUDA binaries in container
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy project application source files with proper permissions directly
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose FastAPI Health/API (8000) and Streamlit Web UI (8501)
EXPOSE 8000 8501

# Health check instruction targeting the RAG-Ops /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default startup orchestrator running both FastAPI and Streamlit
CMD ["python", "run.py"]
