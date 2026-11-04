"""Verifies the bounded-queue worker against the handbook's own
acceptance checks: no duplicate index entries, transient failures retry
successfully, and exhausted retries get quarantined rather than crashing
the whole batch.

See: ../../../interview/interview-01/13-python-sql-coding-round.md (C10)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bounded_worker import run_with_bounded_queue, run_with_semaphore_only  # noqa: E402


@pytest.mark.asyncio
async def test_every_document_is_embedded_exactly_once():
    doc_ids = list(range(20))
    results, quarantined = await run_with_bounded_queue(doc_ids, concurrency=4, queue_maxsize=5)
    assert set(results.keys()) == set(doc_ids)
    assert quarantined == []


@pytest.mark.asyncio
async def test_transient_failure_succeeds_on_retry():
    doc_ids = [1, 2, 3]
    results, quarantined = await run_with_bounded_queue(
        doc_ids, concurrency=2, queue_maxsize=5, fail_once_ids={2}, max_retries=2
    )
    assert 2 in results  # retried and succeeded, never quarantined
    assert quarantined == []


@pytest.mark.asyncio
async def test_a_permanently_failing_document_gets_quarantined_not_crashed():
    # fail_once_ids is consumed on the FIRST failure per id (embed_document
    # discards it from the set), so to simulate a permanent failure we
    # pass max_retries=0 — any failure is immediately exhausted.
    doc_ids = [1, 2, 3]
    results, quarantined = await run_with_bounded_queue(
        doc_ids, concurrency=2, queue_maxsize=5, fail_once_ids={2}, max_retries=0
    )
    assert quarantined == [2]
    assert set(results.keys()) == {1, 3}  # the rest of the batch still completes


@pytest.mark.asyncio
async def test_semaphore_only_pattern_still_produces_correct_results():
    # Confirms the anti-pattern is functionally correct (it IS an
    # anti-pattern for memory behavior at scale, not for correctness at
    # this small size) -- this is why the bug is subtle and easy to miss
    # in a code review on a small test case.
    doc_ids = list(range(10))
    results = await run_with_semaphore_only(doc_ids, concurrency=3)
    assert set(results.keys()) == set(doc_ids)
