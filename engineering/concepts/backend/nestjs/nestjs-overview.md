# NestJS Overview

## What Is NestJS

NestJS is a Node.js framework for building scalable, maintainable server-side applications. It provides a scalable and maintainable backend architecture built on top of Node.js and TypeScript, using [dependency injection](../../programming/fundamentals/dependency-injection.md), modular architecture, decorators, and design patterns inspired by [Angular](../../frontend/angular.md) — making it suitable for enterprise applications and microservices.

Under the hood, NestJS runs on top of Express (the default [HTTP](../../networking/http.md) adapter) or Fastify (for higher performance), so it retains full access to the Node.js ecosystem and [middleware](../middleware.md) compatibility while adding structure on top.

## Why Use It

Compared to a raw Express app, NestJS enforces a clean, opinionated architecture instead of leaving structure entirely up to the developer.

### Structured Architecture

Raw Express gives you freedom but no structure:

```javascript
app.get(...)
app.post(...)
app.use(...)
```

NestJS instead organizes code into modules, [controllers](controllers.md), and services, e.g.:

```text
src/
 ├── users/
 │    ├── users.module.ts
 │    ├── users.controller.ts
 │    ├── users.service.ts
 │    └── dto/
```

This organization pays off for teams, scaling codebases, and enterprise systems.

### Dependency Injection

NestJS has a built-in [DI](../../programming/fundamentals/dependency-injection.md) container. [Providers](providers.md) are declared once and injected wherever needed:

```typescript
@Injectable()
export class UsersService {}
```

```typescript
constructor(private usersService: UsersService) {}
```

Benefits: loose coupling, easier testing, cleaner architecture, reusable services. See [Dependency Injection](../../programming/fundamentals/dependency-injection.md).

### TypeScript First

NestJS is built with TypeScript from the ground up, giving strong typing, autocompletion, safer refactoring, and better maintainability — important in large systems. See [Interface vs Type](../../programming/typescript/interface-vs-type.md) for TypeScript typing fundamentals that apply throughout a NestJS codebase.

### Scalable Modular Architecture

Everything is modular:

```typescript
@Module({
  imports: [],
  controllers: [],
  providers: [],
})
```

This helps with microservices, feature separation, and team scalability — see [NestJS Modules](modules-nestjs.md).

### Enterprise-Level Features Out of the Box

Built-in support for validation, [authentication](../../security/auth/authentication.md), guards, interceptors, [middleware](../middleware.md), exception filters, [WebSockets](../../networking/websockets.md), [GraphQL](../api/graphql.md), and microservices — without messy custom setup.

### Excellent for Microservices

Native support for [TCP](../../networking/tcp.md), Redis, [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md), [Kafka](../../distributed-systems/messaging/kafka.md), and [gRPC](../api/grpc.md) transports:

```typescript
ClientsModule.register([
  {
    transport: Transport.RMQ,
  },
]);
```

### Powerful Decorators

```typescript
@Controller('users')
@Get()
@Post()
@UseGuards()
```

Decorators improve readability, organization, and [abstraction](../../programming/fundamentals/abstraction.md).

### Testing Support

Strong built-in testing architecture supporting unit tests, e2e tests, and dependency mocking.

### Strong Ecosystem

Official integrations with Prisma, TypeORM, Swagger, Passport, [GraphQL](../api/graphql.md), and [BullMQ](../../distributed-systems/messaging/bullmq.md).

### Express vs NestJS

| Feature | Express | NestJS |
|---|---|---|
| Structure | Minimal | Enterprise |
| [Dependency Injection](../../programming/fundamentals/dependency-injection.md) | No | Yes |
| TypeScript | Optional | First-class |
| Scalability | Manual | Built-in |
| Architecture | Flexible/chaotic | Organized |
| Microservices | Manual | Native support |
| Testing | Manual setup | Strong support |

### Where NestJS Fits Well

