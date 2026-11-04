# Middleware

In [NestJS](https://nestjs.com/), middleware executes logic before a request reaches the controller. It sits early in the request pipeline.

## Request Flow

```text
Request
   ↓
Middleware
   ↓
Guards
   ↓
Interceptors
   ↓
Controller
   ↓
Service
```

## What Middleware Is Used For

Common uses:

- logging
- [authentication](../security/auth/authentication.md) preprocessing (e.g. extracting a token)
- request modification
- headers
- [CORS](../security/attacks/cors.md)
- [rate limiting](architecture/rate-limiting.md)
- request timing
- correlation IDs
- compression
- security headers

### Analogy

Think of airport security:

```text
Passenger → Security Check → Airport Gate
```

Middleware checks requests before they continue.

## Basic Middleware Example

```typescript
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {

  use(req: Request, res: Response, next: NextFunction) {
    console.log('Request received');
    next();
  }

}
```

`next()` **must** be called, or the request hangs forever — this is the most common mistake with middleware.

## Applying Middleware

Middleware is applied inside a module:

```typescript
import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';

@Module({})
export class AppModule implements NestModule {

  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware)
      .forRoutes('*');
  }

}
```

`.forRoutes('*')` runs the middleware for all routes.

### Specific and Multiple Routes

```typescript
consumer.apply(LoggerMiddleware).forRoutes('users');
consumer.apply(LoggerMiddleware).forRoutes('users', 'products');
```

### Excluding Routes

```typescript
consumer
  .apply(LoggerMiddleware)
  .exclude('auth/login')
  .forRoutes('*');
```

### Route-Specific Middleware (Method + Path)

```typescript
consumer
  .apply(AuthMiddleware)
  .forRoutes({
    path: 'users',
    method: RequestMethod.GET,
  });
```

### Global Middleware

Applied everywhere, usually registered in `main.ts` or `AppModule`.

## Functional Middleware

A simpler syntax for stateless middleware:

```typescript
export function logger(req, res, next) {
  console.log('Request');
  next();
}
```

## Async Middleware

```typescript
async use(req, res, next) {
  await someOperation();
  next();
}
```

## Middleware vs Guards

| Middleware | Guard |
|---|---|
| Preprocessing | [Authorization](../security/authorization/authorization.md) |
| Express-style | NestJS-specific |
| Can modify req/res | Decides access |
| Runs earlier | Runs later |
| Generic request logic | Route-aware |
| Cannot easily use decorators | Works with decorators |

Middleware is used for generic preprocessing (logging, request modification) and runs *before* guards. [Guards](nestjs/guards.md) are used for [authorization](../security/authorization/authorization.md), access control, and [authentication](../security/auth/authentication.md) decisions (`CanActivate`) and are route-aware. See [Guards](nestjs/guards.md) for the full comparison.

## Middleware vs Interceptors

| Middleware | Interceptor |
|---|---|
| Before request only | Before + after |
| Express-level | NestJS-level |
| Cannot access handler result easily | Can transform response |

## Middleware Order

```text
Middleware
↓
Guards
↓
Interceptors
↓
Pipes
↓
Controller
```

## Middleware Is Not an Authentication System

A very important distinction: middleware can **help** [authentication](../security/auth/authentication.md) (e.g. by parsing a token) but should not implement the entire auth architecture.

```text
Middleware ≠ Authentication System
```

**Correct architecture:**

```text
Middleware  → parse token
Guard       → verify access
AuthService → authentication business logic (validate, generate token, hash password)
```

**Full flow:**

```text
Request
   ↓
Middleware   (extract token, attach request metadata)
   ↓
Guard        (decide: can this request continue?)
   ↓
Controller
   ↓
Service
```

Example middleware step:

```typescript
use(req, res, next) {
  const token = req.headers.authorization;
  req.token = token;
  next();
}
```

Example guard step:

```typescript
canActivate(context: ExecutionContext) {
  const request = context.switchToHttp().getRequest();
  return validateToken(request.token);
}
```

Example service responsibilities:

```typescript
validateUser()
generateToken()
hashPassword()
```

### What Middleware Should NOT Do

Avoid putting [authorization](../security/authorization/authorization.md) decisions, role checks, or business auth logic inside middleware, because it:

- runs too early in the pipeline
- is generic and not route-aware
- is not integrated with NestJS's auth/[DI](../programming/fundamentals/dependency-injection.md) system for decorators and metadata

A common junior mistake is writing `if (!token) return unauthorized;` inside middleware — instead, middleware should parse and guards should authorize.

### Example Real Architecture

```text
AuthModule
 ├── AuthController
 ├── AuthService
 ├── JwtStrategy
 ├── JwtGuard
 └── RolesGuard
```

Middleware may still exist separately for logging, request tracking, or token extraction.

| Middleware | Auth Module |
|---|---|
| Preprocessing | Full [authentication](../security/auth/authentication.md) system |
| Generic request logic | Auth business logic |
| Optional | Essential |
| Extracts token | Validates token |
| Runs early | Full auth architecture |

## Common Questions

**Q: What is middleware?**
A function or class executed before route handlers, commonly used for logging, request preprocessing, [authentication](../security/auth/authentication.md) parsing, and request manipulation.

**Q: Why use middleware?**
It centralizes common request logic, preprocessing, and request transformations.

**Q: Difference between middleware and guards?**
Middleware preprocesses requests; guards determine access permissions.

**Q: What happens if `next()` is not called?**
The request hangs indefinitely.

**Q: Can middleware access the response?**
Yes — it has access to `req`, `res`, and `next`.

**Q: Why not use middleware for [authorization](../security/authorization/authorization.md)?**
Middleware is intended for generic request preprocessing, while guards are specifically designed for [authorization](../security/authorization/authorization.md) and access control because they are aware of route context and execution metadata.

**Senior-level answer:** Middleware in NestJS is executed before route handlers and is primarily used for request preprocessing such as logging, header manipulation, token parsing, and request transformation. It operates at the framework level and integrates with Express/Fastify middleware pipelines. [Authentication](../security/auth/authentication.md) and [authorization](../security/authorization/authorization.md) should primarily be handled through dedicated auth modules, strategies, and guards, since guards are integrated into NestJS's execution context and routing system.

> Easy way to remember: **Middleware prepares the request. Guard protects the route. AuthService manages [authentication](../security/auth/authentication.md).**

## Related

- [NestJS Overview](nestjs/nestjs-overview.md)
- [Guards](nestjs/guards.md)
- [Controllers](nestjs/controllers.md)
