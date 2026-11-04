# Python Web Frameworks

At-a-glance comparison of the major Python web frameworks — when to pick each one and how they relate to [FastAPI](../../concepts/programming/python/fastapi.md).

## At a Glance

| Framework | Type | Sync/Async | Best for |
|---|---|---|---|
| **[FastAPI](../../concepts/programming/python/fastapi.md)** | Micro (API-focused) | Async-native ([ASGI](../../concepts/backend/architecture/asgi.md)) | [LLM](../../concepts/ai/generation/llm.md) backends, AI APIs, high-concurrency [REST](../../concepts/backend/api/rest.md) APIs |
| **[Flask](../../concepts/programming/python/flask.md)** | Micro | Sync (WSGI), partial async | Simple APIs, prototypes, internal tools |
| **[Django](../../concepts/programming/python/django.md) + DRF** | Full-stack | Sync (WSGI), async in views | Enterprise web apps, CMS, complex data models |
| **[Starlette](../../concepts/programming/python/starlette.md)** | Micro (low-level) | Async-native ([ASGI](../../concepts/backend/architecture/asgi.md)) | Building frameworks on top of, raw [ASGI](../../concepts/backend/architecture/asgi.md) apps |
| **Litestar** | Micro (API-focused) | Async-native ([ASGI](../../concepts/backend/architecture/asgi.md)) | [FastAPI](../../concepts/programming/python/fastapi.md) alternative with stricter typing |
| **Sanic** | Micro | Async-native | High-throughput APIs, [WebSockets](../../concepts/networking/websockets.md) |
| **Tornado** | Micro | Async (own [event loop](../../concepts/programming/javascript/event-loop.md)) | Long-lived connections, legacy async Python |
| **aiohttp** | [HTTP](../../concepts/networking/http.md) client + server | Async-native | [HTTP](../../concepts/networking/http.md) client usage; rarely used as a web server now |

## FastAPI vs Flask

The most common comparison. [Flask](../../concepts/programming/python/flask.md) was the default Python micro-framework for a decade; [FastAPI](../../concepts/programming/python/fastapi.md) is its async successor for API work.

| | [FastAPI](../../concepts/programming/python/fastapi.md) | [Flask](../../concepts/programming/python/flask.md) |
|---|---|---|
| Request validation | Automatic ([Pydantic](../../concepts/programming/python/pydantic.md)) | Manual |
| [OpenAPI](../../concepts/backend/api/openapi.md) docs | Auto-generated at `/docs` | Requires [flask](../../concepts/programming/python/flask.md)-smorest or flasgger |
| Async support | Native (`async def`) | Partial (async views, but WSGI blocks) |
| Type hints | First-class — drives validation and docs | Optional, no framework integration |
| Performance | Higher ([ASGI](../../concepts/backend/architecture/asgi.md) + async) | Lower (WSGI, blocking by default) |
| Learning curve | Slightly steeper ([Pydantic](../../concepts/programming/python/pydantic.md), [DI](../../concepts/programming/fundamentals/dependency-injection.md)) | Simpler to start |
| Ecosystem | Growing, AI-focused | Mature, vast extension ecosystem |

**Choose [Flask](../../concepts/programming/python/flask.md) when:** small internal tool, team already on [Flask](../../concepts/programming/python/flask.md), no async [I/O](../../concepts/programming/fundamentals/io.md) needed, pure prototyping.
**Choose [FastAPI](../../concepts/programming/python/fastapi.md) when:** building an API (not a full web app), async [I/O](../../concepts/programming/fundamentals/io.md) ([LLM](../../concepts/ai/generation/llm.md) calls, DB calls), automatic validation and docs matter.

## FastAPI vs Django (+ DRF)

[Django](../../concepts/programming/python/django.md) is a full-stack framework — it includes [ORM](../../concepts/backend/data/orm.md), admin panel, auth, migrations, templates. [FastAPI](../../concepts/programming/python/fastapi.md) is API-only.

