"""
KnowRAG — RAG-Ops Part 2 Automated Test Suite
----------------------------------------------
Offline pytest test suite verifying Part 2 requirements:
1. Text Chunking (splitting documents into nodes preserving metadata)
2. Top-K Retrieval (semantic retrieval with mocked vector index and retriever)
3. GET /health Endpoint (returns HTTP 200 and {"status": "ok"})
4. Question API JSON Structure (validates response schema and keys)
5. Empty-Question Handling (validation, error codes, and graceful fallback)
6. Offline RAG Pipeline (mocked Groq LLM & index execution)

All tests run 100% offline with zero external network calls or paid API keys.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from llama_index.core.schema import Document, NodeWithScore, TextNode

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from health_api import app
from src.chunking import CHUNK_OVERLAP, CHUNK_SIZE, create_chunks
from src.conversation import process_user_query
from src.rag_pipeline import ask_question, format_context_string
from src.retrieval import retrieve_documents


@pytest.fixture
def client():
    """FastAPI TestClient fixture for offline API tests."""
    return TestClient(app)


# ==============================================================================
# 1. Text Chunking Tests
# ==============================================================================
def test_text_chunking_splits_document_and_preserves_metadata():
    """
    Verify text chunking splits a long document into multiple chunk nodes
    while preserving document metadata (e.g. file_name, category).
    """
    # Sample text with multiple sentences to trigger chunk splitting
    paragraph = (
        "TechNova University provides comprehensive academic programs in engineering, "
        "computing, and natural sciences. Students engage in theoretical learning, "
        "hands-on laboratory sessions, and industry-sponsored projects. "
        "The curriculum is designed in collaboration with leading technology companies. "
    )
    long_text = paragraph * 15  # Sufficient tokens to exceed chunk_size 100

    test_doc = Document(
        text=long_text,
        metadata={"file_name": "academic_guide.txt", "department": "Engineering"},
    )

    # Use smaller chunk_size to verify deterministic splitting
    chunks = create_chunks([test_doc], chunk_size=80, chunk_overlap=20)

    assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"

    for i, node in enumerate(chunks):
        assert isinstance(node, TextNode) or hasattr(node, "text")
        assert len(node.text.strip()) > 0, f"Chunk {i} text should not be empty"
        assert node.metadata.get("file_name") == "academic_guide.txt"
        assert node.metadata.get("department") == "Engineering"


def test_text_chunking_preserves_single_short_document():
    """
    Verify that a short document fitting within chunk_size produces exactly one node.
    """
    short_text = "TechNova Central Library is open 24/7 during final exam weeks."
    doc = Document(
        text=short_text,
        metadata={"file_name": "library_hours.txt", "page_number": 1},
    )

    chunks = create_chunks([doc], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    assert len(chunks) == 1
    assert chunks[0].text.strip() == short_text
    assert chunks[0].metadata["file_name"] == "library_hours.txt"
    assert chunks[0].metadata["page_number"] == 1


# ==============================================================================
# 2. Top-K Retrieval Tests (Mocked Offline)
# ==============================================================================
def test_top_k_retrieval_returns_correct_k_nodes():
    """
    Verify retrieve_documents correctly configures the retriever with top_k
    and returns the expected number of NodeWithScore objects offline.
    """
    mock_index = MagicMock()
    mock_retriever = MagicMock()
    mock_index.as_retriever.return_value = mock_retriever

    k = 3
    fake_nodes = [
        NodeWithScore(
            node=TextNode(text=f"Retrieved chunk text {i}", metadata={"file_name": f"doc_{i}.txt"}),
            score=0.95 - (i * 0.1),
        )
        for i in range(k)
    ]
    mock_retriever.retrieve.return_value = fake_nodes

    query = "What are the campus library policies?"
    results = retrieve_documents(query=query, top_k=k, index=mock_index)

    mock_index.as_retriever.assert_called_once_with(similarity_top_k=k)
    mock_retriever.retrieve.assert_called_once_with(query)

    assert len(results) == k
    assert results[0].node.text == "Retrieved chunk text 0"
    assert results[0].score == 0.95
    assert results[1].node.metadata["file_name"] == "doc_1.txt"


def test_top_k_retrieval_respects_custom_k_parameter():
    """
    Verify top-k parameter flexibility (e.g. top_k=1 and top_k=5).
    """
    for custom_k in [1, 5]:
        mock_index = MagicMock()
        mock_retriever = MagicMock()
        mock_index.as_retriever.return_value = mock_retriever
        mock_retriever.retrieve.return_value = [
            NodeWithScore(node=TextNode(text=f"Node {i}"), score=0.8)
            for i in range(custom_k)
        ]

        results = retrieve_documents(query="Test query", top_k=custom_k, index=mock_index)
        mock_index.as_retriever.assert_called_once_with(similarity_top_k=custom_k)
        assert len(results) == custom_k


# ==============================================================================
# 3. GET /health Endpoint Tests
# ==============================================================================
def test_get_health_endpoint_returns_200_and_ok(client):
    """
    Verify GET /health returns HTTP 200 and exact JSON {"status": "ok"}.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"status": "ok"}


