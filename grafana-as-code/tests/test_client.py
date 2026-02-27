"""
Tests for Grafana Client
"""

import pytest
from unittest.mock import Mock, patch
from src.client import GrafanaClient


@pytest.fixture
def client():
    """Create a test client"""
    return GrafanaClient(
        url="http://localhost:3000",
        api_key="test-key"
    )


def test_client_init():
    """Test client initialization"""
    client = GrafanaClient(
        url="http://test.com",
        api_key="test-key"
    )

    assert client.url == "http://test.com"
    assert client.api_key == "test-key"
    assert client.headers == {"Authorization": "Bearer test-key"}


def test_client_init_with_env(monkeypatch):
    """Test client initialization with environment variables"""
    monkeypatch.setenv("GRAFANA_URL", "http://env.com")
    monkeypatch.setenv("GRAFANA_API_KEY", "env-key")

    client = GrafanaClient()
    assert client.url == "http://env.com"
    assert client.api_key == "env-key"


@patch('src.client.requests.request')
def test_get_request(mock_request, client):
    """Test GET request"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_response

    result = client.get("/test")

    mock_request.assert_called_once()
    assert result == {"status": "ok"}


@patch('src.client.requests.request')
def test_post_request(mock_request, client):
    """Test POST request"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1}
    mock_request.return_value = mock_response

    result = client.post("/test", {"name": "test"})

    mock_request.assert_called_once()
    assert result == {"id": 1}


@patch('src.client.requests.request')
def test_list_dashboards(mock_request, client):
    """Test listing dashboards"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"title": "Dashboard 1", "uid": "abc123"},
        {"title": "Dashboard 2", "uid": "def456"}
    ]
    mock_request.return_value = mock_response

    dashboards = client.list_dashboards()

    assert len(dashboards) == 2
    assert dashboards[0]["title"] == "Dashboard 1"


@patch('src.client.requests.request')
def test_health_check(mock_request, client):
    """Test health check"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"database": "ok"}
    mock_request.return_value = mock_response

    health = client.health()

    assert health["database"] == "ok"
