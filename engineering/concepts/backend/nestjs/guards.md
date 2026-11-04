# Guards

Guards are classes that determine whether a request is allowed to proceed. They are mainly used for [authentication](../../security/auth/authentication.md), [authorization](../../security/authorization/authorization.md), role checking, permissions, and access control — a very important NestJS concept.

## Request Flow

```text
Request
   ↓
Middleware
   ↓
Guard
   ↓
Controller
   ↓
Service
```

A guard acts like a security gate.

### Example

A user requests `GET /admin`. The guard checks:

- Is the user logged in?
- Is the token valid?
- Does the user have the admin role?

If allowed, the request continues. If denied, the guard returns `403 Forbidden` / `401 Unauthorized`.

## Why Guards Matter

[Middleware](../middleware.md) cannot easily access route metadata. Guards integrate deeply with decorators, route handlers, and the execution context — which is why they, not [middleware](../middleware.md), are the right place for [authorization](../../security/authorization/authorization.md) decisions.

## Guard Responsibility

A guard answers one question: **can this request continue?** It returns `true`, `false`, or throws an exception.

## Basic Guard Example

```typescript
import {
  CanActivate,
  ExecutionContext,
  Injectable
} from '@nestjs/common';

@Injectable()
export class AuthGuard implements CanActivate {

  canActivate(
    context: ExecutionContext,
  ): boolean {

    const request = context
      .switchToHttp()
      .getRequest();

    return !!request.headers.authorization;
  }

}
```

Applying the guard:

```typescript
@UseGuards(AuthGuard)
@Get()
findAll() {
  return [];
}
```

Flow: request arrives → guard executes → `true` continues, `false` blocks.

## ExecutionContext

`ExecutionContext` provides access to the request, response, route handler, and class metadata:

```typescript
context.switchToHttp().getRequest();
```

## Common Guard Types

### Authentication Guard

Checks "who are you?" — e.g. [JWT](../../security/auth/jwt.md) token, session, [API key](../../security/auth/api-key.md).

### Authorization Guard

Checks "what are you allowed to do?" — e.g. admin role, permissions.

### JWT Auth Guard Example

```typescript
@Injectable()
export class JwtAuthGuard
  implements CanActivate {

  canActivate(
    context: ExecutionContext,
  ): boolean {

    const request = context
      .switchToHttp()
      .getRequest();

    const token =
      request.headers.authorization;

    return validateToken(token);
  }

}
```

### Roles Guard Example

```typescript
@UseGuards(RolesGuard)
@Roles('admin')
@Get('/admin')
getAdminData() {}
```

The guard checks that `user.role === 'admin'`.

## What Is "Route Metadata"?

Route metadata is arbitrary data attached to a controller class or handler method at *definition time* (when the code is written), which anything running at *request time* (a guard, an interceptor) can look up and act on. It's built on the `reflect-metadata` library — a decorator like `@SetMetadata('roles', ['admin'])` doesn't run any logic itself, it just stamps a key/value pair onto that method's metadata, sitting there inert until something reads it.

This is what "[middleware](../middleware.md) cannot easily access route metadata" (above) actually means concretely: [middleware](../middleware.md) runs as a plain Express-style function with only the request/response objects — it has no reference to *which* decorated class/method is about to handle the request, so there's nothing to read metadata off of. A guard receives an `ExecutionContext`, which exposes `context.getHandler()` and `context.getClass()` — the actual method/class references — so a `Reflector` can look up whatever metadata was attached to *that specific* handler.

**Concretely, this is a two-step contract**: something decorates a route with data, and something else reads it back:

```typescript
// 1. Attach metadata at definition time
export const Roles = (...roles: string[]) => SetMetadata('roles', roles);

@Roles('admin')
@Get('/admin')
getAdminData() {}

// 2. Read it back at request time, inside a guard
const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
// requiredRoles === ['admin'] for this specific route, undefined for any route without @Roles
```

