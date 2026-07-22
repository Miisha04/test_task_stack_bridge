from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import user

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="stack_bridge_api",
    lifespan=lifespan,
)

app.include_router(
    user.router
)