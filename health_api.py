"""
KnowRAG — RAG-Ops Health & Monitoring API
------------------------------------------
FastAPI application providing health check, operational monitoring, and
question-answering endpoints for the KnowRAG knowledge assistant service.
"""

import os
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="KnowRAG RAG-Ops API",
    description="Operational health check, monitoring, and RAG query API for KnowRAG",
    version="1.0.0",
)

# Enable CORS for cross-origin monitoring and probe requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    """Request model for question answering API."""
    question: str = Field(default="", description="The query or question to answer")
    top_k: Optional[int] = Field(default=3, description="Number of top chunks to retrieve")


class QuestionResponse(BaseModel):
    """Response model for question answering API."""
    question: str
    answer: str
    sources: List[str] = []
    source_details: List[str] = []
    intent: Optional[str] = "rag"
    status: str = "ok"


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    """
    Health check endpoint returning HTTP 200 and {"status": "ok"}.
    Used for container liveness/readiness probes and automated uptime checks.
    """
    return {"status": "ok"}


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """Root endpoint for basic service discovery."""
    return {"status": "ok", "service": "KnowRAG"}


@app.post("/ask", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
@app.post("/question", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
@app.post("/query", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
def ask(request: QuestionRequest):
    """
    Question answering endpoint.
    Validates user input, catches empty questions, and routes to KnowRAG pipeline.
    """
    question_text = request.question.strip() if request.question else ""
    if not question_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty. Please provide a valid query.",
        )

    try:
        from src.conversation import process_user_query

        result = process_user_query(question_text, top_k=request.top_k or 3)
        return QuestionResponse(
            question=request.question,
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            source_details=result.get("source_details", []),
            intent=result.get("intent", "rag"),
            status="ok",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(exc)}",
        )


@app.get("/ask")
@app.get("/question")
def ask_get(question: str = "", top_k: int = 3):
    """GET convenience wrapper for question answering."""
    return ask(QuestionRequest(question=question, top_k=top_k))


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("health_api:app", host=host, port=port, reload=False)
