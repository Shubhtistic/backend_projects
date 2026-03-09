from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.api_routes.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/index.html") as f:
        return f.read()


@app.get("/scalar")
async def scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url)
