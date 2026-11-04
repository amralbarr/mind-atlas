# Eureka

Netflix Eureka is a service registry built for client-side [service discovery](../../../overviews/backend/microservices-tech-stack.md#service-discovery) — services register themselves with a Eureka server on startup, and calling services fetch the registry (cached locally, refreshed periodically) to pick an instance themselves, rather than asking a central load balancer to route every request. It's the historical default in Spring Cloud stacks.

## Core Concepts

| Term | Meaning |
|---|---|
| **Eureka Server** | The registry itself — holds the current list of registered service instances and their health status |
| **Eureka Client** | Embedded in each service — registers on startup, sends periodic heartbeats, and fetches the registry to discover other services |
| **Heartbeat / lease renewal** | A client must renew its registration periodically (default every 30s); missing several renewals gets it evicted from the registry |
| **Client-side discovery** | The calling client resolves an instance itself (using a cached registry + a load-balancing library like Spring Cloud LoadBalancer), rather than a proxy doing it centrally — the defining trait that distinguishes this from server-side discovery |
| **Self-preservation mode** | If Eureka loses too many heartbeats too quickly (often signaling a network partition, not real instance failures), it stops evicting instances to avoid mass false-positive deregistration |

## Running a Eureka Server (Spring Boot)

```java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
```

```yaml
# application.yml
server:
  port: 8761
eureka:
  client:
    register-with-eureka: false   # the server itself doesn't need to register
    fetch-registry: false
```

## Registering a Client Service

```yaml
# orders-service application.yml
spring:
  application:
    name: orders-service
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

```java
@SpringBootApplication
@EnableDiscoveryClient
public class OrdersServiceApplication { ... }
```

## Calling Another Service by Name

```java
@Autowired
private RestTemplate restTemplate; // annotated with @LoadBalanced elsewhere

public Order getOrder(String id) {
    // "orders-service" is resolved via Eureka + client-side load balancing, not a hardcoded host
    return restTemplate.getForObject("http://orders-service/orders/" + id, Order.class);
}
```

## Common Questions

**Is Eureka still the recommended choice for new Spring Cloud systems?**
> It's still supported and common in existing Spring Cloud stacks, but new systems — especially anything deployed on [Kubernetes](../../distributed-systems/kubernetes/ingress.md) — increasingly rely on [Kubernetes](../../distributed-systems/kubernetes/ingress.md)' own built-in Service/[DNS](../../networking/dns.md) discovery instead, since it removes a separate component to run entirely. See [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md).

**Client-side vs. server-side discovery — why does it matter which Eureka uses?**
> With client-side discovery, load-balancing logic lives in every calling service (via a library), which avoids a central discovery-proxy hop but means every client language/runtime needs a compatible client library. Server-side discovery (e.g. a [Kubernetes](../../distributed-systems/kubernetes/ingress.md) Service, or a gateway doing the resolving) centralizes that logic instead — see [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#service-discovery) for the full comparison.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Consul](consul.md)
- [Spring Cloud Gateway](../api-gateways/spring-cloud-gateway.md)
- [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md)
