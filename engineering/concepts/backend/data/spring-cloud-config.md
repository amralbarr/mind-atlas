# Spring Cloud Config

Spring Cloud Config is a centralized configuration server for Spring-based microservices — instead of each service carrying its own environment-specific `application.yml` baked into its deployment artifact, services fetch their config at startup (and optionally on refresh) from a Config Server backed by a Git repository, so config changes and audit history live in version control.

## Core Concepts

| Term | Meaning |
|---|---|
| **Config Server** | The [Spring Boot](../../programming/java/spring-boot.md) application exposing configuration over [HTTP](../../networking/http.md), backed by a Git repo (or filesystem, Vault, JDBC) |
| **Config Client** | A dependency each service includes to fetch its config from the Config Server at startup |
| **Profile** | An environment name (`dev`, `staging`, `prod`) — the Config Server resolves `{application}-{profile}.yml` to return environment-specific values |
| **`/actuator/refresh`** | An endpoint a client exposes to re-fetch config from the server at runtime, without restarting the service (for `@RefreshScope`-annotated beans) |
| **Git-backed config repo** | The actual source of truth — a separate Git repository holding one [YAML](../../devops/yaml.md)/properties file per service (and per environment), giving config changes the same review/audit trail as code |

## Running a Config Server

```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

```yaml
# application.yml (Config Server)
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/org/config-repo
```

## Client Configuration

```yaml
# bootstrap.yml (orders-service)
spring:
  application:
    name: orders-service
  cloud:
    config:
      uri: http://config-server:8888
      profile: prod
```

On startup, `orders-service` fetches `orders-service-prod.yml` from the Config Server, which reads it from `config-repo`'s corresponding file — the service itself never needs prod-specific values baked into its own repo or image.

## Refreshing Config at Runtime

```java
@RefreshScope
@RestController
public class FeatureController {
    @Value("${feature.new-checkout.enabled}")
    private boolean newCheckoutEnabled;
}
```

```bash
curl -X POST http://orders-service:8080/actuator/refresh
```

`@RefreshScope` beans are recreated with the latest values on the next access after a refresh call — a feature flag or tunable can change without a redeploy.

## Common Questions

**Does this replace the need for a secrets manager?**
> No — Spring Cloud Config is designed for non-sensitive, environment-specific config (URLs, feature flags, timeouts). For actual secrets (API keys, DB passwords), it's commonly backed by or paired with Vault/[OpenBao](../../security/secrets/openbao.md) rather than storing plaintext secrets in the Git config repo — see [Secrets Management](../security/secrets/secrets-management.md).

**Is this Spring-specific, or does it generalize to other stacks?**
> The pattern (centralized, Git-backed, environment-aware config with runtime refresh) generalizes, but Spring Cloud Config itself is JVM/Spring-specific. [Kubernetes](../../distributed-systems/kubernetes/ingress.md)-native systems commonly reach for ConfigMaps plus GitOps tooling like [Argo CD](../../distributed-systems/kubernetes/argo-cd.md) to achieve a similar Git-as-source-of-truth outcome without being tied to Spring.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Consul](../service-discovery/consul.md)
- [Secrets Management](../security/secrets/secrets-management.md)
- [Argo CD](../../distributed-systems/kubernetes/argo-cd.md)
- [curl Commands](../../../commands/curl.md)
