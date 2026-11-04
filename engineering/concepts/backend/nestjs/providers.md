# Providers

In [NestJS](https://nestjs.com/), a provider is any class or value that can be injected and managed by the NestJS [dependency injection](../../programming/fundamentals/dependency-injection.md) system. Providers are the foundation of NestJS architecture.

```text
Provider = injectable dependency
```

Most commonly, services are providers, but providers can also be factories, plain values, classes, configs, or repositories.

## Basic Example

```typescript
@Injectable()
export class UsersService {}
```

This service becomes a provider once registered:

```typescript
@Module({
  providers: [UsersService],
})
export class UsersModule {}
```

NestJS now creates an instance, stores it in the [DI](../../programming/fundamentals/dependency-injection.md) container, and injects it wherever needed:

```typescript
@Controller('users')
export class UsersController {
  constructor(private usersService: UsersService) {}
}
```

## Why Providers Exist

Providers solve dependency management, object creation, lifecycle handling, and loose coupling. Without them you'd manually instantiate dependencies:

```typescript
const service = new UsersService();
```

which creates tight coupling. See [Dependency Injection](../../programming/fundamentals/dependency-injection.md) for the underlying pattern.

## Types of Providers

### 1) Class Providers (most common)

```typescript
providers: [UsersService]
```

Equivalent to:

```typescript
{
  provide: UsersService,
  useClass: UsersService
}
```

### 2) Value Providers

Inject plain values:

```typescript
{
  provide: 'API_KEY',
  useValue: '123456'
}
```

Inject with:

```typescript
@Inject('API_KEY')
private apiKey: string
```

### 3) Factory Providers

Create providers dynamically — very common for configs, database setup, and environment initialization:

```typescript
{
  provide: 'CONFIG',
  useFactory: () => {
    return { port: 3000 };
  }
}
```

Async factories are also supported:

```typescript
{
  provide: 'DATABASE',
  useFactory: async () => {
    return await connectDatabase();
  }
}
```

### 4) Existing Providers

Alias an existing provider:

```typescript
{
  provide: 'LOGGER',
  useExisting: LoggerService
}
```

## Custom Provider Tokens

Providers can use class tokens, string tokens, or symbol tokens, e.g. `provide: 'CACHE_MANAGER'`.

## [Provider Scope](../../programming/fundamentals/provider-scope.md)

By default, providers are **singletons** — one instance shared everywhere. See [Provider Scope](../../programming/fundamentals/provider-scope.md) for the general concept, why [Singleton](../../programming/design-patterns/singleton.md) is the default across every [DI](../../programming/fundamentals/dependency-injection.md) framework, and the exact same three-tier idea under different names in [Spring Boot](../../programming/java/spring-boot.md) and [ASP.NET Core](../../programming/csharp/asp-net.md).

| Scope | Meaning |
|---|---|
| DEFAULT | [Singleton](../../programming/design-patterns/singleton.md) |
| REQUEST | New instance per request |
| TRANSIENT | New instance per injection |

Request scope is useful for request tracking, tenant context, or per-request state:

```typescript
@Injectable({ scope: Scope.REQUEST })
```

Transient scope creates a new instance on every injection:

```typescript
@Injectable({ scope: Scope.TRANSIENT })
```

## Provider Lifecycle

NestJS manages creation, initialization, and destruction of providers via lifecycle [hooks](../../frontend/hooks.md):

```typescript
OnModuleInit
OnModuleDestroy
```

```typescript
@Injectable()
export class DatabaseService implements OnModuleInit {
  onModuleInit() {
    console.log('Connected');
  }
}
```

## Providers vs Services

A very common source of confusion:

```text
Every service is a provider.
But not every provider is a service.
```

Example of a non-service provider:

```typescript
{
  provide: 'APP_CONFIG',
  useValue: config
}
```

This is a provider, not a service. See [Services](services.md) for the logic-layer specialization.

| Service | Provider |
|---|---|
| Business logic class | Any injectable dependency |
| Specific concept | General concept |

## Common Real Usage

Providers commonly manage database clients, Redis connections, config systems, external API clients, AI clients, loggers, and caches.

## Common Questions

**Q: What is a provider?**
A provider is an injectable dependency managed by NestJS's [dependency injection](../../programming/fundamentals/dependency-injection.md) container. Providers can be services, factories, values, or classes.

**Q: Why are providers important?**
They enable [dependency injection](../../programming/fundamentals/dependency-injection.md), reduce coupling, improve testing, and centralize object management.

**Q: What is the default [provider scope](../../programming/fundamentals/provider-scope.md)?**
[Singleton](../../programming/design-patterns/singleton.md).

**Q: Difference between service and provider?**
See the comparison table above.

**Q: What are custom providers?**
Providers manually configured using `useClass`, `useValue`, `useFactory`, or `useExisting`.

**Senior-level answer:** Providers are the core [abstraction](../../programming/fundamentals/abstraction.md) behind NestJS [dependency injection](../../programming/fundamentals/dependency-injection.md). They represent injectable dependencies managed by the [IoC](../../programming/fundamentals/inversion-of-control.md) container and can be implemented as services, values, factories, or classes with configurable lifecycle and scope management.

> Easy way to remember: **Provider = anything NestJS can inject.**

## Related

- [Provider Scope](../../programming/fundamentals/provider-scope.md) — [Singleton](../../programming/design-patterns/singleton.md)/Request/Transient in full depth, including the [Spring Boot](../../programming/java/spring-boot.md)/ASP.NET equivalents
- [NestJS Overview](nestjs-overview.md)
- [Services](services.md)
- [NestJS Modules](modules-nestjs.md)
- [Dependency Injection](../../programming/fundamentals/dependency-injection.md)
- [Interface vs Type](../../programming/typescript/interface-vs-type.md)
- [Singleton Pattern](../../programming/design-patterns/singleton.md) — the default [provider scope](../../programming/fundamentals/provider-scope.md) is [Singleton](../../programming/design-patterns/singleton.md), enforced by the [IoC](../../programming/fundamentals/inversion-of-control.md) container rather than a manual `getInstance()`
- [Factory Pattern](../../programming/design-patterns/factory.md) — `useFactory` providers are this pattern applied to [DI](../../programming/fundamentals/dependency-injection.md)
