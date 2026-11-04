# Spring Boot

Spring Boot is Java's dominant full-stack web framework — [dependency injection](../fundamentals/dependency-injection.md), an embedded web server (Tomcat by default), auto-configuration, and a convention-over-configuration philosophy that removes most of the XML/boilerplate the older plain Spring Framework required. It sits on top of the broader Spring ecosystem (Spring Framework, Spring Data, Spring Security, Spring Cloud), pulling in exactly the pieces a given application needs via "starter" dependencies, and is the closest Java equivalent to what [NestJS](../../backend/nestjs/nestjs-overview.md) is for TypeScript — both are heavily annotation/decorator-driven, dependency-injection-first frameworks built for structured, enterprise-scale backends.

## Core Concepts

| Term | Meaning |
|---|---|
| **`@SpringBootApplication`** | The single annotation combining auto-configuration, component scanning, and configuration — marks the application's entry-point class |
| **Bean** | An object managed by Spring's [dependency injection](../fundamentals/dependency-injection.md) container (the "[IoC](../fundamentals/inversion-of-control.md) container") — created once, injected wherever needed, instead of constructed manually |
| **`@Component` / `@Service` / `@Repository`** | Annotations marking a class as a bean Spring should manage; `@Service` and `@Repository` are semantic aliases for `@Component` used by convention for business-logic and data-access classes respectively |
| **`@Autowired`** | Injects a bean into a field, constructor, or setter — constructor injection is the modern recommended style, since it makes a class's required dependencies explicit and testable |
| **`@RestController`** | Marks a class as an [HTTP](../../networking/http.md) API controller whose methods return data directly (serialized to [JSON](../fundamentals/json.md)) rather than a view/template name |
| **`@RequestMapping` / `@GetMapping` / `@PostMapping`** | Maps an [HTTP](../../networking/http.md) route + method to a controller method |
| **Starter** | A curated dependency bundle (`spring-boot-starter-web`, `spring-boot-starter-data-jpa`) that pulls in everything needed for one capability with sensible default versions |
| **Spring Data JPA** | Spring's [ORM](../../backend/data/orm.md) layer, built on Hibernate — define a `Repository` interface and Spring generates the implementation (CRUD methods, query derivation from method names) automatically |

## A Minimal REST Controller

```java
@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    // Constructor injection -- Spring automatically supplies UserService
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    public User createUser(@RequestBody @Valid CreateUserRequest request) {
        return userService.create(request);
    }
}
```

`@Valid` on `@RequestBody` triggers [Bean Validation](../fundamentals/data-validation.md) (`@NotNull`, `@Email`, `@Size`, etc. on the request [DTO](../../backend/api/dto.md) class) before the method body ever runs — the direct Java equivalent of [class-validator](../../backend/api/class-validator.md)'s decorator-based validation in NestJS, or [Pydantic](../python/pydantic.md) in [FastAPI](../python/fastapi.md).

## Spring Data JPA — The ORM Layer

```java
@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String email;
}

// No implementation needed -- Spring generates it from the interface + method name
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    List<User> findByNameContaining(String namePart);
}
```

Calling `userRepository.findByEmail("amr@example.com")` works with **zero hand-written [SQL](../../databases/relational/sql.md) or implementation code** — Spring Data derives the query from the method name itself. This convenience is also the classic source of an accidental [N+1 query problem](../../backend/data/n-plus-1-problem.md): an entity's `@OneToMany` relationship is lazy-loaded by default, so iterating a list of parents and accessing each one's children triggers one query per parent unless you explicitly use `@EntityGraph` or a `JOIN FETCH` query to eager-load it.

## Spring Boot vs. NestJS vs. Django

| | Spring Boot | [NestJS](../../backend/nestjs/nestjs-overview.md) | [Django](../python/django.md) |
|---|---|---|---|
| Language | Java / Kotlin | TypeScript | Python |
| [DI](../fundamentals/dependency-injection.md) style | Constructor injection, `@Autowired` | Constructor injection, `@Injectable()` | Not [DI](../fundamentals/dependency-injection.md)-based — explicit imports |
| [ORM](../../backend/data/orm.md) | Spring Data JPA (Hibernate) | TypeORM / Prisma (not built-in) | [Django](../python/django.md) [ORM](../../backend/data/orm.md) (built-in) |
| Validation | Bean Validation (`@Valid` + annotations) | [class-validator](../../backend/api/class-validator.md) | DRF serializers |
| Ecosystem maturity | Oldest, most enterprise-entrenched | Newer, Node.js ecosystem | Oldest Python option, batteries-included |

## Configuration and Profiles

```properties
# application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.jpa.hibernate.ddl-auto=update
```

Spring Boot supports environment-specific config files (`application-dev.properties`, `application-prod.properties`), activated via the `spring.profiles.active` property — the same "one config shape, environment-specific overrides" pattern as `.env` files in a Node.js project.

## Common Questions

**Why does Spring Boot favor constructor injection over field injection (`@Autowired` directly on a field)?**
> Constructor injection makes a class's dependencies explicit in its signature, allows them to be declared `final` (immutable after construction), and makes the class trivially testable without needing Spring's container at all — just call the constructor directly with test doubles.

**Is Spring Boot synchronous or async?**
> Synchronous (blocking) by default, using a thread-per-request model over the servlet API. **Spring WebFlux** is Spring's separate, fully reactive/non-blocking stack (built on Project Reactor) for high-concurrency workloads — the two are largely mutually exclusive architectural choices within one application, not a toggle.

## Related

- [NestJS Overview](../../backend/nestjs/nestjs-overview.md) — the closest TypeScript equivalent in philosophy and structure
- [Dependency Injection](../fundamentals/dependency-injection.md) — the core pattern Spring's [IoC](../fundamentals/inversion-of-control.md) container implements
- [Provider Scope](../fundamentals/provider-scope.md) — `@Scope("singleton"/"request"/"prototype")`, the same three-tier concept as NestJS/ASP.NET under different names
- [ORM](../../backend/data/orm.md) — Spring Data JPA is Spring's [ORM](../../backend/data/orm.md) layer, built on Hibernate
- [The N+1 Query Problem](../../backend/data/n-plus-1-problem.md) — a common Spring Data JPA pitfall via default lazy loading
- [Data Validation](../fundamentals/data-validation.md) — Bean Validation is Spring's implementation of the general pattern
- [REST](../../backend/api/rest.md) — the typical API style a `@RestController` exposes
- [Spring Cloud Gateway](../../backend/api-gateways/spring-cloud-gateway.md) — the Spring ecosystem's API gateway
- [Spring Cloud Config](../../backend/data/spring-cloud-config.md) — centralized configuration for Spring microservices
- [Resilience4j](../../backend/resilience/resilience4j.md) — the Spring ecosystem's circuit-breaker/resilience library
- [Eureka](../../backend/service-discovery/eureka.md) — the Spring Cloud service registry
