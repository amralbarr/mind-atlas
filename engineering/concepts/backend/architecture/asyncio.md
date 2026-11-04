# Asyncio

`asyncio` is Python's built-in framework for writing **asynchronous (non-blocking) code** using a single thread.

## Why Do We Need Async?

Normally Python runs like this:

```text
Task 1 → wait → Task 2 → wait → Task 3
```

The problem: waiting on [I/O](../../programming/fundamentals/io.md), API calls, or DB queries wastes time.

### The Async Idea

Instead of waiting idly:

```text
Start Task 1 → switch → Task 2 → switch → Task 3
```

While one task waits, the CPU works on others.

## Key Concepts

### Coroutine

A special function:

```python
async def fetch_data():
    return "data"
```

### `await`

Means: pause here until the result is ready.

## Simple Example

```python
import asyncio

async def task():
    print("Start")
    await asyncio.sleep(2)
    print("End")

asyncio.run(task())
```

Output flow: `Start → wait 2s → End`. But internally, [the event loop](../../programming/javascript/event-loop.md) is running and the thread is NOT blocked.

## Event Loop (Core of asyncio)

`asyncio` uses an **[event loop](../../programming/javascript/event-loop.md)** that manages and switches tasks. This is the Python equivalent of the [JavaScript event loop](../../programming/javascript/event-loop.md) — same core idea of a single thread scheduling work while waiting on [I/O](../../programming/fundamentals/io.md).

### Multiple Tasks Example

```python
import asyncio

async def task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} finished")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3),
    )

asyncio.run(main())
```

Execution flow:

```text
A start
B start
C start
B finish
A finish
C finish
```

Because they run concurrently.

## Concurrency vs Parallelism

| Concept     | Meaning                   |
| ----------- | ------------------------- |
| Concurrency | switching tasks (asyncio) |
| Parallelism | multiple CPU cores        |

## When Is asyncio Useful?

Best for:

- API calls
- database queries
- file [I/O](../../programming/fundamentals/io.md)
- network requests

### When Is It NOT Useful?

Bad for heavy CPU tasks (ML training, tight compute loops), because `asyncio` does NOT use multiple cores.

## Real-World Example

Without async:

```python
download_file()
download_file()
download_file()
```

Each call waits sequentially.

With async:

```python
await gather(
    download_file(),
    download_file(),
    download_file()
)
```

Much faster total execution.

## Async vs Sync

| Sync           | Async          |
| -------------- | -------------- |
| Blocking       | Non-blocking   |
| Sequential     | Concurrent     |
| Slower for [I/O](../../programming/fundamentals/io.md) | Faster for [I/O](../../programming/fundamentals/io.md) |

## Behind the Scenes

`asyncio` uses:

- an [event loop](../../programming/javascript/event-loop.md)
- a task queue
- a coroutine scheduler

## Common Mistake

```python
async def test():
    print("hello")
```

Calling it directly does NOT run it:

```python
test()  # does NOT run
```

Correct usage:

```python
asyncio.run(test())
```

## Advanced Tools in asyncio

- `asyncio.gather()` — run multiple tasks
- `asyncio.create_task()` — schedule a background task
- `asyncio.sleep()` — non-blocking delay

## Common Questions

**Q1) What is asyncio?**

> asyncio is Python's library for writing concurrent code using async/await and an [event loop](../../programming/javascript/event-loop.md).

**Q2) What is [the event loop](../../programming/javascript/event-loop.md)?**

> A loop that manages and schedules async tasks.

**Q3) Difference between concurrency and parallelism?**

- concurrency = switching tasks
- parallelism = multiple CPU cores

**Q4) Why use async?**

To improve performance for [I/O](../../programming/fundamentals/io.md)-heavy operations.

**Q5) Does async improve CPU performance?**

No — only [I/O](../../programming/fundamentals/io.md)-bound tasks benefit.

### Senior-Level Summary

> asyncio is a single-threaded concurrency model based on an [event loop](../../programming/javascript/event-loop.md) that enables efficient non-blocking [I/O](../../programming/fundamentals/io.md) operations by suspending coroutines at await points and resuming them when their tasks are ready.

### Easy Memory Trick

```text
asyncio = do many things while waiting
```

## Related

- [ASGI](asgi.md)
- [Event Loop](../../programming/javascript/event-loop.md)
- [Python for AI Engineering](../../ai/infrastructure/python-ai-engineering.md)
