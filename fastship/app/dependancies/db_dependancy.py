from app.database.db_session import get_db_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
