# class-validator (NestJS / TypeScript)

`class-validator` is a TypeScript/JavaScript decorator-based validation library used in NestJS to validate DTOs (Data Transfer Objects). A [DTO](dto.md) is a plain class that describes the shape of incoming request data; `class-validator` decorators annotate each field with constraints; NestJS's built-in `ValidationPipe` runs the validation automatically before the route handler fires. No per-route validation code is needed once the pipe is wired globally.

---

## Core Concepts

| Term | Meaning |
|---|---|
| **[DTO](dto.md)** | [Data Transfer Object](dto.md) — a plain TypeScript class representing the shape of incoming request data |
| **Decorator** | A `@IsString()`, `@IsInt()`, etc. annotation on a class field that declares the validation rule |
| `ValidationPipe` | NestJS pipe that runs `class-validator` on every decorated [DTO](dto.md) automatically |
| `class-transformer` | Companion library required for type coercion (`@Type()`) and nested [DTO](dto.md) validation (`@ValidateNested()`) |
| `whitelist: true` | Strips any property not present in the [DTO](dto.md) class — prevents unknown fields from reaching handlers |
| `transform: true` | Auto-coerces incoming strings to the declared type (e.g. `"42"` → `42` for an `@IsInt()` field) |

---

## Defining a DTO

```typescript
import { IsString, IsNotEmpty, IsUUID, IsInt, Min, Max, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class ChatRequestDto {
  @ApiProperty({ example: 'What is the leave policy?' })
  @IsString()
  @IsNotEmpty()
  query: string;

  @ApiProperty()
  @IsUUID()
  session_id: string;

  @ApiProperty({ default: 512 })
  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(4096)
  max_tokens?: number;
}
```

`@ApiProperty()` is a `@nestjs/swagger` decorator that feeds the same [DTO](dto.md) into [OpenAPI](openapi.md) documentation generation — the [DTO](dto.md) is the single source of truth for both validation and API docs.

---

## Wiring ValidationPipe Globally

In `main.ts`, register the pipe once — it applies to every route:

```typescript
import { ValidationPipe } from '@nestjs/common';

app.useGlobalPipes(new ValidationPipe({
  whitelist: true,             // strip unknown properties
  forbidNonWhitelisted: true,  // throw 400 on unknown properties instead of silently stripping
  transform: true,             // auto-coerce types (e.g. string → number from query params)
}));
```

With these options NestJS: validates every incoming body against the DTO, strips unexpected fields, coerces types, and returns a structured 400 error on failure — all without any per-route code.

---

## Common Decorators

| Decorator | Validates |
|---|---|
| `@IsString()` | Must be a string |
| `@IsNotEmpty()` | Non-empty after trim |
| `@IsEmail()` | Valid email format |
| `@IsUUID()` | Valid [UUID](../../databases/relational/uuid.md) (v4 by default) |
| `@IsInt()` / `@IsNumber()` | Integer / any number |
| `@Min(n)` / `@Max(n)` | Numeric range |
| `@IsOptional()` | Field may be absent — all other decorators on the same field are skipped if the value is `undefined` |
| `@IsArray()` | Must be an array |
| `@IsEnum(MyEnum)` | Must be one of the enum's values |
| `@Length(min, max)` | String length range |
| `@Matches(regex)` | Must match a regular expression |
| `@ValidateNested()` | Validate a nested DTO object recursively (requires `@Type()` from `class-transformer`) |

---

## Nested DTO Validation

`class-validator` alone cannot validate nested objects — you need `class-transformer`'s `@Type()` decorator to instantiate the nested class first:

```typescript
import { Type } from 'class-transformer';
import { ValidateNested, IsString } from 'class-validator';

export class AddressDto {
  @IsString()
  city: string;

  @IsString()
  country: string;
}

export class CreateOrderDto {
  @ValidateNested()
  @Type(() => AddressDto)    // class-transformer instantiates AddressDto from the raw object
  shipping_address: AddressDto;
}
```

Without `@Type()`, the nested object arrives as a plain `{}` and `@ValidateNested()` has nothing to validate against.

---

## Error Response

On validation failure, NestJS returns a structured 400 with the field-level errors:

```json
{
  "statusCode": 400,
  "message": [
    "query must be a string",
    "session_id must be a UUID"
  ],
  "error": "Bad Request"
}
```

The error messages come from `class-validator`'s defaults, which can be overridden per decorator: `@IsString({ message: 'query must be text' })`.

---

## class-validator vs Zod (TypeScript)

| | class-validator | [Zod](../../programming/typescript/zod.md) |
|---|---|---|
| Style | Decorators on a class | Schema object (no class required) |
| NestJS integration | Native — built into NestJS pipes | Possible via `nestjs-zod`, less idiomatic |
| Type inference | Separate TypeScript type needed | `z.infer<typeof Schema>` derives the type |
| Runtime requirement | Requires `reflect-metadata` | No reflection required |
| Use case | NestJS DTOs | Anywhere in TypeScript — API handlers, env vars, [LLM](../../ai/generation/llm.md) output |

`class-validator` is the NestJS convention and integrates cleanly with its pipe system and [DI](../../programming/fundamentals/dependency-injection.md) container. [Zod](../../programming/typescript/zod.md) is preferred for projects where TypeScript-first type inference matters more than decorator-based validation.

---

## Common Questions

**Why is `class-transformer` a separate install from `class-validator`?**
> They solve different problems. `class-validator` adds validation rules; `class-transformer` handles converting plain objects into typed class instances (and back). NestJS's `ValidationPipe` with `transform: true` calls both internally — but for nested DTOs you must explicitly annotate with `@Type()` so `class-transformer` knows which class to instantiate.

**Does `whitelist: true` break forwards compatibility?**
> It can if a client sends new fields before the server has updated its DTO. `forbidNonWhitelisted: true` is stricter still (returns 400 rather than silently stripping). Choose based on how tightly coupled your API versions are: a public API might omit `forbidNonWhitelisted`, while an internal service can afford to be strict.

**Can I validate query parameters and path params the same way?**
> Yes — decorate the corresponding DTO and apply it to `@Query()` or `@Param()` in the controller, with `transform: true` in the pipe so the string URL params are coerced to their declared types.

---

## Related

- [Data Validation](../../programming/fundamentals/data-validation.md) — the general concept class-validator implements for NestJS
- [NestJS Overview](../nestjs/nestjs-overview.md)
- [OpenAPI](openapi.md) — `@ApiProperty()` on the same DTO feeds NestJS/Swagger [OpenAPI](openapi.md) generation
- [Zod](../../programming/typescript/zod.md) — the schema-first alternative; preferred outside NestJS for TypeScript validation
- [Pydantic](../../programming/python/pydantic.md) — the Python equivalent (used with [FastAPI](../../programming/python/fastapi.md))
- [Validation Libraries Overview](../../../overviews/programming/validation-libraries.md)
