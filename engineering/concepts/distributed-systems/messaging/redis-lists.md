# Redis Lists

Redis Lists are a Redis data structure that store an ordered sequence of strings — effectively a fast, in-memory list that supports push/pop from both ends, making it a natural building block for [message queues](queues.md).

## The Basic Idea

A Redis List works like this:

```text
["job1", "job2", "job3"]
```

Items can be added, removed, and processed in order.

## Core Operations

**Add items:**

```bash
RPUSH mylist "task1"
RPUSH mylist "task2"
# → ["task1", "task2"]

LPUSH mylist "task0"
# → ["task0", "task1", "task2"]
```

**Remove items:**

```bash
LPOP mylist   # removes "task0" from the left
RPOP mylist   # removes from the right
```

## Why Redis Lists Matter

They're commonly used to build:

- **Job queues:** `Producer → LPUSH → Redis List → Worker LPOP`.
- **Task pipelines**, where each item is one job (an [OCR](../../ai/ingestion/ocr.md) task, an embedding task, an [LLM](../../ai/generation/llm.md) task).
- **[FIFO or LIFO](../patterns/fifo-lifo.md) behavior**, depending on which ends you push and pop from:

| Mode | Operation |
|---|---|
| FIFO queue | `LPUSH` + `RPOP` |
| Stack (LIFO) | `LPUSH` + `LPOP` |

## Real-World Queue Example

```text
Producer: LPUSH queue "process_image_123"
Worker:   BRPOP queue
```

The worker blocks until a job appears.

### Blocking Operations

`BRPOP` / `BLPOP` let a worker wait for a new item instead of polling:

```bash
BRPOP queue 0
```

A timeout of `0` means wait forever; the call returns as soon as a job arrives.

## Why Redis Lists Are Used in AI Pipelines

For a pipeline like `OCR → Chunking → Embedding → RAG`, Redis Lists are attractive because they're fast (in-memory), simple to reason about, easy to scale by adding workers, and require no complex setup.

## Limitations

Redis Lists are not a good fit for large-scale systems:

- No persistence guarantee comparable to [Kafka](kafka.md).
- No replay of past events.
- Limited observability into the queue's state.
- Data can be lost if Redis isn't configured for durability (AOF/RDB).

## When to Use Redis Lists

**Good for:** background jobs, AI task queues, image processing, simple pipelines.

**Not good for:** event streaming, financial systems, large-scale distributed logs.

**One-line definition:** Redis Lists are an ordered in-memory data structure used to implement simple queues or stacks for fast task processing.

**Mental model:** a fast conveyor belt where tasks are added at one end and workers pick them up from the other.

## Related

- [Message Queues](queues.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [BullMQ](bullmq.md)
- [FIFO vs LIFO](../patterns/fifo-lifo.md)
- [Single-Threading](../patterns/single-threading.md)
- [Pipeline Orchestration](../../ai/infrastructure/pipeline-orchestration.md)
- [Distributed Locks](../patterns/distributed-locks.md)
