# Starlette

Starlette is the [ASGI](../../backend/architecture/asgi.md) toolkit that [FastAPI](fastapi.md) is built on. It provides the low-level primitives of an async Python web framework — routing, [middleware](../../backend/middleware.md), [WebSockets](../../networking/websockets.md), background tasks, static file serving, and request/response objects — without [Pydantic](pydantic.md) validation, [OpenAPI](../../backend/api/openapi.md) generation, or a [dependency injection](../fundamentals/dependency-injection.md) system. In normal application development you use [FastAPI](fastapi.md), which inherits everything Starlette provides and adds the higher-level API layer on top. Use Starlette directly only when building a custom framework, writing raw [ASGI](../../backend/architecture/asgi.md) [middleware](../../backend/middleware.md), or when [FastAPI](fastapi.md)'s abstractions are specifically in the way. See [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) for a full comparison.

## Core Concepts

| Term | Meaning |
|---|---|
| **[ASGI](../../backend/architecture/asgi.md)** | The async server interface Starlette implements — see [ASGI](../../backend/architecture/asgi.md) for how it works and why it enables true async concurrency |
| **`Starlette` app** | The central application object — routes and [middleware](../../backend/middleware.md) are registered on it |
| **`Router`** | Groups routes; can be mounted at a path prefix — the same concept as [FastAPI](fastapi.md)'s `APIRouter` (which is a Starlette `Router` with extra capability) |
| **`Route`** | Binds a URL pattern to an endpoint function — `Route("/path", endpoint=my_fn, methods=["GET"])` |
| **`Middleware`** | A class wrapping the [ASGI](../../backend/architecture/asgi.md) app to intercept every request/response — [CORS](../../security/attacks/cors.md), [authentication](../../security/auth/authentication.md), tracing, logging |
| **`Request` / `Response`** | Starlette's typed wrappers around the raw [ASGI](../../backend/architecture/asgi.md) scope/receive/send — `await request.json()`, `return JSONResponse(data)` |
| **`WebSocket`** | First-class WebSocket support — `await ws.accept()`, `await ws.send_text(msg)`, `await ws.receive_text()` |
| **`BackgroundTask`** | Run a function after the response is sent — fire-and-forget work without a separate queue |
| **`TestClient`** | Synchronous test client backed by `httpx` — allows writing synchronous test code against an async Starlette app |

## Installation

```bash
pip install starlette uvicorn
# or, for a full async stack:
pip install starlette[full] uvicorn[standard]
```

## A Minimal Starlette App

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

async def homepage(request):
    return JSONResponse({"hello": "world"})

async def user(request):
    user_id = request.path_params["user_id"]
    return JSONResponse({"user_id": user_id})

app = Starlette(routes=[
    Route("/", homepage),
    Route("/users/{user_id}", user),
])
```

```bash
uvicorn main:app --reload
```

Notice what's missing compared to [FastAPI](fastapi.md): no type-hint-driven validation, no automatic [OpenAPI](../../backend/api/openapi.md) docs, no `Depends()`. You get routing and async [I/O](../fundamentals/io.md) — everything else is manual.

## Middleware

```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = Starlette(
    routes=[...],
    middleware=[
        Middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
        Middleware(CORSMiddleware, allow_origins=["*"]),
    ]
)
```

[FastAPI](fastapi.md)'s `add_middleware()` is a thin wrapper around this same Starlette mechanism.

## WebSockets

```python
from starlette.websockets import WebSocket

async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"echo: {data}")
```

## Background Tasks

```python
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

def send_notification(email: str):
    # runs after the response is sent — no waiting for the client
    ...

async def create_user(request):
    data = await request.json()
    task = BackgroundTask(send_notification, email=data["email"])
    return JSONResponse({"status": "created"}, background=task)
```

## Relationship to FastAPI

[FastAPI](fastapi.md) is a Starlette subclass. When you write a [FastAPI](fastapi.md) app, you are writing a Starlette app with:

- [Pydantic](pydantic.md) models wired to route function parameters for automatic request validation
- [OpenAPI](../../backend/api/openapi.md) schema generated from those models and route signatures
- The `Depends()` [dependency injection](../fundamentals/dependency-injection.md) system layered on top of Starlette's routing
- `HTTPException` mapped to [JSON](../fundamentals/json.md) error responses automatically

Any Starlette `Route`, `Mount`, or [middleware](../../backend/middleware.md) works unchanged inside a [FastAPI](fastapi.md) app. Reading Starlette's source or docs directly is useful when debugging [FastAPI](fastapi.md) [middleware](../../backend/middleware.md) or mounting sub-applications.

## When to Use Starlette Directly

- Building a custom framework on top of [ASGI](../../backend/architecture/asgi.md) primitives
- Writing [ASGI](../../backend/architecture/asgi.md) [middleware](../../backend/middleware.md) that needs to be framework-agnostic
- A very thin proxy or gateway where FastAPI's overhead is unwanted
- Teaching or learning how [ASGI](../../backend/architecture/asgi.md) works at the protocol level

For anything that will grow into a real API service, start with FastAPI — it gives you everything Starlette provides plus validation, docs, and [DI](../fundamentals/dependency-injection.md) for free.

## Related

- [FastAPI](fastapi.md) — built on Starlette; the right default for real API services
- [ASGI](../../backend/architecture/asgi.md) — the async server interface Starlette implements
- [Flask](flask.md) — synchronous (WSGI) alternative; contrast with Starlette's async model
- [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) — comparison overview
- [asyncio](../../backend/architecture/asyncio.md) — Python's async runtime that Starlette and FastAPI run on top of
