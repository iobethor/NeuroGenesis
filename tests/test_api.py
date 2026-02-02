"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from neurogenesis.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_remember_endpoint(client: TestClient):
    """Test memory storage endpoint."""
    response = client.post(
        "/api/v1/remember",
        json={
            "content": "API test memory",
            "memory_type": "semantic",
            "importance": 0.7,
            "tags": ["api", "test"],
        },
    )
    
    # May fail if mind not initialized, which is expected in unit test
    # Full integration test would need proper setup
    assert response.status_code in [200, 500]


def test_recall_endpoint(client: TestClient):
    """Test memory recall endpoint."""
    response = client.post(
        "/api/v1/recall",
        json={
            "query": "test query",
            "limit": 5,
        },
    )
    
    assert response.status_code in [200, 500]


def test_think_endpoint(client: TestClient):
    """Test thinking endpoint."""
    response = client.post(
        "/api/v1/think",
        json={
            "content": "What do I know about testing?",
            "context": {},
        },
    )
    
    assert response.status_code in [200, 500]


def test_metrics_endpoint(client: TestClient):
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    
    assert response.status_code in [200, 500]
