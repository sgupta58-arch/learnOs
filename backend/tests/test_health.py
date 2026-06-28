import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient) -> None:
    """Root liveness endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "alive"


@pytest.mark.asyncio
async def test_v1_health(client: AsyncClient) -> None:
    """V1 liveness endpoint returns 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    """Readiness endpoint returns connectivity status."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "database" in body["data"]
    assert "redis" in body["data"]
