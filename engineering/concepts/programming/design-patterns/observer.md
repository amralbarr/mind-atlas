# Observer Pattern

The Observer pattern defines a one-to-many dependency between objects: a **subject** maintains a list of **observers** and notifies all of them automatically whenever its state changes, without needing to know anything about what each observer actually does with that notification.

## Basic Implementation

```typescript
interface Observer {
  update(data: string): void;
}

class Subject {
  private observers: Observer[] = [];

  subscribe(observer: Observer): void {
    this.observers.push(observer);
  }

  unsubscribe(observer: Observer): void {
    this.observers = this.observers.filter((o) => o !== observer);
  }

  notify(data: string): void {
    for (const observer of this.observers) {
      observer.update(data);
    }
  }
}

class EmailAlert implements Observer {
  update(data: string) {
    console.log(`Emailing alert: ${data}`);
  }
}

class LogWriter implements Observer {
  update(data: string) {
    console.log(`Logging: ${data}`);
  }
}

const orderStatus = new Subject();
const emailAlert = new EmailAlert();
const logWriter = new LogWriter();

orderStatus.subscribe(emailAlert);
orderStatus.subscribe(logWriter);

orderStatus.notify("Order #1042 shipped");
// Emailing alert: Order #1042 shipped
// Logging: Order #1042 shipped
```

`Subject` has no idea what `EmailAlert` or `LogWriter` actually do — it only knows they implement `update()`. New observers can be added or removed at runtime without touching `Subject`'s code at all.

## Real-World Examples Already in Use

This pattern is so common that most codebases use it constantly without naming it:

- **DOM events** — `element.addEventListener("click", handler)` is the Observer pattern: the element is the subject, `handler` is the observer, and the browser calls every registered handler when the click happens.
- **Node.js `EventEmitter`** — `emitter.on("data", callback)` / `emitter.emit("data", payload)` is a direct, built-in implementation of subscribe/notify.
- **RxJS `Observable`** — a more powerful, composable version of the same idea, adding operators (`map`, `filter`, `debounceTime`) to transform the stream of notifications before an observer receives them.
- **React state updates** — components that subscribe to a store (Redux, Zustand) re-render when the store's state changes, which is the store acting as subject and the components as observers.

## Observer vs. Publish/Subscribe (Pub/Sub)

These are frequently used interchangeably, but they differ in coupling:

| | Observer | [Pub/Sub](../../distributed-systems/messaging/publish-subscribe.md) |
|---|---|---|
| Awareness | The subject holds direct references to its observers | Publishers and subscribers don't know about each other at all |
| Coupling | Tighter — subject and observer typically share the same process/scope | Looser — a message broker/event bus sits between them |
| Typical mechanism | Direct method call (`observer.update()`) | A broker/topic ([Kafka](../../distributed-systems/messaging/kafka.md), [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md), Redis [Pub/Sub](../../distributed-systems/messaging/publish-subscribe.md), an in-process event bus) routes messages |
| Scope | Usually within a single application | Often crosses process or service boundaries — see [Message Brokers](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) |

In practice, `EventEmitter`/DOM events are closer to classic Observer (direct, synchronous, same-process), while a message queue between microservices is [Pub/Sub](../../distributed-systems/messaging/publish-subscribe.md) (decoupled, often asynchronous, cross-process).

## Trade-offs

| Benefit | Cost |
|---|---|
| Subject and observers are loosely coupled — neither needs to know the other's concrete type | Notification order isn't always guaranteed or obvious from reading the subject's code alone |
| Observers can be added/removed dynamically at runtime | Debugging can get harder — a single `notify()` call can trigger a cascade of side effects scattered across many observer classes |
| Multiple, unrelated systems (logging, email, analytics) can react to the same event without any of them modifying the subject | Forgetting to `unsubscribe()` a no-longer-needed observer is a common source of memory leaks — see [Memory Leaks in JS](../javascript/memory-leaks-js.md) |

## Common Questions

**Is `addEventListener` really the Observer pattern?**
> Yes — the DOM element is the subject, the callback you pass is the observer, and the browser's [event loop](../javascript/event-loop.md) calls `notify()` on your behalf whenever the event fires. It's one of the most common Observer implementations most developers use daily without thinking of it as a "pattern."

**When would I reach for RxJS instead of a plain `EventEmitter`?**
> When notifications need to be transformed, combined, or time-shaped before being consumed — e.g. debouncing rapid-fire events, merging multiple streams, or retrying on error. A plain Observer/`EventEmitter` gives you subscribe/notify; RxJS gives you subscribe/notify *plus* a full operator toolkit for the stream in between.

**Easy way to remember:** Subject = the thing being watched. Observer = the thing watching. `notify()` = "something changed, deal with it however you individually need to."

## Related

- [Strategy Pattern](strategy.md)
- [Message Brokers (Kafka, RabbitMQ, SQS)](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Memory Leaks in JS](../javascript/memory-leaks-js.md)