This is the mechanism behind every "declarative" NestJS pattern — `@Roles(...)`, a custom `@RequirePermission(...)`, even framework-internal metadata like `@Get()`/`@Post()` themselves are stored and read this exact same way. See [Policy-Based Authorization](../data/policy-based-authorization.md) for a route-level guard built entirely on this pattern — a route missing its expected metadata (e.g. no `@PromptAction(...)`) is treated as unreachable rather than unrestricted, precisely because the guard can tell the difference between "metadata says deny" and "no metadata was ever attached."

## Custom Decorators + Guards

A very important NestJS pattern: pair a metadata decorator with a guard that reads it.

**Roles decorator:**

```typescript
export const Roles = (...roles: string[]) =>
  SetMetadata('roles', roles);
```

**Guard reads the metadata:**

```typescript
const roles = this.reflector.get(
  'roles',
  context.getHandler(),
);
```

## Guard Scope Levels

**Global** — applied to all routes:

```typescript
app.useGlobalGuards(new AuthGuard());
```

**Controller-level:**

```typescript
@UseGuards(AuthGuard)
@Controller('users')
```

**Route-level:**

```typescript
@UseGuards(AuthGuard)
@Get()
```

## Guards vs Middleware

| [Middleware](../middleware.md) | Guard |
|---|---|
| Runs before guards | Runs after [middleware](../middleware.md) |
| Generic request processing | Access control |
| Cannot easily access route metadata | Can access metadata |
| Express-level | NestJS-level |

[Middleware](../middleware.md) is good for logging, [CORS](../../security/attacks/cors.md), request parsing, and [rate limiting](../architecture/rate-limiting.md). Guards are good for [authentication](../../security/auth/authentication.md), [authorization](../../security/authorization/authorization.md), and permissions.

## Guards vs Interceptors

| Guard | Interceptor |
|---|---|
| Decide access | Transform request/response |
| Before controller | Before & after handler |

## Guards vs Pipes

| Guard | Pipe |
|---|---|
| Access control | Validation/transformation |

## NestJS Request Lifecycle

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

## Async Guards

Guards can be asynchronous:

```typescript
async canActivate() {
  return await validateUser();
}
```

## Throwing Exceptions

Instead of returning `false`, throw for better control over the response:

```typescript
throw new UnauthorizedException();
```

## Passport Integration

NestJS commonly integrates guards with Passport.js:

```typescript
@UseGuards(AuthGuard('jwt'))
```

## Why Guards Are Powerful

They integrate with decorators, metadata, [dependency injection](../../programming/fundamentals/dependency-injection.md), and route handlers — producing a clean, policy-driven architecture.

## Common Questions

**Q: What is a guard in NestJS?**
Guards determine whether a request is authorized to access a specific route.

**Q: Difference between [middleware](../middleware.md) and guards?**
Middleware handles generic request processing; guards focus on [authentication](../../security/auth/authentication.md) and [authorization](../../security/authorization/authorization.md) with route awareness.

**Q: Why are guards better than middleware for auth?**
Because guards can access route metadata, decorators, and the execution context.

**Q: What is `CanActivate`?**
The interface that defines authorization logic for a guard.

**Q: What is `ExecutionContext`?**
An [abstraction](../../programming/fundamentals/abstraction.md) providing access to the request lifecycle and handler metadata.

**Q: Guard execution order?**
`Middleware → Guards → Pipes → Controller`

**Q: What are common guard use cases?**
[JWT](../../security/auth/jwt.md) auth, role checks, permission checks, API access control.

**Senior-level answer:** Guards in NestJS are request lifecycle components responsible for authorization and access control decisions. They execute after middleware and before route handlers, leveraging execution context and metadata reflection to enforce [authentication](../../security/auth/authentication.md) and policy-based permissions declaratively. This separates business logic from access-control logic, improving scalability, maintainability, and security architecture.

> Easy way to remember: **Middleware = general processing. Guard = security checkpoint.**

## Related

- [NestJS Overview](nestjs-overview.md)
- [Middleware](../middleware.md)
- [Controllers](controllers.md)
- [Policy-Based Authorization](../data/policy-based-authorization.md)
- [JWT](../../security/auth/jwt.md)
- [HTTP Status Codes](../api/http-status-codes.md)
