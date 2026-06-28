import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient) -> None:
    """Every response includes an X-Request-ID header."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


@pytest.mark.asyncio
async def test_request_id_propagation(client: AsyncClient) -> None:
    """Provided X-Request-ID is propagated in the response."""
    custom_id = "test-request-id-12345"
    response = await client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_not_found_envelope(client: AsyncClient) -> None:
    """404 errors return the standard response envelope."""
    response = await client.get("/nonexistent-route")
    assert response.status_code == 404
