from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.database.db_models import SQLModel
from app.database.db_session import engine
from contextlib import asynccontextmanager
from app.api_routes import shipment


@asynccontextmanager
async def lifespan():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(title="FastSHIP API", lifespan=lifespan)
app.include_router(shipment.router, tags=["Shipments"])


@app.get("/scalar")
def scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Fastship")
