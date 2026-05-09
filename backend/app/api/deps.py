# deps — FastAPI dependency injection: DB session, settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import getSettings

settings = getSettings()
_connectArgs = {"check_same_thread": False} if settings.use_sqlite else {}
_engine = create_async_engine(
    settings.databaseUrl, echo=False,
    pool_pre_ping=not settings.use_sqlite,
    connect_args=_connectArgs,
)
_AsyncSessionLocal = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


async def getDbSession():
    async with _AsyncSessionLocal() as session:
        yield session
