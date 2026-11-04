# Asynchronous / Non-Blocking Execution

**Blocking** means the thread that made a call sits idle — doing nothing else — until that call finishes. **Non-blocking** (asynchronous) means the calling thread starts the operation and immediately moves on to other work, getting the result later via a callback, a promise/future it can check or compose, or an `await` that resumes a suspended function when the result arrives. This is a language-agnostic runtime concept — every mainstream language has some version of it (Python's `asyncio`, JavaScript's [event loop](../javascript/event-loop.md) and Promises, Java's `CompletableFuture`, C#'s `Task`, Go's goroutines) — and it's the single idea underneath async/await syntax in all of them.

## Blocking vs. Non-Blocking, Precisely

```text
Blocking:
  call db.query(sql)   →  thread waits here, doing nothing, until the DB responds
  (next line runs only after the response arrives)

Non-blocking:
  call db.query(sql)   →  thread hands the request off and keeps running
  (next line runs immediately; the result shows up later via callback/promise/await)
```

The operation itself — the network round-trip, the disk read, the DB query — takes the same wall-clock time either way. What changes is whether the *calling thread* is forced to sit idle for that duration or is free to do other useful work while the operation is in flight.

## Why It Matters: Threads Are a Limited Resource, I/O Waits Are Idle Time

An OS thread isn't free — each one carries a real memory footprint (its stack) and the kernel has to schedule it, context-switch into and out of it, and track it. A classic **thread-per-request** server model (common in older blocking architectures: one thread handles one connection/request from start to finish) runs into a hard ceiling once concurrent connections climb into the thousands — this is the well-known **C10K problem**: you simply can't keep tens of thousands of OS threads alive and scheduled efficiently, most of them blocked waiting on a slow client or a downstream call that hasn't returned yet.

The key insight non-blocking [I/O](io.md) exploits: during an [I/O](io.md) wait (network, disk, a downstream service), the CPU isn't actually doing anything — it's just waiting for hardware or another machine to respond. If the calling thread doesn't have to sit there blocked for that wait, a *single* thread can have thousands of [I/O](io.md) operations in flight simultaneously, moving between them as each one becomes ready, instead of needing one dedicated thread per operation. This is exactly why a single-threaded Node.js process or a Python `asyncio` application can serve tens of thousands of concurrent connections, where an equivalent thread-per-request blocking server would need roughly as many OS threads as concurrent connections.

**This only helps [I/O](io.md)-bound work.** Non-blocking execution doesn't make the CPU do more work per second or run code in parallel — it only avoids wasting thread-time on idle waits. A CPU-bound task (image processing, ML training, a tight compute loop) gets zero benefit from being made "async": there's no idle waiting to reclaim, so true speedup there requires actual parallelism (multiple threads/processes/cores), not non-blocking [I/O](io.md).

## The Common Implementation Patterns

These are the same underlying idea expressed through progressively nicer syntax — every one of them is ultimately "start the operation, don't block, get notified later":

### Callbacks

The oldest and most primitive pattern: pass a function to be invoked once the operation finishes.

```text
readFile(path, function(err, data) {
  // runs later, whenever the read completes
})
nextLine()   // runs immediately, doesn't wait for readFile
```

Nesting callbacks inside callbacks (to sequence several async steps) produces the infamous "callback hell" — deeply indented, hard-to-follow code — which is the main reason later patterns exist.

### Promises / Futures

A **promise** (JavaScript's term) or **future** (the term used in Python's `concurrent.futures`, Java's `CompletableFuture`, etc.) is an object that represents a result that doesn't exist yet but will — it has a state (pending → fulfilled/resolved or rejected/failed) and lets you attach what to do with the eventual result without nesting callbacks inside callbacks. Promises/futures can be composed: run several concurrently and wait for all of them, race them against each other, or chain one's result into the next step.

### `async`/`await` — Syntax Sugar, Not a Different Mechanism

`async`/`await` (in JavaScript, Python, C#, and others) lets non-blocking code *read* like ordinary sequential blocking code, while still behaving non-blockingly underneath:

```text
async function getUser() {
  const user = await fetchUser();     // thread is freed here, not blocked;
  const orders = await fetchOrders(); // this line resumes once fetchUser's result is ready
  return orders;
}
```

Under the hood, `await` is still built on promises/futures and a scheduler — it just removes the visual nesting of `.then()` chains or callback pyramids. Recognizing this is important: `await` does not introduce a new concurrency model, it's a more readable way to write the same callback/promise-based non-blocking execution.

### The Event Loop (or Equivalent Scheduler)

Something has to actually track which operations are in flight and resume the right piece of code when each one's result is ready — that's the job of an **[event loop](../javascript/event-loop.md)** (or a "reactor" in some other runtimes). A single thread runs the loop: it hands [I/O](io.md) waits off to the operating system's own async [I/O](io.md) facilities (e.g. `epoll` on Linux, `kqueue` on BSD/macOS, IOCP on Windows), continues running other application code in the meantime, and when the OS reports an operation is ready, the loop resumes the corresponding paused callback/coroutine. The specific queues, phases, and priority rules differ by runtime — see the JavaScript- and Python-specific files linked below for those concrete mechanics.

## Distinguishing This From Similarly-Named Concepts Already in This Handbook

This general concept is easy to conflate with several more specific things already documented elsewhere here — each of those files specializes *this* one rather than duplicating it:

- **[Asyncio](../../backend/architecture/asyncio.md)** — Python's concrete library implementing this general concept: `async def` coroutines, `await`, `asyncio.gather()`, and Python's particular [event loop](../javascript/event-loop.md) implementation. Read this file for the universal vocabulary (blocking vs. non-blocking, callback/promise/future/async-await, [event loop](../javascript/event-loop.md)) and *why* non-blocking [I/O](io.md) exists at all; read `asyncio.md` for Python's actual syntax and standard-library API.
- **[The Event Loop](../javascript/event-loop.md)** — the specific scheduling mechanism JavaScript's runtime (V8/Node.js) uses to implement non-blocking execution: the call stack, Web/Node APIs, the macrotask (callback) queue, and the microtask queue, with concrete ordering rules between them. It's one concrete implementation of the general "[event loop](../javascript/event-loop.md)" pattern described above.
- **[Promise Chaining](../javascript/promise-chaining.md)** — JavaScript's specific API (`.then()` chains, and `async/await` as sugar over it) for composing non-blocking operations sequentially, plus its error-propagation rules (`.catch()`). It's the JS-specific realization of the general "promise/future" pattern described above.
- **["Synchronous vs. Asynchronous" in Network Communication](../../distributed-systems/patterns/network-communication.md)** — a *different, narrower* concept at a different layer, easy to mix up with this one because it uses the same words. That section is about the relationship between **two separate services** communicating over a network: does the caller wait for the callee's response before continuing (synchronous RPC/[HTTP](../../networking/http.md)/[gRPC](../../backend/api/grpc.md)-style request-response), or does it fire a message/event and move on without waiting for the other side to finish processing it (asynchronous messaging/event streaming, e.g. [Kafka](../../distributed-systems/messaging/kafka.md) or [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md))? This file, by contrast, is about **a single process's own I/O model** — whether its own thread blocks while waiting on *any* operation (a disk read, a socket, a timer, a call to another process). The two axes are independent: a service can be implemented with fully non-blocking I/O internally while still making synchronous (wait-for-the-answer) [HTTP](../../networking/http.md) calls to another service — e.g. an async Node.js or Python handler does `await httpClient.get(...)`, which is synchronous in the sense that the business logic waits for that response before proceeding, while the underlying thread is never blocked during the wait. That's why these two "sync/async" ideas are documented in two separate files rather than one.
- **[Single-Threading](../../distributed-systems/patterns/single-threading.md)** — describes the baseline (one thread, one task at a time, strictly sequential) that non-blocking execution is contrasted against; a single-threaded runtime with an [event loop](../javascript/event-loop.md) (Node.js, Python's `asyncio`) achieves concurrency without ever running two pieces of application code at the literal same instant, which is a distinct claim from parallelism.

## Common Questions

**Does "asynchronous" mean "runs in parallel" or "runs on another thread"?**
> Not necessarily. Non-blocking execution commonly happens on a *single* thread (Node.js, Python `asyncio`) — concurrency here comes from interleaving many in-flight operations on one thread while they wait on I/O, not from running multiple pieces of code at the exact same instant on multiple cores. True parallelism (multiple cores actually executing simultaneously) is a separate, complementary concept.

**If `async`/`await` is just sugar over promises/callbacks, why does it matter?**
> Because readability has real engineering value — deeply nested callbacks or long `.then()` chains are harder to reason about, especially for error handling and sequencing multiple dependent steps. `async`/`await` doesn't change what's possible, but it changes what's maintainable, which is why most codebases prefer it once the language supports it.

**Does non-blocking I/O make a single CPU-bound computation finish faster?**
> No. Non-blocking execution reclaims idle thread-time during I/O waits; it does nothing for work that's genuinely CPU-bound with no waiting involved. Making a tight compute loop or an ML training step "async" doesn't speed it up — it can even add scheduling overhead for no benefit. CPU-bound work needs real parallelism (threads/processes/cores) to go faster.

**Can a blocking call accidentally undo the benefit of an otherwise non-blocking system?**
> Yes — this is a common real bug. If any code path in an event-loop-based system performs a genuinely blocking call (a synchronous file read, a CPU-heavy synchronous function, a blocking library call that doesn't yield control back to the loop), it blocks the *entire* [event loop](../javascript/event-loop.md)'s thread for that duration, stalling every other in-flight operation that thread was supposed to be servicing concurrently — not just the one that made the blocking call.

## Related

- [Asyncio](../../backend/architecture/asyncio.md)
- [The Event Loop](../javascript/event-loop.md)
- [Promise Chaining](../javascript/promise-chaining.md)
- [Microtasks vs Macrotasks](../javascript/microtask-vs-macrotask.md)
- [Network Communication](../../distributed-systems/patterns/network-communication.md)
- [Single-Threading](../../distributed-systems/patterns/single-threading.md)
