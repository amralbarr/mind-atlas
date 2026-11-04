"""Interfaces (Protocols) the pipeline depends on, instead of a concrete
vector store or model provider.

See: ../../../concepts/programming/fundamentals/dependency-injection.md
"""
from typing import Protocol


class Retriever(Protocol):
    async def search(self, query: str, allowed_groups: list[str], k: int) -> list[dict]: ...


class LLMClient(Protocol):
    async def generate(self, question: str, chunks: list[dict]) -> dict: ...
