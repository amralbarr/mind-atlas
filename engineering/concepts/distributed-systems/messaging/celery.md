# Celery

Celery is Python's standard distributed task queue library — the direct equivalent of [BullMQ](bullmq.md) in the Node.js ecosystem. Like [BullMQ](bullmq.md), Celery is **not itself a broker** — it's a task-queue layer (job semantics: retries, scheduling, result tracking) that runs on top of an actual broker, most commonly [Redis](redis-lists.md) or [RabbitMQ](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **Task** | A Python function decorated to be run asynchronously by a worker instead of inline |
| **Worker** | A separate process that pulls tasks off the broker and executes them |
| **Broker** | The actual message transport underneath Celery — Redis or [RabbitMQ](rabbitmq.md) in the vast majority of setups |
| **Result backend** | Optional separate store (often also Redis, or a database) for retrieving a task's return value/status later |

## Defining and Calling a Task

```python
# tasks.py
from celery import Celery

app = Celery('myapp', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')

@app.task
def send_welcome_email(user_id: int):
    # ... actual send logic
    return f"sent to user {user_id}"
```

```python
# calling code — returns immediately, doesn't block on the actual send
result = send_welcome_email.delay(123)

# check status/result later (requires a result backend)
result.status   # 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE'
result.get(timeout=10)  # blocks until done or raises on failure/timeout
```

Running a worker to actually process tasks:

```bash
celery -A tasks worker --loglevel=info
```

## Retries

```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def call_flaky_api(self):
    try:
        ...
    except SomeTransientError as exc:
        raise self.retry(exc=exc)
```

## Scheduled & Periodic Tasks (Celery Beat)

Celery's own scheduler process, **Beat**, triggers tasks on a recurring schedule — the Python-ecosystem equivalent of [BullMQ](bullmq.md)'s `repeat` option:

```python
app.conf.beat_schedule = {
    'daily-report': {
        'task': 'tasks.generate_daily_report',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

Beat itself is a separate process from the workers that execute tasks — it just enqueues tasks on schedule; actual execution still goes through the normal worker pool.

## Common Questions

**Why does Celery need a separate result backend if it already has a broker?**
> The broker's job is reliably delivering the task to a worker once; a result backend is a different concern — storing the *outcome* somewhere a caller can check later, potentially long after the message itself has been consumed and removed from the broker.

**Is Celery the right choice outside of Python?**
> No — it's Python-specific by design (tasks are Python functions/objects). A Node.js codebase reaches for [BullMQ](bullmq.md) for the same job; other ecosystems have their own equivalents (Sidekiq for Ruby, for example).

## Related

- [BullMQ](bullmq.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Redis Lists](redis-lists.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
