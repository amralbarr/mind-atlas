# I/O (Input/Output)

**I/O** is any operation where a program exchanges data with something outside the CPU/memory itself — reading or writing a file on disk, sending/receiving data over a network socket, reading from a database, printing to a terminal, reading keyboard/mouse input. The defining trait: an I/O operation has to wait on something slower than the CPU — a spinning disk, a network round-trip, another machine — rather than being limited by how fast the CPU can compute.

## Common Types of I/O

| Type             | Example                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| **Disk I/O**     | Reading/writing a file, a database's on-disk pages                                                   |
| **Network I/O**  | An [HTTP](../../networking/http.md) request, a database query over the wire, a message queue publish |
| **Standard I/O** | Reading stdin, writing stdout/stderr, terminal input                                                 |
| **Device I/O**   | Keyboard, mouse, sensors, a GPU transfer                                                             |

## I/O-Bound vs. CPU-Bound — The Core Classification

This is the distinction that decides which concurrency tool actually helps:

| | I/O-bound | CPU-bound |
|---|---|---|
| **Bottleneck** | Waiting on disk/network/another system | The CPU doing actual computation |
| **During the wait** | CPU sits idle — nothing to do until the response arrives | N/A — CPU is continuously busy |
| **What speeds it up** | [Non-blocking execution](asynchronous-non-blocking-execution.md) / an [event loop](../javascript/event-loop.md) — reclaim the idle wait time instead of blocking a thread on it | Real parallelism — [multiple threads/processes/cores](../../distributed-systems/patterns/multi-threading.md) actually computing at once |
| **Example** | API calls, database queries, file reads, downloading a file | Image processing, ML training, parsing a huge document, cryptographic hashing |
| **Python caveat** | `asyncio`/threads both help (the GIL releases during I/O waits) | Only `multiprocessing` helps — see [Multi-Threading](../../distributed-systems/patterns/multi-threading.md)'s GIL section |

## Why I/O Waits Are "Free" to Reclaim

The moment a program issues a disk read or a network request, the CPU has nothing left to do for that operation until the hardware or the remote machine responds — it's not computing, it's idle. This is the single fact that [non-blocking/asynchronous execution](asynchronous-non-blocking-execution.md) exploits: instead of a thread sitting there doing nothing during that wait, it can be freed to do other useful work, and resumed later once the result is ready. A CPU-bound task has no equivalent idle gap to reclaim — the CPU is genuinely busy the whole time, so only running more of it in parallel (not making it "async") makes it faster.

## Practical Implication

Classify the actual bottleneck before reaching for a concurrency tool: an API gateway spending most of its time waiting on downstream [HTTP](../../networking/http.md) calls and database queries is I/O-bound, and benefits enormously from [asyncio](../../backend/architecture/asyncio.md)/an [event loop](../../programming/javascript/event-loop.md) — adding more CPU cores barely helps, since the CPU wasn't the bottleneck. A batch job resizing a million images is CPU-bound, and needs real parallel workers (processes/cores), not async syntax — making it "non-blocking" does nothing when there's no idle wait to reclaim in the first place.

## Related

- [Asynchronous / Non-Blocking Execution](asynchronous-non-blocking-execution.md) — the mechanism that exploits I/O wait time specifically
- [Multi-Threading](../../distributed-systems/patterns/multi-threading.md) — real parallelism for CPU-bound work, and why it doesn't help I/O-bound Python code any more than [asyncio](../../backend/architecture/asyncio.md) does
- [Single-Threading](../../distributed-systems/patterns/single-threading.md) — how a single thread can still serve many I/O-bound tasks concurrently via an [event loop](../javascript/event-loop.md)
- [Asyncio](../../backend/architecture/asyncio.md) — Python's concrete async I/O implementation
- [The Event Loop](../javascript/event-loop.md)
- [Network Communication](../../distributed-systems/patterns/network-communication.md)
