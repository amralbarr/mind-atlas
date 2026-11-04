# OpenAPI / Swagger

OpenAPI is the industry standard specification for describing [REST](rest.md) APIs in a machine-readable format ([YAML](../../devops/yaml.md) or [JSON](../../programming/fundamentals/json.md)). Swagger is the original name for the spec (Swagger 2.0) and still refers to the UI tooling. OpenAPI 3.x is the current standard.

## The Naming History

| Name | What it is |
|---|---|
| **Swagger 2.0** | The original API spec format (2014) — still widely used |
| **OpenAPI 3.x** | The renamed, evolved standard (2017+) — the current version |
| **Swagger UI** | The interactive HTML docs rendered from an OpenAPI spec — what [FastAPI](../../programming/python/fastapi.md) serves at `/docs` |
| **Swagger Editor** | Browser-based editor for writing OpenAPI specs at editor.swagger.io |
| **SwaggerHub** | Hosted platform for teams to design, document, and share OpenAPI specs |

Swagger 2.0 and OpenAPI 3.x are different formats — they are not directly interchangeable, though converters exist.

## What an OpenAPI Spec Contains

An OpenAPI spec is a single [YAML](../../devops/yaml.md) or [JSON](../../programming/fundamentals/json.md) file describing every endpoint, request shape, response shape, auth scheme, and reusable component of an API.

```yaml
openapi: "3.1.0"
info:
  title: RAG Chat API
  version: "1.0.0"

paths:
  /chat:
    post:
      summary: Submit a query to the RAG pipeline
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ChatRequest"
      responses:
        "200":
          description: Grounded answer with cited sources
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ChatResponse"
        "401":
          description: Missing or invalid JWT

components:
  schemas:
    ChatRequest:
      type: object
      required: [query, session_id]
      properties:
        query:
          type: string
          example: "What is the leave policy?"
        session_id:
          type: string

    ChatResponse:
      type: object
      properties:
        answer:
          type: string
        sources:
          type: array
          items:
            type: string

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## Key Sections of an OpenAPI 3.x Spec

| Section | Purpose |
|---|---|
| `openapi` | Spec version (`3.0.3`, `3.1.0`) |
| `info` | Title, version, description, contact |
| `servers` | Base URLs (production, staging, local) |
| `paths` | Every endpoint — [HTTP](../../networking/http.md) method, parameters, request body, responses |
| `components.schemas` | Reusable data models (referenced with `$ref`) |
| `components.securitySchemes` | Auth definitions (Bearer [JWT](../../security/auth/jwt.md), [API Key](../../security/auth/api-key.md), OAuth2) |
| `components.parameters` | Reusable query/path/header parameters |
| `tags` | Groups of related endpoints for UI organization |

## How Frameworks Generate It Automatically

**[FastAPI](../../programming/python/fastapi.md)** — generates OpenAPI automatically from type hints and [Pydantic](../../programming/python/pydantic.md) models. No annotation needed beyond normal Python typing.
- Interactive Swagger UI: `GET /docs`
- ReDoc UI: `GET /redoc`
- Raw spec [JSON](../../programming/fundamentals/json.md): `GET /openapi.json`

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI(title="RAG Chat API", version="1.0.0")

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.post("/chat", summary="Submit a query", tags=["chat"])
async def chat(body: ChatRequest):
    ...
```

[FastAPI](../../programming/python/fastapi.md) reads `ChatRequest` and its fields and builds the full OpenAPI schema — no extra decorators.

**NestJS** — requires explicit decorators from `@nestjs/swagger`:

```typescript
import { ApiProperty, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';

export class ChatRequestDto {
  @ApiProperty({ example: 'What is the leave policy?' })
  query: string;

  @ApiProperty()
  session_id: string;
}

@ApiBearerAuth()
@Controller('chat')
export class ChatController {
  @Post()
  @ApiOperation({ summary: 'Submit a query to the RAG pipeline' })
  async chat(@Body() body: ChatRequestDto) { ... }
}
```

## Swagger UI vs ReDoc

Both render an OpenAPI spec as interactive HTML documentation.

| | Swagger UI | ReDoc |
|---|---|---|
| Try it out | Yes — execute real requests from the browser | No — read-only |
| Design | More functional/dense | Cleaner, three-panel layout |
| [FastAPI](../../programming/python/fastapi.md) route | `/docs` | `/redoc` |
| Use case | Developer testing + exploration | Public-facing API documentation |

## Why OpenAPI Matters Beyond Documentation

1. **Client generation** — OpenAPI Generator / Swagger Codegen can generate typed API clients in Python, TypeScript, Go, etc. directly from the spec — no hand-writing fetch calls
2. **Contract testing** — tools like Schemathesis can auto-generate and run property-based tests against a live API from the spec alone
3. **Mock servers** — Prism (from Stoplight) runs a mock server from a spec before the real API is built
4. **[LLM](../../ai/generation/llm.md) tool definitions** — an OpenAPI spec is structurally very close to an [LLM](../../ai/generation/llm.md) tool definition; the [MCP](../../ai/agents/model-context-protocol.md) Gateway pattern (exposing [REST](rest.md) endpoints as [LLM](../../ai/generation/llm.md) tools via [YAML](../../devops/yaml.md) config) is essentially an OpenAPI-to-tool-schema adapter

## Common Mistakes

- **Swagger 2.0 vs OpenAPI 3.x confusion** — they have different field names (`swagger: "2.0"` vs `openapi: "3.x"`); tools often support one or the other, not both interchangeably
- **`$ref` paths** — `$ref: "#/components/schemas/Foo"` must match exactly; a typo silently breaks the spec in most validators
- **Missing `required` arrays** — OpenAPI treats all properties as optional unless listed in a `required` array at the object level (not on each property)
- **Not versioning the spec** — treat `openapi.yaml` as source code; changes to it are breaking changes for any generated clients

## Related

- [FastAPI](../../programming/python/fastapi.md) — auto-generates OpenAPI from type hints
- [NestJS Overview](../nestjs/nestjs-overview.md) — generates OpenAPI via `@nestjs/swagger` decorators
- [REST](rest.md) — the architectural style OpenAPI specs describe
- [YAML](../../devops/yaml.md) — the format OpenAPI specs are typically written in
