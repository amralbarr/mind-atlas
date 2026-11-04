# Resilience4j

Resilience4j is a lightweight, modern JVM library implementing the standard [resilience patterns](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns) — circuit breaker, retry, timeout, bulkhead, rate limiter — as small, composable, functional decorators around a call, rather than a single all-in-one framework. It's the direct successor to Netflix's [Hystrix](hystrix.md), which is now in maintenance mode.

## Core Concepts

| Term | Meaning |
|---|---|
| **Circuit Breaker** | Tracks recent call failures; once a failure-rate threshold is crossed, it "opens" and fails fast for a cooldown period instead of continuing to call a struggling dependency |
| **Retry** | Automatically retries a failed call, with configurable backoff and a max attempt count |
| **Bulkhead** | Limits concurrent calls to a given dependency (via a semaphore or a fixed thread pool), preventing one slow dependency from exhausting shared resources |
| **RateLimiter** | Caps how many calls per time window are permitted, independent of failure behavior |
| **TimeLimiter** | Enforces a maximum duration on a call, treating a timeout as a failure the other patterns can react to |
| **State machine (Circuit Breaker)** | `CLOSED` (normal) → `OPEN` (failing fast) → `HALF_OPEN` (a few trial calls allowed) → back to `CLOSED` or `OPEN` depending on their outcome |

## Configuring a Circuit Breaker

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)                          // open above 50% failure rate
    .waitDurationInOpenState(Duration.ofSeconds(30))    // cooldown before trying again
    .slidingWindowSize(10)                              // evaluate over the last 10 calls
    .build();

CircuitBreaker circuitBreaker = CircuitBreaker.of("paymentService", config);

Supplier<String> decorated = CircuitBreaker.decorateSupplier(
    circuitBreaker, () -> paymentServiceClient.charge(order)
);

String result = Try.ofSupplier(decorated)
    .recover(throwable -> "fallback-response")
    .get();
```

## Combining Multiple Patterns

```java
Supplier<String> decorated = CircuitBreaker.decorateSupplier(circuitBreaker,
    Retry.decorateSupplier(retry,
        TimeLimiter.decorateFutureSupplier(timeLimiter,
            () -> callPaymentServiceAsync(order))));
```

Decorators compose from the inside out — a call is time-limited, then retried on failure, then subject to the circuit breaker's overall failure tracking — each pattern handling one concern independently rather than one framework trying to do everything at once.

## Spring Boot Integration

```java
@CircuitBreaker(name = "paymentService", fallbackMethod = "fallback")
@Retry(name = "paymentService")
public String chargeCustomer(Order order) {
    return paymentServiceClient.charge(order);
}

public String fallback(Order order, Throwable t) {
    return "payment-pending";
}
```

## Common Questions

**Why did Resilience4j replace [Hystrix](hystrix.md) as the standard choice?**
> [Hystrix](hystrix.md) was placed into maintenance mode by Netflix in 2018 — no new features, security-fix-only support. Resilience4j offers the same core patterns with a lighter footprint (no mandatory thread-pool isolation by default — bulkhead is opt-in and configurable), functional-style composition, and active maintenance.

**Does a circuit breaker replace the need for retries?**
> No — they solve different problems and are typically combined: retry handles a single transient blip (worth trying again immediately), while the circuit breaker handles sustained failure (stop trying altogether for a while). Retrying blindly against an already-open circuit just wastes calls that are guaranteed to fail fast anyway.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Hystrix](hystrix.md)
- [Polly](polly.md)
- [Spring Cloud Gateway](../api-gateways/spring-cloud-gateway.md)
- [Exponential Backoff and Jitter](exponential-backoff-and-jitter.md) — the retry algorithm this library's `Retry` module implements
