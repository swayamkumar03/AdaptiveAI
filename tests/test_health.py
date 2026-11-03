"""
tests/test_health.py
Basic smoke test — verifies the app starts and the health endpoint responds.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    """Swagger UI should be available in debug mode."""
    response = await client.get("/docs")
    assert response.status_code == 200
