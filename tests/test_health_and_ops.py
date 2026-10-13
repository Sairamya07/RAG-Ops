"""
KnowRAG — Automated Test Suite for RAG-Ops Part 1
--------------------------------------------------
Automated validation suite verifying all Part 1 requirements:
1. Working GET /health endpoint returning HTTP 200 and {"status": "ok"}
2. Root GET / endpoint returns HTTP 200 and {"status": "ok"}
3. Safe .env.example template exists, is documented, and has zero exposed secrets
4. Comprehensive .gitignore rules protecting secrets, virtualenvs, vector databases, and caches
5. Pinned dependencies in requirements.txt (using ==) including FastAPI and Uvicorn
6. Single startup runner (run.py) integrity and help execution
"""

import os
import re
import subprocess
import sys
from pathlib import Path

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

from fastapi.testclient import TestClient
from health_api import app as health_fastapi_app


def test_health_endpoint_testclient() -> None:
    """Test 1: FastAPI TestClient GET /health returns HTTP 200 and {"status": "ok"}."""
    client = TestClient(health_fastapi_app)
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {data}"


def test_root_endpoint() -> None:
    """Test 2: Root endpoint GET / returns HTTP 200."""
    client = TestClient(health_fastapi_app)
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "ok", f"Expected status: ok, got {data}"


def test_env_example_safety() -> None:
    """Test 3: .env.example exists, defines required variables, and leaks NO real secrets."""
    env_example_path = PROJECT_ROOT / ".env.example"
    assert env_example_path.exists(), ".env.example does not exist"

    content = env_example_path.read_text(encoding="utf-8")
    assert "GROQ_API_KEY" in content, "GROQ_API_KEY missing from .env.example"
    assert "GROQ_MODEL" in content, "GROQ_MODEL missing from .env.example"

    # Verify no real secret patterns are committed
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("GROQ_API_KEY="):
            val = line.split("=", 1)[1].strip()
            assert val in [
                "your_groq_api_key_here",
                "your_actual_groq_api_key_here",
                "gsk_your_groq_api_key_here",
            ], f"Potential real key leaked in .env.example: {val}"


def test_gitignore_rules() -> None:
    """Test 4: .gitignore properly protects sensitive files and vector databases."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore does not exist"

    content = gitignore_path.read_text(encoding="utf-8")
    rules = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

    required_patterns = [".env", "chroma_db/", ".venv/"]
    for pat in required_patterns:
        assert any(pat in rule for rule in rules), f"Missing gitignore rule for {pat}"

    # Verify .env.example is whitelisted or not ignored
    assert "!.env.example" in rules or "!.env.example" in content, "!.env.example whitelist missing in .gitignore"


def test_requirements_pinned() -> None:
    """Test 5: requirements.txt exists and all dependencies are pinned (==)."""
    req_path = PROJECT_ROOT / "requirements.txt"
    assert req_path.exists(), "requirements.txt does not exist"

    content = req_path.read_text(encoding="utf-8")
    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert len(lines) > 0, "requirements.txt has no dependencies"

    # Check for core dependencies
    expected_pkgs = [
        "streamlit",
        "chromadb",
        "sentence-transformers",
        "python-dotenv",
        "llama-index-core",
        "fastapi",
        "uvicorn",
        "pytest",
    ]

    for pkg in expected_pkgs:
        matching = [l for l in lines if l.lower().startswith(pkg.lower() + "==")]
        assert len(matching) > 0, f"Package {pkg} is not pinned with == in requirements.txt"

    # Ensure no unpinned (>=, <=, >) dependencies exist
    for line in lines:
        assert "==" in line, f"Dependency line not strictly pinned with '==': {line}"
        assert ">=" not in line, f"Dependency line contains '>=' instead of pinned '==': {line}"


def test_run_script_integrity() -> None:
    """Test 6: Single startup runner run.py exists and can execute --help."""
    run_script = PROJECT_ROOT / "run.py"
    assert run_script.exists(), "run.py startup runner does not exist"

    res = subprocess.run(
        [sys.executable, str(run_script), "--help"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert res.returncode == 0, f"run.py --help failed with code {res.returncode}: {res.stderr}"
    assert "KnowRAG" in res.stdout or "usage" in res.stdout.lower(), "run.py help text missing expected content"



def run_all_health_and_ops_tests() -> bool:
    """Run all Part 1 tests and print summary."""
    print("=" * 65)
    print("Starting KnowRAG — RAG-Ops Part 1 Automated Verification Suite")
    print("=" * 65)

    tests = [
        ("TEST 1: GET /health Returns HTTP 200 & {'status':'ok'}", test_health_endpoint_testclient),
        ("TEST 2: GET / Root Service Discovery Endpoint", test_root_endpoint),
        ("TEST 3: Safe .env.example Template & Secret Sanitization", test_env_example_safety),
        ("TEST 4: Repository .gitignore Security & Persistence Rules", test_gitignore_rules),
        ("TEST 5: Pinned Dependencies in requirements.txt", test_requirements_pinned),
        ("TEST 6: Single Startup Runner (run.py) Command Integrity", test_run_script_integrity),
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
    print(f"RAG-Ops Part 1 Test Summary: {passed}/{len(tests)} PASS ({(passed / len(tests)) * 100:.0f}%)")
    print("=" * 65)

    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_health_and_ops_tests()
    sys.exit(0 if success else 1)
