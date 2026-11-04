# Zod

Zod is a TypeScript-first schema declaration and runtime validation library. You define a schema with Zod's fluent API, and Zod both infers the TypeScript type from it (no duplication) and validates real data against it at runtime. It is the TypeScript equivalent of [Pydantic](../python/pydantic.md) in Python — used extensively in AI agent code written in TypeScript/Node.js to enforce the shape of [LLM](../../ai/generation/llm.md) outputs, tool call arguments, and API request bodies. See [Structured Output](../../ai/generation/structured-output.md) for the [LLM](../../ai/generation/llm.md)-side schema enforcement that complements Zod's application-side validation.

---

## Core Concepts

| Term | Meaning |
|---|---|
| `z.object({})` | Defines an object schema with named fields and their types |
| `z.string()`, `z.number()`, `z.boolean()` | Primitive type validators |
| `z.enum([...])` | Restricts a field to a specific set of string values |
| `z.optional()` | Marks a field as optional (may be `undefined`) |
| `z.nullable()` | Allows a field to be `null` |
| `.parse(data)` | Validates and returns the typed value, throws `ZodError` on failure |
| `.safeParse(data)` | Returns `{ success, data }` or `{ success: false, error }` — never throws |
| `z.infer<typeof schema>` | Derives the TypeScript type from a schema — no duplication |
| `.refine(fn)` | Adds a custom validation function (equivalent of [Pydantic](../python/pydantic.md)'s `@field_validator`) |
| `zodToJsonSchema()` | Converts a Zod schema to [JSON](../fundamentals/json.md) Schema — used to pass tool definitions to [LLMs](../../ai/generation/llm.md) |

---

## Basic Schema

```typescript
import { z } from "zod";

const UserSchema = z.object({
  name: z.string(),
  age: z.number().int().positive(),
  email: z.string().email(),
});

// TypeScript type inferred automatically — no separate interface needed
type User = z.infer<typeof UserSchema>;

// Valid
const user = UserSchema.parse({ name: "Amr", age: 30, email: "amr@example.com" });
//    ^ type: User — fully typed

// Invalid — throws ZodError with field path and expected type
UserSchema.parse({ name: "Amr", age: "not-a-number", email: "amr@example.com" });
```

---

## Optional Fields, Defaults, and Enums

```typescript
const ArticleSchema = z.object({
  title: z.string().min(1),
  body: z.string(),
  tags: z.array(z.string()).default([]),
  author: z.string().nullable().optional(),
  status: z.enum(["draft", "published", "archived"]).default("draft"),
});
```

`.default()` is applied when the field is `undefined` in the input — it coerces rather than rejects.

---

## Parsing LLM Output (the AI engineering use case)

When an [LLM](../../ai/generation/llm.md) returns [JSON](../fundamentals/json.md) and you need to parse it into a typed object:

```typescript
import { z } from "zod";

const ExtractedEntitySchema = z.object({
  company: z.string(),
  location: z.string(),
  employee_count: z.number().nullable().optional(),
});

type ExtractedEntity = z.infer<typeof ExtractedEntitySchema>;

// raw is the JSON string returned by the LLM
const raw = `{"company": "Acme Corp", "location": "Riyadh", "employee_count": 200}`;
const entity = ExtractedEntitySchema.parse(JSON.parse(raw));
//    ^ type: ExtractedEntity — validated and typed
```

Use `.safeParse()` when you want to handle the error without a try/catch:

```typescript
const result = ExtractedEntitySchema.safeParse(JSON.parse(raw));
if (!result.success) {
  console.error("LLM returned invalid shape:", result.error.issues);
} else {
  const entity = result.data; // typed as ExtractedEntity
}
```

---

## Generating JSON Schema for Tool Definitions

To pass a tool's parameter schema to an [LLM](../../ai/generation/llm.md), convert the Zod schema to [JSON](../fundamentals/json.md) Schema:

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema"; // npm install zod-to-json-schema

const SearchArgsSchema = z.object({
  query: z.string().describe("The search query to execute"),
  max_results: z.number().int().min(1).max(20).default(5).describe("Number of results"),
  filter_date: z.string().optional().describe("ISO date string to filter results after"),
});

const jsonSchema = zodToJsonSchema(SearchArgsSchema, "SearchArgs");
// Pass jsonSchema.definitions.SearchArgs to the LLM as the tool's parameter schema
```

The [LLM](../../ai/generation/llm.md) reads the `.describe()` annotations to understand what each field means — write them as if explaining to the model, not to a developer.

---

## Enforcing Agent Tool Permissions (interview pattern)

The pattern from Q14 in the interview prep — validating agent actions and blocking disallowed tools before any execution:

```typescript
import { z } from "zod";

const ALLOWED_TOOLS = ["search_documents", "get_policy", "send_summary"] as const;

const AgentActionSchema = z.discriminatedUnion("action", [
  z.object({
    action: z.literal("tool_call"),
    tool_name: z.enum(ALLOWED_TOOLS),  // rejected immediately if not in the allowlist
    tool_args: z.record(z.unknown()),
  }),
  z.object({
    action: z.literal("final_answer"),
    answer: z.string().min(1),
  }),
]);

type AgentAction = z.infer<typeof AgentActionSchema>;

// Parse LLM response — throws ZodError if tool_name is not in ALLOWED_TOOLS
const rawLlmOutput = `{"action": "tool_call", "tool_name": "search_documents", "tool_args": {"query": "leave policy"}}`;
const agentAction = AgentActionSchema.parse(JSON.parse(rawLlmOutput));
// If tool_name = "delete_database" → ZodError thrown before any execution
```

`z.discriminatedUnion` is the idiomatic TypeScript pattern for a response that is one of several distinct shapes — here, either a tool call or a final answer.

---

## Custom Validation with `.refine()`

```typescript
const DateRangeSchema = z.object({
  start: z.string().datetime(),
  end: z.string().datetime(),
}).refine(
  (data) => new Date(data.end) > new Date(data.start),
  { message: "end must be after start", path: ["end"] }
);
```

`.refine()` runs after type validation passes — use it for cross-field rules or business constraints that can't be expressed as a type alone.

---

## Zod vs Pydantic: Key Differences

| | Zod (TypeScript) | [Pydantic](../python/pydantic.md) (Python) |
|---|---|---|
| Type inference | `z.infer<typeof Schema>` | `class Model(BaseModel)` |
| Safe parse | `.safeParse()` returns result object | `model_validate()` raises `ValidationError` |
| [JSON](../fundamentals/json.md) Schema | `zodToJsonSchema()` (separate package) | `.model_json_schema()` (built-in) |
| Discriminated union | `z.discriminatedUnion()` | `Union[ModelA, ModelB]` with `Annotated` |
| Default values | `.default()` | `Field(default=...)` |
| Custom validation | `.refine()` | `@field_validator` |

Both provide the same core guarantee: **data is either valid and typed, or rejected with a detailed error before it reaches application logic.**

---

## Common Questions

**Why use Zod instead of TypeScript interfaces?**
> TypeScript interfaces are compile-time only — they disappear at runtime. Zod validates at runtime, when real data arrives from an [LLM](../../ai/generation/llm.md), an [HTTP](../../networking/http.md) request, or an external API. The interface tells the compiler what you expect; Zod enforces it on actual data.

**When to use `.parse()` vs `.safeParse()`?**
> `.parse()` when a validation failure is an unrecoverable error (invalid [LLM](../../ai/generation/llm.md) output that the agent can't continue with). `.safeParse()` when you want to handle the failure gracefully and continue — log it, return a fallback, or ask the model to try again.

**Does Zod work with NestJS?**
> Yes — through libraries like `nestjs-zod` or by using Zod schemas inside guards and pipes. NestJS natively uses `class-validator` + `class-transformer`, but Zod schemas are often preferred in projects where TypeScript-first type inference matters more than decorator-based validation.

---

## Related

- [Data Validation](../fundamentals/data-validation.md) — the general concept Zod implements for TypeScript
- [Pydantic](../python/pydantic.md) — the Python equivalent; same purpose, different syntax
- [Structured Output](../../ai/generation/structured-output.md) — LLM-side schema enforcement that Zod validates on the application side
- [Tool Calling](../../ai/agents/tool-calling.md) — tool argument schemas can be generated from Zod schemas and passed to [LLMs](../../ai/generation/llm.md)
- [class-validator](../../backend/api/class-validator.md) — the NestJS decorator-based alternative; Zod is preferred outside NestJS
- [Validation Libraries Overview](../../../overviews/programming/validation-libraries.md) — [Pydantic](../python/pydantic.md) vs [class-validator](../../backend/api/class-validator.md) vs Zod: when to choose each
- [FastAPI](../python/fastapi.md) — uses [Pydantic](../python/pydantic.md) in the same role Zod fills in TypeScript backends
