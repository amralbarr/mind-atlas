# Multi-Threading

**Multi-threading** means a program runs multiple threads of execution at once, letting it do more than one thing in parallel (true parallelism on multi-core hardware) or interleaved (time-sliced on a single core).

## Core Idea

```text
Thread 1: Task A -----> Task A -----> Task A
Thread 2: Task B -----> Task B -----> Task B   (running at the same time)
Thread 3: Task C -----> Task C -----> Task C
```

Unlike [single-threading](single-threading.md), where tasks run strictly one after another, multiple threads can genuinely overlap in time — on a multi-core CPU, different threads can execute on different cores simultaneously; on a single core, the OS scheduler time-slices between them so fast it looks simultaneous.

## Why Use It

- **CPU-bound work** — split a large computation across threads to use all available CPU cores (image processing, numerical computation, compression).
- **Responsiveness** — keep a UI or main thread free to respond to input while background threads do heavy work.
- **Throughput** — serve many concurrent requests/connections without each one blocking the next.

## Shared Memory — The Core Trade-off

Threads within the same process share the same memory space. That's what makes multi-threading powerful (no copying data between threads) and dangerous (two threads can read/write the same variable at the same time).

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1  # NOT atomic: read, add, write -- three separate steps

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # expected 200_000 -- often prints less, due to a race condition
```

Two threads can both read `counter` before either writes back the incremented value, silently dropping an update. This is a **race condition** — see [Idempotency and Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) for the general pattern and how to defend against it.

## Locks / Mutexes — The Usual Fix

A **lock** (mutex) ensures only one thread executes a critical section at a time:

```python
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:          # only one thread inside this block at a time
            counter += 1
```

This fixes correctness but reintroduces some of [single-threading](single-threading.md)'s cost: threads now serialize on the lock, and excessive locking can erase the parallelism benefit entirely (or cause **deadlock** if two threads wait on each other's locks).

## Python's GIL — A Language-Specific Caveat

CPython (the standard Python interpreter) has a **Global Interpreter Lock (GIL)**: only one thread executes Python bytecode at a time, even on a multi-core machine. This means Python threads give real concurrency for **[I/O](../../programming/fundamentals/io.md)-bound** work (the GIL is released during [I/O](../../programming/fundamentals/io.md) waits) but not for **CPU-bound** work — a CPU-heavy Python computation split across threads will not run faster than single-threaded, because only one thread's Python code actually runs at once.

```
I/O-bound Python work  → threading helps (GIL released while waiting on I/O)
CPU-bound Python work  → threading does NOT help (GIL serializes bytecode execution)
                        → use multiprocessing instead (separate processes, separate GILs)
                        → or asyncio for I/O-bound work without thread overhead
```

This is why Python's own [asyncio](../../backend/architecture/asyncio.md) exists as a *single-threaded* alternative for [I/O](../../programming/fundamentals/io.md) concurrency — it avoids both the GIL ceiling and the race-condition risk of real threads, at the cost of needing `async`/`await` throughout the call chain.

## Context-Switching Overhead

Every time the OS scheduler switches which thread is running on a CPU core, it pays a real cost: saving one thread's register state, loading another's. More threads than CPU cores means more switching, not more real parallelism — past a certain thread count, adding more threads can make things *slower*, not faster.

## Single-Thread vs. Multi-Thread

| Feature | [Single thread](single-threading.md) | Multi thread |
|---|---|---|
| Execution | One at a time | Parallel (multi-core) or interleaved (single-core) |
| Complexity | Simple | Complex (locks, shared state, ordering) |
| Performance | Limited (one core) | High for CPU-bound work, if cores are available |
| Bugs | Fewer (no race conditions) | More (race conditions, deadlocks) |
| Memory | One stack | Shared heap + per-thread stack |

## Advantages

- Uses multiple CPU cores for real parallel speedup on CPU-bound work.
- Keeps a program responsive while background threads do heavy work.
- Threads share memory directly — no [serialization](../../programming/fundamentals/serialization.md)/copying cost between them (unlike separate processes).

## Disadvantages

- Race conditions when threads touch shared state without synchronization.
- Deadlocks when locks are acquired in inconsistent order.
- Harder to reason about and debug than [single-threaded](single-threading.md) code — bugs can be non-deterministic, appearing only under specific timing.
- In CPython specifically, the GIL caps CPU-bound speedup regardless of thread count.

## Practical Implication

Reach for multi-threading when work is CPU-bound and the runtime gives real parallelism (most languages; Python needs `multiprocessing` instead, due to the GIL). Reach for [asyncio](../../backend/architecture/asyncio.md)/an [event loop](../../programming/javascript/event-loop.md) instead when work is [I/O](../../programming/fundamentals/io.md)-bound — waiting on network/disk, not burning CPU — since that avoids race conditions and locking entirely while still handling many tasks concurrently.

## One-Line Definition

> Multi-threading means running multiple threads of execution at once, sharing memory, trading added concurrency/throughput for the risk of race conditions and the cost of synchronization.

## Related

- [Single-Threading](single-threading.md) — the one-thread-at-a-time model this contrasts with
- [Idempotency and Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) — what goes wrong when threads share state without synchronization, and how to guard against it
- [Asyncio](../../backend/architecture/asyncio.md) — Python's single-threaded alternative for [I/O](../../programming/fundamentals/io.md) concurrency, sidesteps the GIL and race conditions entirely
- [The Event Loop](../../programming/javascript/event-loop.md) — JavaScript's single-threaded concurrency model, the same underlying idea [asyncio](../../backend/architecture/asyncio.md) borrows
- [Asynchronous / Non-Blocking Execution](../../programming/fundamentals/asynchronous-non-blocking-execution.md)
- [Queues](../messaging/queues.md) — offloading CPU-heavy work to background workers instead of blocking a request-handling thread
- [Mesh Architecture](mesh-architecture.md)
