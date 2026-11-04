# Hystrix

Hystrix was Netflix's original JVM circuit-breaker library — one of the first widely-adopted implementations of the [resilience patterns](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns) (circuit breaker, bulkhead, fallback) for microservices, and a major influence on the whole category. Netflix placed it into **maintenance mode** in 2018, and [Resilience4j](resilience4j.md) is now the standard successor for new JVM projects.

## Core Concepts

| Term | Meaning |
|---|---|
| **Command** | A unit of work (typically a call to another service) wrapped in a `HystrixCommand`, giving it circuit-breaking, timeout, and fallback behavior |
| **Thread pool isolation** | Hystrix's default isolation strategy — each dependency gets its own fixed-size thread pool, so a hung call to one dependency can't exhaust threads needed to call a different, healthy one (a form of [bulkhead](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns)) |
| **Fallback** | Code that runs when a command fails or the circuit is open — returning a cached/default value instead of propagating the failure to the caller |
| **Hystrix Dashboard** | A real-time visualization of each command's circuit state, request volume, and latency |

## A Hystrix Command (Legacy Pattern)

```java
public class GetOrderCommand extends HystrixCommand<Order> {
    private final String orderId;

    public GetOrderCommand(String orderId) {
        super(HystrixCommandGroupKey.Factory.asKey("OrderService"));
        this.orderId = orderId;
    }

    @Override
    protected Order run() {
        return orderServiceClient.getOrder(orderId);
    }

    @Override
    protected Order getFallback() {
        return Order.unavailable(orderId); // returned if run() fails or times out
    }
}

Order order = new GetOrderCommand("123").execute();
```

## Spring Cloud Annotation Style

```java
@HystrixCommand(fallbackMethod = "getOrderFallback")
public Order getOrder(String orderId) {
    return orderServiceClient.getOrder(orderId);
}

public Order getOrderFallback(String orderId, Throwable t) {
    return Order.unavailable(orderId);
}
```

## Common Questions

**Should a new project still adopt Hystrix?**
> No — it's been in maintenance mode (security fixes only, no new features) since 2018. [Resilience4j](resilience4j.md) implements the same core ideas with active maintenance and a lighter, more modular design; Hystrix is documented here mainly to recognize it in legacy Spring Cloud codebases still running it.

**What's the practical downside of Hystrix's thread-pool-per-dependency isolation?**
> It provides strong bulkhead isolation, but at real resource cost — every dependency needs its own thread pool sized correctly, which adds memory/thread overhead and tuning burden. [Resilience4j](resilience4j.md) makes this isolation strategy opt-in (semaphore-based bulkhead by default, thread-pool bulkhead available) rather than the mandatory default.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Resilience4j](resilience4j.md)
- [Eureka](../service-discovery/eureka.md)
- [Exponential Backoff and Jitter](exponential-backoff-and-jitter.md) — the retry algorithm this library's retry mechanism implements
