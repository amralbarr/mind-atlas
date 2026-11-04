"""App creation and connection lifecycle: one shared, pooled httpx client
created once at startup and closed cleanly at shutdown, instead of opening
a fresh connection on every request.

See:
- ../../concepts/databases/relational/connection-pooling.md
- ../../interview/interview-01/20-python-assistant-api-deep-dive.md
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from api.routes import router
from pipeline import AssistantPipeline
from services.llm import AzureLLMClient
from services.retriever import SearchRetriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: create clients once.
    http = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=5.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    app.state.pipeline = AssistantPipeline(
        retriever=SearchRetriever(http),
        llm=AzureLLMClient(http),
    )
    app.state.http = http
    yield
    # On shutdown: close connections cleanly.
    await http.aclose()


app = FastAPI(lifespan=lifespan, title="Assistant API")
app.include_router(router)
