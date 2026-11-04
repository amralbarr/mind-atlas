# Services

In [NestJS](https://nestjs.com/), services handle business logic and application functionality. They are the core logic layer of the application.

## Request Flow

```text
Client Request
     ↓
Controller
     ↓
Service
     ↓
Database / External APIs / Logic
```

## What Is a Service?

A service is usually reusable, injectable, independent, and focused on logic. Services should contain:

- business rules
- database operations
- calculations
- external API communication
- reusable functionality

### Analogy

```text
Customer → Waiter → Chef
```

- Controller = Waiter (receives requests)
- Service = Chef (does the actual work)

## Basic Service Example

```typescript
import { Injectable } from '@nestjs/common';

@Injectable()
export class UsersService {

  findAll() {
    return ['Amr', 'Ali'];
  }

}
```

`@Injectable()` tells NestJS that this class can be managed by [dependency injection](../../programming/fundamentals/dependency-injection.md) — NestJS can create an instance, inject it elsewhere, and manage its lifecycle. See [Dependency Injection](../../programming/fundamentals/dependency-injection.md).

## Using a Service in a Controller

```typescript
@Controller('users')
export class UsersController {

  constructor(private usersService: UsersService) {}

  @Get()
  getUsers() {
    return this.usersService.findAll();
  }

}
```

## Why Services Are Important

Without services, [controllers](controllers.md) become huge and messy. Services create clean architecture, reusable logic, and separation of concerns:

```text
Controller → handles request
Service    → handles logic
```

**Bad practice:**

```typescript
@Get()
async getUsers() {
  const users = await prisma.user.findMany();
  // huge logic here ❌
}
```

**Better:**

```typescript
@Get()
getUsers() {
  return this.usersService.getUsers();
}
```

## Database Logic in Services

A very common pattern — services typically wrap [ORM](../data/orm.md)/database calls (see [ORM](../data/orm.md)):

```typescript
@Injectable()
export class UsersService {

  async getUsers() {
    return await this.prisma.user.findMany();
  }

}
```

## Services Can Call Other Services

```typescript
@Injectable()
export class OrdersService {

  constructor(
    private paymentService: PaymentService
  ) {}

}
```

This is [dependency injection](../../programming/fundamentals/dependency-injection.md) in action.

## Reusable Logic

Services allow logic reuse across [controllers](controllers.md), modules, jobs, and gateways:

```typescript
validateUser()
calculatePrice()
sendEmail()
generateToken()
```

## Singleton Behavior

By default, services are singletons — one shared instance reused everywhere. This is efficient for database connections, caches, and configuration objects.

## Async Services

Most services are async:

```typescript
@Injectable()
export class UsersService {

  async findAll() {
    return await this.database.findMany();
  }

}
```

## Services and External APIs

Services often communicate with databases, AI APIs, payment gateways, or other microservices:

```typescript
@Injectable()
export class WeatherService {

  async getWeather(city: string) {
    return await axios.get(...);
  }

}
```

## Registering and Exporting Services

Services must be registered as providers inside a module:

```typescript
@Module({
  providers: [UsersService],
})
export class UsersModule {}
```

To use a service in another module, export it:

```typescript
exports: [UsersService]
```

See [NestJS Modules](modules-nestjs.md) for the full imports/exports model.

## Testing Services

Services are easy to test because of [dependency injection](../../programming/fundamentals/dependency-injection.md):

```typescript
const module = await Test.createTestingModule({
  providers: [UsersService],
}).compile();
```

## Common Service Types

| Service Type | Purpose |
|---|---|
| UserService | user logic |
| AuthService | [authentication](../../security/auth/authentication.md) |
| EmailService | send emails |
| PaymentService | payment processing |
| CacheService | caching |
| LoggerService | logging |

## Service vs Controller

| Controller | Service |
|---|---|
| Handles [HTTP](../../networking/http.md) requests | Handles logic |
| Thin layer | Core functionality |
| Route management | Business rules |

## Common Questions

**Q: What is a service in NestJS?**
A service is a provider responsible for handling business logic, reusable functionality, and communication with databases or external systems.

**Q: Why use services?**
They separate concerns, improve maintainability, allow reuse, and simplify testing.

**Q: Should [controllers](controllers.md) contain business logic?**
No — business logic belongs in services.

**Q: Why use `@Injectable()`?**
It enables the NestJS [dependency injection](../../programming/fundamentals/dependency-injection.md) system to manage the class.

**Q: Are services singletons?**
Yes, by default.

**Senior-level answer:** Services in NestJS encapsulate business logic and reusable application functionality. They are injectable providers managed by NestJS's [dependency injection](../../programming/fundamentals/dependency-injection.md) container and help maintain clean separation of concerns between API handling and core logic.

> Easy way to remember: **Controller = receives request. Service = does the work.**

## Related

- [NestJS Overview](nestjs-overview.md)
- [Providers](providers.md)
- [ORM](../data/orm.md)
- [Dependency Injection](../../programming/fundamentals/dependency-injection.md)
- [Interface vs Type](../../programming/typescript/interface-vs-type.md)
