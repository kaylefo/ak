import pytest
from httpx import ASGITransport, AsyncClient

from tsubo_api.config import Settings, get_settings
from tsubo_api.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://tsubo:tsubo@localhost:5432/tsubo_test",
        DATABASE_URL_SYNC="postgresql://tsubo:tsubo@localhost:5432/tsubo_test",
        OPENSEARCH_URL="http://localhost:9200",
        AUTH_SECRET="test-secret-with-enough-characters",
    )


@pytest.fixture
def app(test_settings: Settings):
    get_settings.cache_clear()
    app = create_app()
    yield app
    get_settings.cache_clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
