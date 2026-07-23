from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import admin, ticket, user

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

app.include_router(
    ticket.router
)

app.include_router(
    admin.router
)
