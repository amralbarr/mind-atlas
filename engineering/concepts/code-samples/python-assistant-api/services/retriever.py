"""A real Retriever implementation calling an external search endpoint over
a shared, pooled httpx client.

This is illustrative, not production-ready: it demonstrates the shape a
real implementation of the Retriever protocol takes, wired through the
shared connection pool created in main.py's lifespan. Point
SEARCH_BASE_URL at a real hybrid-search service to make it functional.

See: ../../../concepts/ai/retrieval/hybrid-search.md
"""
import os

import httpx

SEARCH_BASE_URL = os.environ.get("SEARCH_BASE_URL", "http://localhost:9200")


class SearchRetriever:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def search(self, query: str, allowed_groups: list[str], k: int) -> list[dict]:
        response = await self._http.post(
            f"{SEARCH_BASE_URL}/search",
            json={"query": query, "allowed_groups": allowed_groups, "k": k},
        )
        response.raise_for_status()
        return response.json()["results"]
