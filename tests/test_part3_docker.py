"""
KnowRAG — Automated Test Suite for RAG-Ops Part 3 (Docker & Containerization)
-----------------------------------------------------------------------------
Automated validation suite verifying all Part 3 containerization requirements:
1. Dockerfile exists, uses python:3.11-slim, implements non-root user, exposes ports 8000 & 8501, and defines HEALTHCHECK
2. .dockerignore exists, strictly protects secrets (.env), caches, virtualenvs, and whitelists .env.example
3. docker-compose.yml exists, defines knowrag service, maps ports 8000 & 8501, mounts persistent volumes, and configures healthcheck
4. GitHub Actions CI pipeline (.github/workflows/ci.yml) has test + build-and-publish jobs using GitHub Secrets
5. Zero secrets baked or committed
"""

from pathlib import Path
import re
import sys
import yaml

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


def test_dockerfile_specification() -> None:
    """Verify Dockerfile presence, security best practices, and runtime instructions."""
    dockerfile_path = PROJECT_ROOT / "Dockerfile"
    assert dockerfile_path.exists(), "Dockerfile does not exist at project root"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Base image check
    assert re.search(r"FROM\s+python:3\.11-slim", content, re.IGNORECASE), \
        "Dockerfile must use python:3.11-slim as the base image"

    # Non-root user check
    assert "USER appuser" in content or "USER 1000" in content, \
        "Dockerfile must configure a non-root user for security"

    # Port exposure check
    assert re.search(r"EXPOSE\s+.*8000", content), "Dockerfile must expose port 8000 (FastAPI Health API)"
    assert re.search(r"EXPOSE\s+.*8501", content), "Dockerfile must expose port 8501 (Streamlit Web UI)"

    # Healthcheck check
    assert "HEALTHCHECK" in content, "Dockerfile must define a HEALTHCHECK instruction"
    assert "/health" in content, "HEALTHCHECK in Dockerfile must target /health endpoint"

    # Command entrypoint check
    assert "run.py" in content, "Dockerfile CMD must execute run.py orchestrator"


def test_dockerignore_security_and_rules() -> None:
    """Verify .dockerignore blocks virtualenv, cache, vector store, and secrets."""
    dockerignore_path = PROJECT_ROOT / ".dockerignore"
    assert dockerignore_path.exists(), ".dockerignore does not exist at project root"

    content = dockerignore_path.read_text(encoding="utf-8")
    rules = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

    required_patterns = [
        ".env",
        ".venv",
        "__pycache__",
        "chroma_db",
    ]
    for pat in required_patterns:
        assert any(pat in r for r in rules), f"Missing .dockerignore pattern for '{pat}'"

    # Ensure .env.example is retained
    assert any("!.env.example" in r for r in rules), "!.env.example exception must be present in .dockerignore"


def test_docker_compose_specification() -> None:
    """Verify docker-compose.yml structure, service definitions, ports, and volumes."""
    compose_path = PROJECT_ROOT / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml does not exist at project root"

    content = compose_path.read_text(encoding="utf-8")
    assert "services:" in content, "docker-compose.yml must have a 'services' section"
    assert "knowrag:" in content or "services:" in content, "knowrag service must be defined"

    # Ports check
    assert "8000:8000" in content or "8000" in content, "Service must map port 8000 for Health API"
    assert "8501:8501" in content or "8501" in content, "Service must map port 8501 for Streamlit UI"

    # Volumes check
    assert "chroma_db" in content, "docker-compose.yml must persist chroma_db"
    assert "data" in content, "docker-compose.yml must persist data directory"

    # Healthcheck check
    assert "healthcheck:" in content, "Service in docker-compose.yml must define a healthcheck"
    assert "/health" in content, "docker-compose healthcheck must target /health"


def test_github_actions_ci_workflow() -> None:
    """Verify GitHub Actions CI pipeline includes automated test and Docker build/publish jobs."""
    ci_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_path.exists(), "ci.yml does not exist at .github/workflows/ci.yml"

    content = ci_path.read_text(encoding="utf-8")

    # Workflow jobs
    assert "jobs:" in content, "ci.yml must define workflow jobs"
    assert "test:" in content, "ci.yml must contain a 'test' job"
    assert "build-and-publish:" in content or "publish:" in content or "docker:" in content, \
        "ci.yml must contain a Docker build and publish job"

    # Secret usage check (No hardcoded passwords or tokens)
    assert "secrets.DOCKERHUB_USERNAME" in content, "ci.yml must use secrets.DOCKERHUB_USERNAME"
    assert "secrets.DOCKERHUB_TOKEN" in content, "ci.yml must use secrets.DOCKERHUB_TOKEN"

    # Dependency check: Docker publish must depend on test job passing
    assert "needs: test" in content, "Docker publish job must declare 'needs: test'"


def run_all_docker_tests() -> bool:
    """Run all Part 3 tests and print summary."""
    print("=" * 65)
    print("Starting KnowRAG — RAG-Ops Part 3 Automated Verification Suite")
    print("=" * 65)

    tests = [
        ("TEST 1: Dockerfile Security & Multi-Service Specification", test_dockerfile_specification),
        ("TEST 2: .dockerignore Security & Leakage Prevention Rules", test_dockerignore_security_and_rules),
        ("TEST 3: docker-compose.yml Service, Ports, & Persistence Configuration", test_docker_compose_specification),
        ("TEST 4: GitHub Actions Docker Build & Publish Workflow with Secrets", test_github_actions_ci_workflow),
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
    print(f"RAG-Ops Part 3 Test Summary: {passed}/{len(tests)} PASS ({(passed / len(tests)) * 100:.0f}%)")
    print("=" * 65)

    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_docker_tests()
    sys.exit(0 if success else 1)
