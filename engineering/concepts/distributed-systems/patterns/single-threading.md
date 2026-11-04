# Single-Threading

**Single-threading** means a program executes one task at a time using a single thread of execution.

## Core Idea

```text
Task A → Task B → Task C (one after another)
```

There's no parallel execution — everything happens sequentially.

## What Is a Thread?

A thread is the smallest unit of execution inside a program, scheduled onto the CPU by the operating system.

## Example

```js
console.log("Start");

for (let i = 0; i < 1e9; i++) {} // heavy task

console.log("End");
```

Output:

```text
Start
(wait...)
End
```

The loop blocks everything — nothing else runs until it finishes.

## Blocking Behavior

In a single-threaded system, one long-running task means the entire program stops. This is called **blocking**.

Node.js is a common real-world example: its main thread is single-threaded, but it uses asynchronous techniques to avoid blocking wherever possible.

## How Single-Threaded Systems Still Handle Many Tasks

Single-threaded runtimes often rely on:

- An [event loop](../../programming/javascript/event-loop.md)
- Callbacks and promises
- Asynchronous [I/O](../../programming/fundamentals/io.md)

This makes them *feel* concurrent, but only one piece of code ever actually executes at a time.

## Single-Thread vs. Multi-Thread

| Feature | Single thread | [Multi thread](multi-threading.md) |
|---|---|---|
| Execution | One at a time | Parallel |
| Complexity | Simple | Complex |
| Performance | Limited (one core) | High (multiple cores) |
| Bugs | Fewer (no race conditions) | More (race conditions) |

## Advantages

- Simple to design and reason about.
- Easier debugging.
- No race conditions.
- Lower memory usage.

## Disadvantages

- Cannot use multiple CPU cores effectively.
- A blocking task freezes the entire system.
- Not ideal for heavy computation.

## Practical Implication

Single-threaded runtimes like Node.js are well suited to [I/O](../../programming/fundamentals/io.md)-heavy work — APIs, database calls, network requests — but poorly suited to CPU-heavy work like large-scale data or AI processing. That's why heavy computation is typically offloaded to separate worker processes, dedicated services better suited to CPU-bound work, or background [queues](../messaging/queues.md) rather than run on the main thread.

## One-Line Definition

> Single-threading means executing one task at a time using a single execution thread.

## Related

- [Multi-Threading](multi-threading.md) — the parallel/interleaved alternative, and the race conditions/locking it introduces
- [Mesh Architecture](mesh-architecture.md)
- [Queues](../messaging/queues.md)
- [Decoupling Pipeline Stages](decouple-stages.md)
