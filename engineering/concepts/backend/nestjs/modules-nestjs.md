# NestJS Modules

Modules are one of the most important concepts in [NestJS](https://nestjs.com/) — they're foundational to understanding the framework.

## What Is a Module?

A module is a way to organize related parts of an application into a single unit. It groups [controllers](controllers.md), services, providers, imports, and exports.

## Why Modules Exist

Without modules, everything becomes messy and large applications become difficult to maintain. Modules provide:

- separation of concerns
- scalability
- encapsulation
- reusability

### Analogy

Think of a hospital where each department is separate:

```text
Cardiology Module
Radiology Module
Emergency Module
```

Each has its own staff and equipment, but departments can still communicate. That's exactly how NestJS modules work.

## Basic Module Example

```typescript
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';

@Module({
  controllers: [UsersController],
  providers: [UsersService],
})
export class UsersModule {}
```

## Main Parts of a Module

### 1) Controllers

Handle incoming requests — see [Controllers](controllers.md).

```typescript
controllers: [UsersController]
```

### 2) Providers

Usually services, managed by [dependency injection](../../programming/fundamentals/dependency-injection.md) — see [Providers](providers.md).

```typescript
providers: [UsersService]
```

### 3) Imports

Import other modules to use their exported providers:

```typescript
imports: [AuthModule]
```

### 4) Exports

Make providers available to other modules:

```typescript
exports: [UsersService]
```

### Full Visualization

```text
UsersModule
 ├── UsersController
 ├── UsersService
 ├── Imports AuthModule
 └── Exports UsersService
```

## The Root Module (AppModule)

Every NestJS app starts with a root module:

```typescript
@Module({
  imports: [UsersModule],
})
export class AppModule {}
```

### Folder Structure Example

```text
src/
 ├── app.module.ts
 ├── users/
 │    ├── users.module.ts
 │    ├── users.controller.ts
 │    └── users.service.ts
```

This structure scales well for larger applications.

## Feature Modules

Most applications use feature-based modules:

```text
AuthModule
UsersModule
ProductsModule
OrdersModule
PaymentsModule
```

Each feature is isolated, which lets large teams work independently without conflicts (e.g. Team A owns `AuthModule`, Team B owns `PaymentsModule`).

## Shared Modules

Some modules are reused everywhere, e.g. `DatabaseModule`, `ConfigModule`, `LoggerModule`:

```typescript
@Module({
  providers: [LoggerService],
  exports: [LoggerService],
})
export class LoggerModule {}
```

Any module can then import it:

```typescript
@Module({
  imports: [LoggerModule],
})
export class UsersModule {}
```

## Exporting Providers

If a provider is not listed in `exports`, other modules cannot access it.

## Global Modules

Some modules should be available everywhere without repeated imports:

```typescript
@Global()
@Module({
  providers: [ConfigService],
  exports: [ConfigService],
})
export class ConfigModule {}
```

## Dynamic Modules

Modules created dynamically at runtime — common for database configs, [authentication](../../security/auth/authentication.md), and external libraries:

```typescript
ConfigModule.forRoot()
```

Example implementation:

```typescript
@Module({})
export class DatabaseModule {
  static forRoot(options): DynamicModule {
    return {
      module: DatabaseModule,
      providers: [
        {
          provide: 'DB_OPTIONS',
          useValue: options,
        },
      ],
    };
  }
}
```

## Module Encapsulation

Modules encapsulate providers internally: providers are private by default, and only exported providers are public. This is an important architectural principle.

## Example: Applied to a Real System

A telemetry/agents backend naturally fits modular design:

```text
TelemetryModule
SignalsModule
RealtimeModule
HistorianModule
IngestionModule
AgentsModule
AuthModule
```

## Common Questions

**Q: Why use modules?**
Modules organize related functionality into isolated, reusable units, improving scalability, maintainability, and separation of concerns in large applications.

**Q: Difference between imports and exports?**

| Keyword | Purpose |
|---|---|
| imports | use another module |
| exports | expose providers to other modules |

**Q: What happens if a service is not exported?**
Other modules cannot inject it — you get a `Nest can't resolve dependencies` error.

**Senior-level answer:** NestJS modules are organizational units that encapsulate related [controllers](controllers.md), providers, and services. They enable scalable feature-based architecture, dependency isolation, and reusable functionality through imports and exports.

> Easy way to remember: **Module = feature container.**

## Related

- [NestJS Overview](nestjs-overview.md)
- [Providers](providers.md)
- [Services](services.md)
- [Controllers](controllers.md)
