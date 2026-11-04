# Polly

Polly is the .NET-ecosystem equivalent of [Resilience4j](resilience4j.md) — a library implementing the standard [resilience patterns](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns) (retry, circuit breaker, timeout, bulkhead, fallback) as composable policies that wrap a delegate/call, for C#/.NET services making calls to other services.

## Core Concepts

| Term | Meaning |
|---|---|
| **Policy** | A single resilience behavior (retry, circuit breaker, timeout, etc.), created independently and applied to a delegate |
| **PolicyWrap** | Multiple policies combined into one, executed in a defined order (e.g. timeout inside retry inside circuit breaker) |
| **Execution context** | Optional key-value data passed through a policy chain, useful for logging/correlating retries |
| **Reactive vs. proactive policies** | Retry/circuit-breaker/fallback are *reactive* (react to a fault); timeout/bulkhead/rate-limit are *proactive* (impose a constraint regardless of outcome) |

## A Retry Policy

```csharp
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)));
    // 2s, 4s, 8s between attempts

var result = await retryPolicy.ExecuteAsync(() => httpClient.GetAsync("https://payment-service/charge"));
```

## A Circuit Breaker

```csharp
var circuitBreakerPolicy = Policy
    .Handle<HttpRequestException>()
    .CircuitBreakerAsync(
        handledEventsAllowedBeforeBreaking: 5,
        durationOfBreak: TimeSpan.FromSeconds(30));

await circuitBreakerPolicy.ExecuteAsync(() => httpClient.GetAsync("https://payment-service/charge"));
```

## Combining Policies (PolicyWrap)

```csharp
var timeoutPolicy = Policy.TimeoutAsync(TimeSpan.FromSeconds(2));

var combinedPolicy = Policy.WrapAsync(circuitBreakerPolicy, retryPolicy, timeoutPolicy);

await combinedPolicy.ExecuteAsync(() => httpClient.GetAsync("https://payment-service/charge"));
```

Execution order flows outside-in as written: the circuit breaker wraps the retry, which wraps the timeout — each individual call attempt is time-limited, failed attempts are retried, and sustained failure across retries trips the circuit breaker.

## Integration with HttpClientFactory

```csharp
services.AddHttpClient("PaymentService")
    .AddPolicyHandler(retryPolicy)
    .AddPolicyHandler(circuitBreakerPolicy);
```

Wiring policies directly into `HttpClientFactory` applies them to every request made through that named client, without wrapping each call site manually.

## Common Questions

**Is Polly conceptually the same as [Resilience4j](resilience4j.md)?**
> Yes — same category of tool (composable resilience policies), same core patterns, just idiomatic to .NET rather than the JVM. If moving between a Java and .NET microservices codebase, the mental model transfers directly even though the API surface differs.

**Does using Polly remove the need for a service mesh's retry/circuit-breaking features?**
> Not necessarily — a service mesh (see [Mesh Architecture](../../distributed-systems/patterns/mesh-architecture.md)) applies these patterns uniformly at the network layer without application code changes, which is valuable across many services in many languages. Polly applies them explicitly in .NET application code, giving finer-grained, request-aware control (e.g. different retry policies per endpoint) than a mesh's more uniform defaults.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Resilience4j](resilience4j.md)
- [Hystrix](hystrix.md)
- [Mesh Architecture](../../distributed-systems/patterns/mesh-architecture.md)
- [Exponential Backoff and Jitter](exponential-backoff-and-jitter.md) — the retry algorithm this library's retry policies implement
