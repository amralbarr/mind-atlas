# FIFO vs LIFO

FIFO and LIFO are two basic ways systems manage the order in which items are processed — relevant to data structures, inventory systems, and [message queues](../messaging/queues.md) alike.

## FIFO (First In, First Out)

FIFO means the first item added is the first one removed — like a queue at a supermarket checkout.

If items are added in order `A → B → C`, they're removed in the same order: `A → B → C`.

**Real-world examples:**

- A printer queue (the first document sent prints first).
- A traffic queue at a toll booth.
- Task scheduling in operating systems.
- [Message queues](../messaging/queues.md) ([Kafka](../messaging/kafka.md) and [RabbitMQ](../messaging/rabbitmq.md) commonly preserve FIFO ordering per partition/queue).

**Key idea:** the oldest data is processed first.

## LIFO (Last In, First Out)

LIFO means the last item added is the first one removed — like a stack of plates.

If items are added in order `A → B → C`, they're removed in reverse order: `C → B → A`.

**Real-world examples:**

- A stack of books.
- Undo/redo in software (the last action is undone first).
- The function call stack in programming.
- Thread execution stacks in an OS.

**Key idea:** the newest data is processed first.

## Quick Comparison

| Feature | FIFO | LIFO |
|---|---|---|
| Full name | First In, First Out | Last In, First Out |
| Structure | Queue | Stack |
| Processing order | Oldest first | Newest first |
| Real-life analogy | Queue line | Stack of plates |
| Common use | Messaging, scheduling | Recursion, undo systems |

## In Pipeline and Queue Systems

For event-driven backends (IoT pipelines, event queues, Redis/Firebase-backed orchestration):

- **FIFO** is typically used for sensor events, job-processing pipelines, and message brokers, where order of arrival should be preserved.
- **LIFO** is typically used for rollback systems, local execution stacks, and debugging/execution tracing.

## References

- *Operating Systems: Three Easy Pieces* (Remzi H. Arpaci-Dusseau)
- Redis Data Structures documentation (Lists behave as FIFO or LIFO depending on which ends you push/pop from)
- [Apache Kafka](../messaging/kafka.md) design docs (partition ordering and the log-append model)

## Related

- [Message Queues](../messaging/queues.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Redis Lists](../messaging/redis-lists.md)
- [Single-Threading](single-threading.md)
- [Saga Pattern](saga-pattern.md)
