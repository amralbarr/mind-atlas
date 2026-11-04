# Spring Cloud Gateway

Spring Cloud Gateway is the JVM-ecosystem-native [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway) for Spring-based microservices — built on Spring's reactive stack (Spring WebFlux/Project Reactor), and typically the default choice when the rest of a system is already [Spring Boot](../../programming/java/spring-boot.md), so routing config, filters, and service discovery integration all live in the same framework and configuration style as the services themselves.

## Core Concepts

| Term | Meaning |
|---|---|
| **Route** | An ID, a destination URI, and a set of predicates/filters — the core routing unit |
| **Predicate** | A condition a request must match for a route to apply (path, header, method, host) |
| **Filter** | Modifies a request/response as it passes through — add headers, rewrite paths, apply [rate limiting](../architecture/rate-limiting.md), circuit-break a downstream call |
| **Gateway Handler Mapping** | The internal component matching incoming requests to a route based on its predicates |

## Route Configuration (application.yml)

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: orders-route
          uri: lb://orders-service          # lb:// resolves via service discovery
          predicates:
            - Path=/orders/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
```

`lb://orders-service` resolves `orders-service` through whatever [service discovery](../../../overviews/backend/microservices-tech-stack.md#service-discovery) mechanism is configured (commonly [Eureka](../service-discovery/eureka.md) in a Spring Cloud stack) rather than a hardcoded host — the gateway picks a live instance at request time.

## Programmatic Route Definition (Java)

```java
@Bean
public RouteLocator customRoutes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("orders-route", r -> r.path("/orders/**")
            .filters(f -> f.stripPrefix(1)
                .circuitBreaker(c -> c.setName("ordersCB")))
            .uri("lb://orders-service"))
        .build();
}
```

The `circuitBreaker` filter here wires the gateway route directly to a [Resilience4j](../resilience/resilience4j.md) circuit breaker — failing fast on a struggling downstream service without every calling client needing its own retry/breaker logic.

## Common Questions

**Why would a Spring shop choose this over [Kong](kong.md) or [NGINX](nginx.md)?**
> Configuration, filters, and observability all live in the same [Spring Boot](../../programming/java/spring-boot.md) idioms as the rest of the system ([YAML](../../devops/yaml.md) config, Spring beans, Micrometer metrics) — no separate gateway product/language (Lua for [Kong](kong.md), a proxy DSL for [NGINX](nginx.md)) to operate alongside the JVM services it's routing to.

**Is this the same thing as Netflix Zuul?**
> No, though they solve the same role — Zuul was Netflix's earlier Spring Cloud gateway, now effectively superseded by Spring Cloud Gateway, which is built on the newer reactive (WebFlux) stack rather than Zuul's older blocking servlet model.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Eureka](../service-discovery/eureka.md)
- [Resilience4j](../resilience/resilience4j.md)
- [Kong](kong.md)
