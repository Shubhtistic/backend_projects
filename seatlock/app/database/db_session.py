from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import database_settings

async_engine = create_async_engine(database_settings.get_db_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