| | [FastAPI](../../concepts/programming/python/fastapi.md) | [Django](../../concepts/programming/python/django.md) + DRF |
|---|---|---|
| [ORM](../../concepts/backend/data/orm.md) | Bring your own (SQLAlchemy, Tortoise, Prisma) | Built-in [Django](../../concepts/programming/python/django.md) [ORM](../../concepts/backend/data/orm.md) |
| Admin panel | None | Built-in `/admin` |
| Auth | Bring your own ([JWT](../../concepts/security/auth/jwt.md), OAuth) | Built-in session auth + [django](../../concepts/programming/python/django.md)-allauth |
| Migrations | Alembic (SQLAlchemy) or Prisma | Built-in `makemigrations` |
| Async | Native | Partial (async views available, [ORM](../../concepts/backend/data/orm.md) still sync by default) |
| API [serialization](../../concepts/programming/fundamentals/serialization.md) | [Pydantic](../../concepts/programming/python/pydantic.md) (automatic) | DRF Serializers (explicit) |

**Choose [Django](../../concepts/programming/python/django.md) when:** you need the full stack — [ORM](../../concepts/backend/data/orm.md), admin, auth, templates, content management.
**Choose [FastAPI](../../concepts/programming/python/fastapi.md) when:** building a pure API service, microservice, or AI backend with your own data layer.

## Starlette — FastAPI's Foundation

[FastAPI](../../concepts/programming/python/fastapi.md) is built on [Starlette](../../concepts/programming/python/starlette.md). [Starlette](../../concepts/programming/python/starlette.md) is the lower-level [ASGI](../../concepts/backend/architecture/asgi.md) toolkit that provides routing, [middleware](../../concepts/backend/middleware.md), [WebSockets](../../concepts/networking/websockets.md), and request/response primitives. FastAPI adds [Pydantic](../../concepts/programming/python/pydantic.md) validation, [OpenAPI](../../concepts/backend/api/openapi.md) generation, and the `Depends()` injection system on top.

Use [Starlette](../../concepts/programming/python/starlette.md) directly only when: building a custom framework, need raw [ASGI](../../concepts/backend/architecture/asgi.md) [middleware](../../concepts/backend/middleware.md), or FastAPI's abstractions are in the way.

## Litestar — The Modern FastAPI Alternative

Litestar (formerly Starlite) is an [ASGI](../../concepts/backend/architecture/asgi.md) framework with a similar goal to FastAPI but different design choices:
- Stricter typing enforcement
- Built-in [DTO](../../concepts/backend/api/dto.md) (Data Transfer Object) system separate from the domain model
- Built-in [OpenTelemetry](../../concepts/backend/observability/opentelemetry.md) support
- Class-based [controllers](../../concepts/backend/nestjs/controllers.md) as first-class citizens
- More opinionated project structure

Still maturing ecosystem compared to FastAPI. Worth knowing exists; FastAPI remains the default for AI/[LLM](../../concepts/ai/generation/llm.md) work.

## Why FastAPI Dominates AI/LLM Backends

1. **`async def` handlers** — [LLM](../../concepts/ai/generation/llm.md) API calls, vector DB queries, and embedding calls are all [I/O](../../concepts/programming/fundamentals/io.md)-bound; async handlers let one process handle many concurrent waiting requests
2. **[Pydantic](../../concepts/programming/python/pydantic.md)** — the same library used for structured [LLM](../../concepts/ai/generation/llm.md) output validation (`.model_validate()`, `instructor` library) is also FastAPI's request/response layer — one mental model throughout
3. **Streaming responses** — `StreamingResponse` with an async generator is the natural shape for token-by-token [LLM](../../concepts/ai/generation/llm.md) output
4. **[OpenAPI](../../concepts/backend/api/openapi.md) docs** — auto-generated, always in sync with code — useful when wiring [LLM](../../concepts/ai/generation/llm.md) tool-use to API endpoints

## Atomic Notes

- [FastAPI](../../concepts/programming/python/fastapi.md)
- [Flask](../../concepts/programming/python/flask.md)
- [Django](../../concepts/programming/python/django.md)
- [Starlette](../../concepts/programming/python/starlette.md)
