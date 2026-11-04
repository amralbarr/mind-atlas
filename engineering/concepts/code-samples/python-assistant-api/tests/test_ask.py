"""Tests for AssistantPipeline — fast, free, and deterministic because
they run entirely against fakes, never a real search/model service.

See: ../../../interview/interview-01/20-python-assistant-api-deep-dive.md
"""
import pytest

from auth import User
from pipeline import AssistantPipeline
from schemas import AnswerStatus
from tests.fakes import FakeLLM, FakeRetriever

fake_user = User(request_id="req_test_1", groups=["hr"])


@pytest.mark.asyncio
async def test_abstains_when_no_relevant_chunks():
    pipeline = AssistantPipeline(
        retriever=FakeRetriever(results=[{"id": "x", "score": 0.40, "text": "..."}]),
        llm=FakeLLM(),
    )
    response = await pipeline.ask("What is the manager's salary?", fake_user)
    assert response.status == AnswerStatus.ABSTAINED
    assert response.reason == "no_relevant_documents"


@pytest.mark.asyncio
async def test_answers_with_evidence_when_grounded():
    chunk = {"id": "doc_42_chunk_3", "score": 0.91, "source": "hr_handbook.pdf", "page": 12}
    pipeline = AssistantPipeline(
        retriever=FakeRetriever(results=[chunk]),
        llm=FakeLLM(response={"answer": "30 days", "cited_ids": ["doc_42_chunk_3"]}),
    )
    response = await pipeline.ask("How many annual leave days?", fake_user)
    assert response.status == AnswerStatus.ANSWERED
    assert response.answer == "30 days"
    assert response.evidence[0].chunk_id == "doc_42_chunk_3"


@pytest.mark.asyncio
async def test_rejects_a_citation_that_was_never_retrieved():
    chunk = {"id": "doc_1_chunk_1", "score": 0.91, "source": "handbook.pdf", "page": 1}
    pipeline = AssistantPipeline(
        retriever=FakeRetriever(results=[chunk]),
        llm=FakeLLM(response={"answer": "fabricated", "cited_ids": ["doc_99_chunk_9"]}),
    )
    response = await pipeline.ask("Any question", fake_user)
    assert response.status == AnswerStatus.ERROR
    assert response.reason == "invalid_citation"
