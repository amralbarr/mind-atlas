"""A real bounded-concurrency embedding batch worker, and a demonstration
of exactly the failure mode the handbook's "Follow-up" warns about: a
semaphore alone does NOT bound memory, because every task object still
gets created upfront before any of them acquire the semaphore.

Companion to:
- ../../interview/interview-01/13-python-sql-coding-round.md (C10)
- ../../concepts/backend/architecture/asyncio.md
- ../../concepts/distributed-systems/patterns/multi-threading.md
"""
import asyncio
import random


class TransientError(Exception):
    """Simulates a retriable failure — a timeout or rate limit, not a
    permanently invalid document."""


async def embed_document(doc_id: int, fail_once_ids: set[int]) -> tuple[int, list[float]]:
    """Stands in for a real embedding-model call. Documents in
    fail_once_ids raise TransientError on their first attempt only, to
    exercise the retry path."""
    await asyncio.sleep(0.01)
    if doc_id in fail_once_ids:
        fail_once_ids.discard(doc_id)  # succeeds on retry
        raise TransientError(f"transient failure embedding doc {doc_id}")
    return doc_id, [float(doc_id)] * 4  # a fake 4-dim vector


# --- The anti-pattern: a semaphore alone, with every task created upfront ---

async def run_with_semaphore_only(doc_ids: list[int], concurrency: int) -> dict:
    """ANTI-PATTERN, kept here to demonstrate the failure mode, not to
    recommend it: wrapping each call in a semaphore still requires
    creating one asyncio.Task per document BEFORE any of them actually
    runs — with millions of documents, that's millions of Task objects
    sitting in memory waiting for a semaphore slot, the exact problem
    the handbook's Follow-up question flags."""
    sem = asyncio.Semaphore(concurrency)

    async def bounded_call(doc_id):
        async with sem:
            return await embed_document(doc_id, set())

    tasks = [asyncio.ensure_future(bounded_call(doc_id)) for doc_id in doc_ids]
    # ^ every Task object already exists here, for ALL doc_ids, regardless
    #   of `concurrency` — this line is where "unbounded gather" lives.
    results = await asyncio.gather(*tasks)
    return dict(results)


# --- The real pattern: a bounded queue + a fixed worker pool ---

async def run_with_bounded_queue(
    doc_ids: list[int],
    concurrency: int,
    queue_maxsize: int,
    fail_once_ids: set[int] | None = None,
    max_retries: int = 2,
) -> tuple[dict, list[int]]:
    """A producer feeds doc_ids into a bounded asyncio.Queue; a fixed pool
    of `concurrency` workers pulls from it. Memory is bounded by
    `queue_maxsize` + `concurrency`, not by len(doc_ids) — the producer
    blocks on queue.put() once the queue is full, instead of creating
    every task upfront.

    Returns (results, quarantined) — quarantined holds doc_ids that
    exhausted their retries, per the handbook's "quarantine invalid
    inputs" requirement.
    """
    fail_once_ids = fail_once_ids or set()
    queue: asyncio.Queue = asyncio.Queue(maxsize=queue_maxsize)
    results: dict[int, list[float]] = {}
    quarantined: list[int] = []
    max_observed_queue_size = 0

    async def producer():
        for doc_id in doc_ids:
            await queue.put(doc_id)
        for _ in range(concurrency):
            await queue.put(None)  # sentinel: tells each worker to stop

    async def worker():
        nonlocal max_observed_queue_size
        while True:
            doc_id = await queue.get()
            max_observed_queue_size = max(max_observed_queue_size, queue.qsize())
            if doc_id is None:
                return
            for attempt in range(max_retries + 1):
                try:
                    returned_id, vector = await embed_document(doc_id, fail_once_ids)
                    results[returned_id] = vector
                    break
                except TransientError:
                    if attempt == max_retries:
                        quarantined.append(doc_id)
                    else:
                        await asyncio.sleep(0.01 * (attempt + 1))  # bounded backoff

    workers = [asyncio.ensure_future(worker()) for _ in range(concurrency)]
    await producer()
    await asyncio.gather(*workers)

    return results, quarantined


if __name__ == "__main__":
    doc_ids = list(range(50))

    results = asyncio.run(run_with_semaphore_only(doc_ids[:10], concurrency=3))
    print(f"Semaphore-only (anti-pattern): {len(results)} documents embedded")

    results, quarantined = asyncio.run(
        run_with_bounded_queue(doc_ids, concurrency=5, queue_maxsize=10, fail_once_ids={7, 23})
    )
    print(f"Bounded queue: {len(results)} embedded, {len(quarantined)} quarantined")