def test_get_root_endpoint_returns_200_and_status(client):
    """
    Verify GET / root discovery endpoint returns HTTP 200 and status ok.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "service" in data


# ==============================================================================
# 4. Question API JSON Structure Tests (Mocked Offline)
# ==============================================================================
def test_question_api_json_structure(client):
    """
    Verify POST /ask endpoint returns the correct JSON structure:
    question, answer, sources, source_details, intent, and status.
    """
    mock_response = {
        "question": "What academic programs are offered?",
        "answer": "TechNova offers B.Tech and M.Tech in Computer Science.",
        "sources": ["academic_programs.txt"],
        "source_details": ["academic_programs.txt — Page 1"],
        "intent": "rag",
    }

    with patch("src.conversation.process_user_query", return_value=mock_response) as mock_query:
        payload = {"question": "What academic programs are offered?", "top_k": 3}
        response = client.post("/ask", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check required schema keys
        expected_keys = {"question", "answer", "sources", "source_details", "intent", "status"}
        assert expected_keys.issubset(set(data.keys())), f"Missing keys in response: {data}"

        assert data["status"] == "ok"
        assert data["question"] == "What academic programs are offered?"
        assert data["answer"] == "TechNova offers B.Tech and M.Tech in Computer Science."
        assert isinstance(data["sources"], list)
        assert "academic_programs.txt" in data["sources"]
        assert isinstance(data["source_details"], list)
        assert data["intent"] == "rag"

        mock_query.assert_called_once_with("What academic programs are offered?", top_k=3)


def test_question_api_aliases_return_consistent_structure(client):
    """
    Verify route aliases /question and /query adhere to the same schema.
    """
    mock_response = {
        "question": "What is TechNova?",
        "answer": "TechNova is a premier research university.",
        "sources": ["university_overview.txt"],
        "source_details": ["university_overview.txt"],
        "intent": "rag",
    }

    with patch("src.conversation.process_user_query", return_value=mock_response):
        for alias in ["/question", "/query"]:
            response = client.post(alias, json={"question": "What is TechNova?"})
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["answer"] == "TechNova is a premier research university."
            assert data["sources"] == ["university_overview.txt"]


# ==============================================================================
# 5. Empty-Question Handling Tests
# ==============================================================================
def test_empty_question_handling_empty_string(client):
    """
    Verify POST /ask returns HTTP 400 when an empty question string is sent.
    """
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "empty" in data["detail"].lower()


def test_empty_question_handling_whitespace_only(client):
    """
    Verify POST /ask returns HTTP 400 when whitespace-only question is sent.
    """
    response = client.post("/ask", json={"question": "     \n\t  "})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "empty" in data["detail"].lower()


def test_empty_question_handling_missing_payload(client):
    """
    Verify POST /ask returns HTTP 400 or 422 when question field is missing.
    """
    response = client.post("/ask", json={})
    assert response.status_code in [400, 422]


def test_empty_question_handling_conversation_module():
    """
    Verify process_user_query returns graceful empty guidance when passed an empty string.
    """
    result = process_user_query("")
    assert result["intent"] == "empty"
    assert len(result["sources"]) == 0
    assert len(result["source_details"]) == 0
    assert "please enter a question" in result["answer"].lower()

    # Also test whitespace
    result_ws = process_user_query("   ")
    assert result_ws["intent"] == "empty"


# ==============================================================================
# 6. End-to-End RAG Pipeline Execution with Mocked LLM (Offline)
# ==============================================================================
def test_rag_pipeline_offline_with_mocked_llm():
    """
    Verify ask_question correctly formats context and parses source attribution
    using a mocked LLM and mocked index without hitting any external API.
    """
    mock_llm = MagicMock()
    # Mock LLM generation response containing strict source attribution format
    fake_completion = MagicMock()
    fake_completion.text = (
        "Students must carry a valid university identity card on campus.\n"
        "SOURCES_USED: campus_rules.txt"
    )
    mock_llm.complete.return_value = fake_completion

    mock_index = MagicMock()
    mock_retriever = MagicMock()
    mock_index.as_retriever.return_value = mock_retriever
    mock_retriever.retrieve.return_value = [
        NodeWithScore(
            node=TextNode(
                text="Carry a valid ID card at all times on campus.",
                metadata={"file_name": "campus_rules.txt", "page_number": 1},
            ),
            score=0.92,
        )
    ]

    result = ask_question(
        question="What are the ID card campus rules?",
        top_k=1,
        index=mock_index,
        llm=mock_llm,
    )

    assert result["question"] == "What are the ID card campus rules?"
    assert "Students must carry a valid university identity card" in result["answer"]
    assert "campus_rules.txt" in result["sources"]
    assert len(result["source_details"]) > 0
    assert "campus_rules.txt — Page 1" in result["source_details"][0]
    assert len(result["retrieved_context"]) == 1
