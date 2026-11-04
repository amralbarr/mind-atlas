# Bounded Concurrent Worker — Runnable Example

A real bounded-queue + fixed-worker-pool embedding batch worker — companion to
[Design a bounded concurrent embedding batch worker (C10)](../../interview/interview-01/13-python-sql-coding-round.md#c10--hard--design-a-bounded-concurrent-embedding-batch-worker).

`run_with_semaphore_only()` is kept in the same file deliberately, to make
concrete exactly what the handbook's own Follow-up question warns about:
*"Does a semaphore alone bound memory? Not if millions of tasks are created
before acquiring it."* That function creates one `asyncio.Task` per document
upfront, regardless of `concurrency` — functionally correct on a small test
set (see the test for it), but a real memory problem at scale.

`run_with_bounded_queue()` is the actual recommended pattern: a producer
blocks on `queue.put()` once the queue is full, so memory is bounded by
`queue_maxsize + concurrency`, never by the total document count. It also
implements retries with bounded backoff and quarantines documents that
exhaust their retries, per the handbook's acceptance checks.

## Run it

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r bounded-concurrent-worker/requirements.txt
.venv/bin/python3 bounded-concurrent-worker/bounded_worker.py
.venv/bin/pytest bounded-concurrent-worker/tests/ -v
```

## Concepts this demonstrates

- [Asyncio](../../concepts/backend/architecture/asyncio.md)
- [Multi-Threading](../../concepts/distributed-systems/patterns/multi-threading.md) — the same bounded-resource reasoning applies to thread pools
- [Idempotency and Race Conditions](../../concepts/programming/fundamentals/idempotency-and-race-conditions.md)

## Related

- [Python & SQL Coding Round — Interview Q&A](../../interview/interview-01/13-python-sql-coding-round.md)
