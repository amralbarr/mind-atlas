"""A real LLMClient implementation calling a model endpoint over a shared,
pooled httpx client.

Illustrative, not production-ready: demonstrates the shape a real
implementation of the LLMClient protocol takes. Point MODEL_BASE_URL at a
real Azure OpenAI / vLLM endpoint to make it functional.

See: ../../../concepts/ai/generation/llm.md
"""
import os

import httpx

MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL", "http://localhost:8000")


class AzureLLMClient:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def generate(self, question: str, chunks: list[dict]) -> dict:
        response = await self._http.post(
            f"{MODEL_BASE_URL}/generate",
            json={"question": question, "context": chunks},
        )
        response.raise_for_status()
        return response.json()
