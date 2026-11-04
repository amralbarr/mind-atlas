# Controllers

In [NestJS](https://nestjs.com/), controllers are responsible for handling incoming [HTTP](../../networking/http.md) requests and returning responses. They are the entry point of your API.

## Request Flow

```text
Client Request
     ↓
Controller
     ↓
Service
     ↓
Database / Logic
```

### Analogy

Think of a restaurant:

```text
Customer → Waiter → Chef
```

- Customer = Client
- Waiter = Controller
- Chef = Service

The waiter receives the order, passes it to the chef, and returns the response — the waiter does **not** cook. Likewise, controllers should not contain business logic.

## Basic Controller Example

```typescript
import { Controller, Get } from '@nestjs/common';

@Controller('users')
export class UsersController {

  @Get()
  getUsers() {
    return ['Amr', 'Ali'];
  }

}
```

`@Controller('users')` creates the route prefix `/users`. The `@Get()` decorator handles `GET /users` and returns `["Amr", "Ali"]`.

## Route Decorators

NestJS provides a decorator for each [HTTP](../../networking/http.md) verb:

```typescript
@Get()
@Post()
@Put()
@Delete()
@Patch()
```

### Full CRUD Example

```typescript
@Controller('users')
export class UsersController {

  @Get()
  findAll() {}

  @Get(':id')
  findOne() {}

  @Post()
  create() {}

  @Put(':id')
  update() {}

  @Delete(':id')
  remove() {}
}
```

## Route Parameters

```typescript
@Get(':id')
findOne(@Param('id') id: string) {
  return id;
}
```

Request `GET /users/5` returns `5`.

## Query Parameters

```typescript
@Get()
findAll(@Query('page') page: string) {
  return page;
}
```

Request: `/users?page=2`

## Request Body

```typescript
@Post()
create(@Body() body: any) {
  return body;
}
```

Example request body:

```json
{
  "name": "Amr"
}
```

## Injecting Services

Controllers usually delegate work to services via [dependency injection](../../programming/fundamentals/dependency-injection.md).

```typescript
@Injectable()
export class UsersService {
  findAll() {
    return ['Amr', 'Ali'];
  }
}
```

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

## Best Practices

Controllers **should**:

- receive requests
- validate input
- call services
- return responses

Controllers **should NOT**:

- access the database directly
- contain heavy logic
- contain business rules

**Bad:**

```typescript
@Get()
async getUsers() {
  const users = await prisma.user.findMany();
  // huge logic here ❌
}
```

**Good:**

```typescript
@Get()
getUsers() {
  return this.usersService.getUsers();
}
```

Logic stays in the service — see [Services](services.md).

## HTTP Status Codes

NestJS handles many status codes automatically:

```typescript
@Post()
create() {
  return { success: true };
}
```

Default response code: `201 Created`.

Override with a custom status code:

```typescript
@HttpCode(200)
@Post()
create() {}
```

## Response Object

Advanced usage lets you access the raw response object directly, though this is usually avoided unless necessary:

```typescript
@Get()
findAll(@Res() res: Response) {
  res.json({ message: 'Hello' });
}
```

## [DTO](../api/dto.md) Validation

Controllers commonly validate incoming data using [DTOs](../api/dto.md).

```typescript
export class CreateUserDto {
  name: string;
  age: number;
}
```

```typescript
@Post()
create(@Body() dto: CreateUserDto) {}
```

This is usually combined with a `ValidationPipe`.

## Async Controllers

```typescript
@Get()
async findAll() {
  return await this.usersService.findAll();
}
```

## Exception Handling

NestJS automatically catches thrown exceptions:

```typescript
throw new NotFoundException();
```

Returns:

```json
{
  "statusCode": 404,
  "message": "Not Found"
}
```

## Controller vs Service

| Controller | Service |
|---|---|
| Handles requests | Handles business logic |
| API layer | Logic layer |
| Thin layer | Core functionality |

## Example: Applied to a Real System

In a telemetry/agents backend, controllers typically map one-to-one with feature areas:

```text
TelemetryController
SignalsController
AgentsController
DashboardController
AuthController
```

Example endpoints:

```text
GET /signals/latest
POST /agents/run
GET /dashboard/:id
```

Controllers expose the API surface; services handle the underlying logic.

## Common Questions

**Q: What is a controller?**
A controller handles incoming [HTTP](../../networking/http.md) requests, delegates business logic to services, and returns responses to the client.

**Q: Should business logic exist in controllers?**
No — business logic belongs in services.

**Q: What is the role of decorators?**
Decorators define routes, metadata, and request-handling behavior (e.g. `@Get()`, `@Post()`, `@Controller()`).

**Q: Difference between controller and service?**
See the comparison table above.

**Senior-level answer:** Controllers in NestJS are responsible for handling incoming requests, mapping routes, validating input, and delegating business logic to services while maintaining clean separation of concerns.

> Easy way to remember: **Controller = API entry point.**

## Related

- [DTO](../api/dto.md) — the request/response objects controllers validate against
- [NestJS Overview](nestjs-overview.md)
- [Middleware](../middleware.md)
- [Guards](guards.md)
- [REST](../api/rest.md)
- [GraphQL](../api/graphql.md)
