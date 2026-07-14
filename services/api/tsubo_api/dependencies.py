from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.config import Settings, get_settings
from tsubo_api.database import get_db
from tsubo_api.services.fx import FXService
from tsubo_api.services.search import SearchService


async def get_settings_dep() -> Settings:
    return get_settings()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


def get_fx_service() -> FXService:
    return FXService(get_settings())


def get_search_service() -> SearchService:
    return SearchService(get_settings())
