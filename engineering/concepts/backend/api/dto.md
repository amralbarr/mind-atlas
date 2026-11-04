# DTO (Data Transfer Object)

A **DTO** is a plain object whose only job is carrying data between two layers of a system — typically across a network boundary (an API request/response body) or between an application's own layers (controller → service) — with no business logic of its own. It defines *what shape of data moves*, deliberately separate from the domain model that defines *what that data means and how it behaves* internally.

## Why Not Just Pass the Domain Model Directly?

```
Client request
    ↓
DTO           ← exactly the fields the API contract exposes, nothing more
    ↓
Service layer  ← maps DTO → internal domain model, applies business logic
    ↓
Database
```

If a controller accepted and returned the raw database entity directly, every internal field (an audit timestamp, an internal [foreign key](../../databases/relational/foreign-key.md), a password hash) would be implicitly part of the public API contract — any schema change to the entity would silently change the API too, and an entity update endpoint could accidentally let a client set fields it was never meant to control. A DTO is the explicit, intentional subset of fields the API actually exposes in each direction, decoupling the internal data model from the external contract.

## The Three Common Directions

| DTO | Direction | Purpose |
|---|---|---|
| **Request DTO** | Client → server | The exact shape an endpoint accepts — validated before any business logic runs |
| **Response DTO** | Server → client | The exact shape returned — excludes internal-only fields (password hashes, internal IDs, soft-delete flags) even if the underlying entity has them |
| **Internal DTO** | Service → service | Passes data between application layers without either layer depending on the other's full internal model |

A single resource commonly has multiple different DTOs for different operations — a `CreateUserDto` (no `id`, since the server assigns it), an `UpdateUserDto` (every field optional, since a partial update doesn't require all of them), and a `UserResponseDto` (no password field, ever).

## DTOs and Validation Are a Natural Pair

A DTO's fields are exactly what [data validation](../../programming/fundamentals/data-validation.md) needs to check — which is why DTO classes are usually also the validation schema itself, not a separate thing:

```typescript
// NestJS: the DTO class IS the validation schema via class-validator decorators
export class CreateUserDto {
  @IsString() @IsNotEmpty()
  name: string;

  @IsEmail()
  email: string;
}
```

```python
# Python/FastAPI: a Pydantic BaseModel plays exactly the same DTO role
class CreateUserDto(BaseModel):
    name: str
    email: EmailStr
```

See [class-validator](class-validator.md) for the NestJS convention (DTO class + decorators, wired through `ValidationPipe`) and [Pydantic](../../programming/python/pydantic.md) for the same pattern in Python — in both ecosystems, "define the DTO" and "define the validation rules" are typically the same step, not two separate ones.

## DTO vs. Domain Model vs. Database Entity

These three are easy to conflate because a simple CRUD endpoint can look identical across all of them — but they diverge the moment the system has any real logic or any field that shouldn't cross the API boundary:

| | DTO | Domain model | Database entity |
|---|---|---|---|
| **Lives at** | The API boundary | Application/business logic | The persistence layer |
| **Contains** | Only what this specific request/response needs | Behavior + the data the business logic actually operates on | Every persisted column, including internal-only ones |
| **Changes when** | The public API contract changes | The business rules change | The schema/[ORM](../data/orm.md) mapping changes |

A mature system's mapping layer explicitly converts between these three — entity → domain model → response DTO — rather than reusing one object for all three roles, which is exactly what tends to leak internal fields into a public API by accident.

## Related

- [Data Validation](../../programming/fundamentals/data-validation.md) — DTO fields are what gets validated
- [class-validator](class-validator.md) — the NestJS DTO + validation convention
- [Pydantic](../../programming/python/pydantic.md) — the Python equivalent pattern
- [Interface vs. Type](../../programming/typescript/interface-vs-type.md) — a DTO is often defined as a `class` specifically (not just an `interface`/`type`) because decorator-based validation needs a real class instance to attach to
- [Controllers](../nestjs/controllers.md) — where request DTOs are received and response DTOs are returned
- [OpenAPI](openapi.md) — DTO classes commonly double as the source [OpenAPI](openapi.md) schema generation reads from
