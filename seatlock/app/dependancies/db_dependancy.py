# reusable db dependancy
from fastapi import Depends
from app.database.db_session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
