# Dependency Injection (DI)

Dependency Injection (DI) is one of the most important backend concepts, especially for frameworks that build on it directly: [NestJS](https://nestjs.com/), [Spring Boot](../java/spring-boot.md), [Angular](../../frontend/angular.md), and ASP.NET.

## Simple Definition

> Dependency Injection means giving a class the dependencies it needs from the outside instead of creating them internally.

**Not to be confused with the [Dependency Inversion Principle (DIP)](dependency-inversion-principle.md)** — DI is a *technique* for wiring dependencies; [DIP](dependency-inversion-principle.md) is the SOLID *design principle* (depend on abstractions, not concrete implementations) that DI is commonly, but not exclusively, used to satisfy. See [Dependency Inversion Principle](dependency-inversion-principle.md) for the full distinction.

A **dependency** is simply something a class needs in order to work:

```typescript
class UserService {
  constructor(private db: DatabaseService) {}
}
```

Here, `DatabaseService` is a dependency of `UserService`.

## Without Dependency Injection

```typescript
class UserService {
  private db = new DatabaseService();

  getUsers() {
    return this.db.findAll();
  }
}
```

This is tightly coupled: it's hard to test, hard to swap out the database implementation, and scales poorly as the class graph grows.

## With Dependency Injection

```typescript
class UserService {
  constructor(private db: DatabaseService) {}

  getUsers() {
    return this.db.findAll();
  }
}
```

Now the dependency is provided from outside — the class is flexible, easier to test, and loosely coupled.

## Real-World Analogy

Without DI, a car builds its own engine — very inflexible. With DI, the engine is provided to the car, so you can swap in a diesel engine, an electric engine, or a test engine without changing the car itself.

## Why DI Matters

1. **Loose coupling** — classes are independent and implementations can be replaced easily.
2. **Easier testing** — you can inject mock services instead of real ones:
   ```typescript
   const mockDb = {
     findAll: jest.fn(),
   };
   ```
3. **Better scalability** — large applications stay manageable as they grow.
4. **Reusability** — services can be shared cleanly across modules.

## Dependency Injection in NestJS

NestJS ships with a built-in **[IoC](inversion-of-control.md) container** that automatically creates services, manages their lifecycle, and injects dependencies where they're needed.

```typescript
@Injectable()
export class DatabaseService {
  findAll() {
    return ['user1', 'user2'];
  }
}

@Injectable()
export class UserService {
  constructor(private db: DatabaseService) {}

  getUsers() {
    return this.db.findAll();
  }
}
```

NestJS automatically injects `DatabaseService` into `UserService` once both are registered as providers:

```typescript
@Module({
  providers: [DatabaseService, UserService],
})
export class UserModule {}
```

### How NestJS DI Works Internally

1. NestJS scans the module's `providers` array.
2. It creates instances of each provider ([singleton](../design-patterns/singleton.md) by default).
3. It inspects each class's constructor for dependencies.
4. It injects the matching instance automatically.

```text
NestJS Container
     │
     ├── DatabaseService instance
     │
     └── injects into UserService
```

### Provider Scope

By default, NestJS providers are **singletons** — one instance shared everywhere, which is efficient for things like database services, caches, and configuration. See [Provider Scope](provider-scope.md) for the full three-tier breakdown ([Singleton](../design-patterns/singleton.md)/Request/Transient), why [Singleton](../design-patterns/singleton.md) is the default across every DI framework, and the same concept under different names in [Spring Boot](../java/spring-boot.md) and [ASP.NET Core](../csharp/asp-net.md).

### Custom and Factory Providers

You can inject arbitrary values, not just classes:

```typescript
{
  provide: 'API_KEY',
  useValue: '123'
}
```

```typescript
@Inject('API_KEY')
private apiKey: string
```

Factory providers are useful for configuration and dynamic initialization, such as database connections:

```typescript
{
  provide: 'CONFIG',
  useFactory: () => {
    return loadConfig();
  }
}
```

## DI vs. IoC

These two terms are often confused: **[IoC](inversion-of-control.md) (Inversion of Control)** is the general principle that a framework, not your own code, controls object creation and execution flow; DI is one specific, common implementation of [IoC](inversion-of-control.md), focused on dependency creation. See [Inversion of Control](inversion-of-control.md) for the full distinction and other [IoC](inversion-of-control.md) implementations beyond DI.

## Testing Example

Without DI, `new DatabaseService()` is hard to mock. With DI, you simply substitute the injected dependency:

```typescript
const mockDb = {
  findAll: jest.fn(),
};
```

This makes unit testing straightforward, since the class under test never constructs its own dependencies.

## Where DI Pays Off in Practice

In real backend systems, DI is especially useful for wiring together services that need to communicate cleanly without hard dependencies on each other's concrete implementations — for example: caching/Redis services, WebSocket gateways, message brokers, background job or snapshot services, third-party integrations (e.g. Firebase listeners), and historical/audit data modules.

## Common Questions

**What problem does DI solve?**
> Dependency Injection reduces tight coupling between classes by externalizing dependency creation and management, improving scalability, maintainability, and testability.

**Senior-level answer:**
> Dependency Injection is a design pattern where dependencies are provided externally rather than instantiated internally. In NestJS, the [IoC](inversion-of-control.md) container manages provider creation and lifecycle, enabling loose coupling, easier testing, modularity, and scalable architecture.

**Easy way to remember:** Without DI, a class creates its own dependencies. With DI, the framework provides them.

## Related

- [NestJS Overview](../../backend/nestjs/nestjs-overview.md), [Spring Boot](../java/spring-boot.md), [ASP.NET Core](../csharp/asp-net.md), [Angular](../../frontend/angular.md) — the four frameworks in this handbook built around constructor-based DI as a first-class feature
- [Dependency Inversion Principle (DIP)](dependency-inversion-principle.md) — the SOLID design principle DI is a common technique for satisfying; not the same thing
- [Inversion of Control (IoC)](inversion-of-control.md) — the broader principle DI is one implementation of
- [Provider Scope](provider-scope.md) — how long an injected instance lives ([Singleton](../design-patterns/singleton.md)/Request/Transient)
- [Object-Oriented Programming (OOP)](oop.md)
- [Abstraction](abstraction.md)
- [interface vs type](../typescript/interface-vs-type.md)
- [Singleton Pattern](../design-patterns/singleton.md) — DI is what replaces most manual [Singleton](../design-patterns/singleton.md) usage in practice
- [Factory Pattern](../design-patterns/factory.md) — NestJS's `useFactory` providers are the [Factory pattern](../design-patterns/factory.md) applied to DI
