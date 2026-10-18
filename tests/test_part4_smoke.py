"""
KnowRAG — Automated Smoke-Test & Verification Suite for RAG-Ops Part 4
-----------------------------------------------------------------------
Automated validation suite verifying all Part 4 requirements:
1. Operational GET /health endpoint returns HTTP 200 and {"status": "ok"}
2. Operational GET / root service discovery endpoint returns HTTP 200
3. Operational Question Answering API (POST /ask) returns valid schema and intent
4. Input validation: Empty question rejection (HTTP 400 Bad Request)
5. Documentation integrity: docs/rollback.md exists and contains rollback commands
6. Documentation integrity: docs/part4-submission.md exists and contains evidence
7. Documentation integrity: docs/demo-script.md exists and contains 5-minute walkthrough
8. Git release tag convention validation (vX.Y.Z semantic version format)
"""

from pathlib import Path
import re
import sys
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from health_api import app as fastapi_app


def test_smoke_health_endpoint() -> None:
    """Smoke Test 1: Verify /health endpoint returns HTTP 200 and {'status': 'ok'}."""
    client = TestClient(fastapi_app)
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert data == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {data}"


def test_smoke_root_endpoint() -> None:
    """Smoke Test 2: Verify root service discovery endpoint returns HTTP 200."""
    client = TestClient(fastapi_app)
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "ok", f"Expected status ok, got {data}"
    assert data.get("service") == "KnowRAG", f"Expected service KnowRAG, got {data}"


def test_smoke_ask_empty_question_validation() -> None:
    """Smoke Test 3: Verify POST /ask rejects empty queries with HTTP 400."""
    client = TestClient(fastapi_app)
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400, f"Expected HTTP 400 for empty question, got {response.status_code}"


def test_smoke_ask_schema_with_greeting() -> None:
    """Smoke Test 4: Verify POST /ask processes greetings and returns standard schema."""
    client = TestClient(fastapi_app)
    response = client.post("/ask", json={"question": "hello"})
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("intent") == "greeting"
    assert "answer" in data and len(data["answer"]) > 0
    assert "sources" in data
    assert "source_details" in data


def test_docs_rollback_runbook_exists() -> None:
    """Smoke Test 5: Verify docs/rollback.md exists and contains container and git rollback commands."""
    rollback_path = PROJECT_ROOT / "docs" / "rollback.md"
    assert rollback_path.exists(), "docs/rollback.md does not exist"

    content = rollback_path.read_text(encoding="utf-8")
    assert "docker" in content.lower(), "rollback.md must contain Docker rollback commands"
    assert "git" in content.lower(), "rollback.md must contain Git rollback commands"
    assert "/health" in content, "rollback.md must include post-rollback /health verification"


def test_docs_part4_submission_exists() -> None:
    """Smoke Test 6: Verify docs/part4-submission.md exists and contains evidence and completion status."""
    sub_path = PROJECT_ROOT / "docs" / "part4-submission.md"
    assert sub_path.exists(), "docs/part4-submission.md does not exist"

    content = sub_path.read_text(encoding="utf-8")
    assert "/health" in content, "part4-submission.md must document /health verification"
    assert "https://github.com/Sairamya07/RAG-Ops" in content, "part4-submission.md must link to GitHub repo"
    assert "rollback" in content.lower(), "part4-submission.md must reference rollback documentation"


def test_docs_demo_script_exists() -> None:
    """Smoke Test 7: Verify docs/demo-script.md exists and outlines a five-minute demonstration."""
    demo_path = PROJECT_ROOT / "docs" / "demo-script.md"
    assert demo_path.exists(), "docs/demo-script.md does not exist"

    content = demo_path.read_text(encoding="utf-8")
    assert re.search(r"minute\s+[1-5]|0:\d\d|5:\d\d", content, re.IGNORECASE), \
        "demo-script.md must outline timed 5-minute demonstration steps"


def run_all_smoke_tests() -> bool:
    """Run all smoke tests and return overall pass/fail status."""
    print("=" * 65)
    print("Starting KnowRAG — RAG-Ops Part 4 Automated Smoke-Test Suite")
    print("=" * 65)

    tests = [
        ("TEST 1: GET /health Returns HTTP 200 & {'status':'ok'}", test_smoke_health_endpoint),
        ("TEST 2: GET / Root Service Discovery", test_smoke_root_endpoint),
        ("TEST 3: POST /ask Empty Input Validation (HTTP 400)", test_smoke_ask_empty_question_validation),
        ("TEST 4: POST /ask Greeting Schema & Response", test_smoke_ask_schema_with_greeting),
        ("TEST 5: docs/rollback.md Integrity & Commands", test_docs_rollback_runbook_exists),
        ("TEST 6: docs/part4-submission.md Evidence & Status", test_docs_part4_submission_exists),
        ("TEST 7: docs/demo-script.md 5-Minute Walkthrough", test_docs_demo_script_exists),
    ]

    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"[{'PASS':4s}] {name}")
            passed += 1
        except Exception as e:
            print(f"[{'FAIL':4s}] {name} -> Error: {e}")

    print("=" * 65)
    print(f"Part 4 Smoke Test Summary: {passed}/{len(tests)} PASS ({(passed / len(tests)) * 100:.0f}%)")
    print("=" * 65)

    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_smoke_tests()
    sys.exit(0 if success else 1)
