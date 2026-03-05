"""Health check endpoint tests."""

from httpx import AsyncClient


async def test_health_check_returns_healthy(client: AsyncClient) -> None:
    """GET /api/v1/health returns healthy status."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "healthy"
    assert body["data"]["app"] == "DocuQuery"
    assert body["error"] is None
