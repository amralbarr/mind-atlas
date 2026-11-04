# Validation Libraries

Validation libraries ensure incoming data matches an expected shape and type before application logic touches it — catching malformed requests, coercing types, and producing structured errors instead of silent bad values propagating downstream.

## At a Glance

| Library | Language | Style | Primary Context |
|---|---|---|---|
| **[Pydantic](../../concepts/programming/python/pydantic.md)** | Python | Class + type hints | [FastAPI](../../concepts/programming/python/fastapi.md) (built-in), standalone |
| **[class-validator](../../concepts/backend/api/class-validator.md)** | TypeScript | Decorators on a class | NestJS (via `ValidationPipe`) |
| **[Zod](../../concepts/programming/typescript/zod.md)** | TypeScript | Schema object | Anywhere in TypeScript/Node.js |
| **Joi** | JavaScript | Schema object (older) | Express, standalone |
| **Yup** | JavaScript | Schema object | React/Formik forms |

---

## Same Problem, Three Styles

**[Pydantic](../../concepts/programming/python/pydantic.md) (Python)** — type hints drive everything:

```python
class ChatRequest(BaseModel):
    query: str
    max_tokens: int = Field(default=512, ge=1)
```

**[class-validator](../../concepts/backend/api/class-validator.md) (TypeScript/NestJS)** — decorators on a class:

```typescript
export class ChatRequestDto {
  @IsString() @IsNotEmpty()
  query: string;

  @IsOptional() @IsInt() @Min(1)
  max_tokens?: number;
}
```

**[Zod](../../concepts/programming/typescript/zod.md) (TypeScript)** — schema object, type inferred automatically:

```typescript
const Schema = z.object({
  query: z.string().min(1),
  max_tokens: z.number().int().min(1).optional(),
});
type ChatRequest = z.infer<typeof Schema>;
```

---

## When to Choose Which

| Scenario | Choose |
|---|---|
| [FastAPI](../../concepts/programming/python/fastapi.md) backend (Python) | [Pydantic](../../concepts/programming/python/pydantic.md) — it's built in, no choice needed |
| NestJS backend (TypeScript) | [class-validator](../../concepts/backend/api/class-validator.md) + `ValidationPipe` — the NestJS convention |
| Next.js API route, Edge function, standalone TypeScript | [Zod](../../concepts/programming/typescript/zod.md) — no framework dependency, type inference is its killer feature |
| Environment variable validation | [Zod](../../concepts/programming/typescript/zod.md) (`z.coerce` handles string → number from `process.env`) |
| Structured [LLM](../../concepts/ai/generation/llm.md) output (Python) | [Pydantic](../../concepts/programming/python/pydantic.md) (`instructor`, [LangChain](../../concepts/ai/agents/langchain.md) [structured output](../../concepts/ai/generation/structured-output.md)) |
| Structured [LLM](../../concepts/ai/generation/llm.md) output (TypeScript) | [Zod](../../concepts/programming/typescript/zod.md) (Vercel AI SDK `generateObject`, `instructor-js`) |
| React form validation | [Zod](../../concepts/programming/typescript/zod.md) + `react-hook-form`, or Yup + Formik |

---

## The TypeScript Duplication Problem

With `class-validator`, you typically end up maintaining two things for one concept: a [DTO](../../concepts/backend/api/dto.md) class (runtime validation) and a TypeScript interface or type (compile-time typing). [Zod](../../concepts/programming/typescript/zod.md) eliminates this — define the schema once, derive the type with `z.infer<>`.

This is why [Zod](../../concepts/programming/typescript/zod.md) is increasingly preferred for new TypeScript projects outside NestJS. NestJS sticks with `class-validator` because its pipe system requires class instances (not plain objects) for decorator reflection — a `reflect-metadata` constraint. [Zod](../../concepts/programming/typescript/zod.md) schemas produce plain objects, not class instances, so they do not integrate with NestJS's [DI](../../concepts/programming/fundamentals/dependency-injection.md) container and pipe system as cleanly.

---

## Atomic Notes

- [Pydantic](../../concepts/programming/python/pydantic.md) — Python validation via `BaseModel`, used with [FastAPI](../../concepts/programming/python/fastapi.md) and [LLM](../../concepts/ai/generation/llm.md) [structured output](../../concepts/ai/generation/structured-output.md)
- [class-validator](../../concepts/backend/api/class-validator.md) — TypeScript decorator-based validation for NestJS DTOs, wired via `ValidationPipe`
- [Zod](../../concepts/programming/typescript/zod.md) — TypeScript schema-first validation with automatic type inference

## Related

- [Data Validation](../../concepts/programming/fundamentals/data-validation.md) — the general concept this overview compares concrete implementations of
- [FastAPI](../../concepts/programming/python/fastapi.md) — [Pydantic](../../concepts/programming/python/pydantic.md) is [FastAPI](../../concepts/programming/python/fastapi.md)'s built-in validation layer
- [NestJS Overview](../../concepts/backend/nestjs/nestjs-overview.md) — [class-validator](../../concepts/backend/api/class-validator.md) is the NestJS validation convention
- [OpenAPI](../../concepts/backend/api/openapi.md) — [Pydantic](../../concepts/programming/python/pydantic.md) models and NestJS DTOs both feed [OpenAPI](../../concepts/backend/api/openapi.md) schema generation
- [Structured Output](../../concepts/ai/generation/structured-output.md) — [Pydantic](../../concepts/programming/python/pydantic.md) and Zod are used to constrain and validate [LLM](../../concepts/ai/generation/llm.md) responses
