import pytest
from httpx import ASGITransport, AsyncClient

from tsubo_api.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_openapi_available():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"].endswith("API")
    assert "/api/v1/listings" in payload["paths"]