NestJS is a particularly strong fit for realtime telemetry systems, WebSocket-heavy applications, Redis-backed services, AI agent orchestration, [RAG](../../ai/rag/rag.md) systems, and IoT/telemetry platforms — domains that benefit from its modular structure, [DI](../../programming/fundamentals/dependency-injection.md), and native WebSocket/microservices support.

```typescript
@WebSocketGateway()
```

## Core Architecture

NestJS applications are composed of a small set of building blocks that work together on every request:

| Building Block | Responsibility |
|---|---|
| [Modules](modules-nestjs.md) | Organize [controllers](controllers.md), providers, and services into cohesive, reusable units |
| [Controllers](controllers.md) | Handle incoming [HTTP](../../networking/http.md) requests and return responses |
| [Services](services.md) | Contain business logic and reusable application functionality |
| [Providers](providers.md) | The general injectable-dependency [abstraction](../../programming/fundamentals/abstraction.md) that services are built on |
| [Middleware](../middleware.md) | Run early in the pipeline for generic preprocessing (logging, [CORS](../../security/attacks/cors.md), token extraction) |
| [Guards](guards.md) | Decide whether a request is authorized to proceed |
| Interceptors | Transform requests/responses before and after the handler runs |
| Pipes | Validate and transform incoming data (e.g. [DTO](../api/dto.md) validation) |
| Exception filters | Catch thrown exceptions and shape the error response |

### Request Lifecycle

```text
Middleware
   ↓
Guards
   ↓
Interceptors (before)
   ↓
Pipes
   ↓
Controller
   ↓
Service
   ↓
Interceptors (after)
   ↓
Response
```

### Core Questions

- Explain [dependency injection](../../programming/fundamentals/dependency-injection.md)
- Difference between [middleware](../middleware.md) and guards
- What are interceptors?
- Explain the request lifecycle
- How does validation work (pipes)?
- Global vs scoped providers
- Circular dependencies
- Dynamic modules
- Custom decorators
- WebSocket gateways
- Microservices transport options
- [Caching strategies](../architecture/caching-strategies.md)
- [Rate limiting](../architecture/rate-limiting.md)

**Why not use Express directly?** Express is minimal and flexible, but in large-scale systems it can become difficult to maintain without enforced architecture. NestJS provides structured patterns, [dependency injection](../../programming/fundamentals/dependency-injection.md), modularity, and enterprise-level tooling while still using Express or Fastify internally.

**Senior-level answer:** NestJS enables scalable backend architecture through modular design, [dependency injection](../../programming/fundamentals/dependency-injection.md), and TypeScript-first development. It simplifies enterprise concerns like validation, [authentication](../../security/auth/authentication.md), microservices, [WebSockets](../../networking/websockets.md), and testing while maintaining flexibility through Express/Fastify compatibility.

> Easy way to remember: **Express gives freedom. NestJS gives architecture.**

## See Also — Building Block Deep Dives

- [Controllers](controllers.md)
- [Guards](guards.md)
- [Middleware](../middleware.md)
- [Providers](providers.md)
- [Services](services.md)
- [NestJS Modules](modules-nestjs.md)

## Related

- [Controllers](controllers.md)
- [Guards](guards.md)
- [Middleware](../middleware.md)
- [Providers](providers.md)
- [Services](services.md)
- [NestJS Modules](modules-nestjs.md)
- [class-validator](../api/class-validator.md) — NestJS's decorator-based [DTO](../api/dto.md) validation library, wired via `ValidationPipe`
- [Dependency Injection](../../programming/fundamentals/dependency-injection.md)
- [Spring Boot](../../programming/java/spring-boot.md) — the Java framework whose decorator/[DI](../../programming/fundamentals/dependency-injection.md) philosophy NestJS mirrors
- [Angular](../../frontend/angular.md) — the frontend framework NestJS's own design was explicitly influenced by
- [ASP.NET Core](../../programming/csharp/asp-net.md) — the C# equivalent, same [DI](../../programming/fundamentals/dependency-injection.md)-first architectural family
- [BullMQ](../../distributed-systems/messaging/bullmq.md)
