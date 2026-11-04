# Flask

Flask is Python's original lightweight micro web framework — routing, request/response handling, and a development server are the core; everything else ([ORM](../../backend/data/orm.md), validation, auth, migrations) is deliberately left out or added via extensions. WSGI-based and blocking by default, with partial async view support added in Flask 2.0. It was the go-to Python web framework for a decade before [FastAPI](fastapi.md) arrived, and it remains dominant by installed base, particularly in internal tools, prototypes, and codebases that predate async becoming mainstream. For new API work, [FastAPI](fastapi.md) has largely superseded it. See [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) for a full comparison.

## Core Concepts

| Term | Meaning |
|---|---|
| **App object** | `Flask(__name__)` — the central application instance; routes, config, and extensions all attach to it |
| **Route** | `@app.route("/path", methods=["GET", "POST"])` — binds a URL pattern to a view function |
| **View function** | A plain Python function that returns a response; no type-driven validation — return a dict, a string, a `Response`, or a `render_template()` call |
| **Blueprint** | A sub-application object for organizing routes into modules; imported and registered on the main app |
| **Application context** | The `g` object and `current_app` proxy — request-scoped and app-scoped state available inside view functions without passing it explicitly |
| **Request context** | `flask.request` — the current [HTTP](../../networking/http.md) request, available as a thread-local proxy inside any active request |
| **`flask.g`** | Per-request scratch space — store a DB connection or current user once per request, share across helpers |

## Installation

```bash
pip install flask
```

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/echo")
def echo():
    data = request.get_json()
    return jsonify(data)
```

```bash
flask --app main run --reload
```

## Blueprints (Organizing a Larger App)

```python
# orders/routes.py
from flask import Blueprint, jsonify

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.get("/")
def list_orders():
    return jsonify([])

# main.py
from flask import Flask
from orders.routes import orders_bp

app = Flask(__name__)
app.register_blueprint(orders_bp)
```

## Key Extensions

| Extension | Purpose |
|---|---|
| **Flask-SQLAlchemy** | SQLAlchemy [ORM](../../backend/data/orm.md) integration — session management, model base class |
| **Flask-Migrate** | Alembic-based DB migrations for Flask-SQLAlchemy models |
| **flask-smorest** | [OpenAPI](../../backend/api/openapi.md) 3 docs + request validation via marshmallow schemas |
| **Flask-[JWT](../../security/auth/jwt.md)-Extended** | [JWT](../../security/auth/jwt.md) access + refresh token auth |
| **Flask-Login** | Session-based auth (user object, `@login_required`) |
| **Flask-[CORS](../../security/attacks/cors.md)** | [Cross-origin resource sharing](../../security/attacks/cors.md) headers |
| **[Celery](../../distributed-systems/messaging/celery.md)** | Background tasks (not a Flask extension, but commonly wired with the app context) |

## Async Views (Flask 2.0+)

Flask 2.0 introduced `async def` views, but the underlying server is still WSGI. An `async def` view runs in a thread-local [event loop](../javascript/event-loop.md) per request — it does not give you true concurrency across requests the way [ASGI](../../backend/architecture/asgi.md) frameworks do. For genuinely concurrent async [I/O](../fundamentals/io.md) across many simultaneous requests, [ASGI](../../backend/architecture/asgi.md) + [FastAPI](fastapi.md) or [Starlette](starlette.md) is the correct choice.

```python
import asyncio
from flask import Flask

app = Flask(__name__)

@app.get("/slow")
async def slow():
    await asyncio.sleep(1)   # yields within this request, but doesn't free the thread for other requests
    return {"done": True}
```

## When to Use Flask

- Small internal tools or scripts exposed as [HTTP](../../networking/http.md) endpoints
- Teams with existing Flask expertise and no immediate need to rewrite
- Prototypes where simplicity matters more than performance
- Legacy codebases already on Flask with extensive extension integrations

## When to Use Something Else

- New API project with async [I/O](../fundamentals/io.md) ([LLM](../../ai/generation/llm.md) calls, DB calls, vector search) — use [FastAPI](fastapi.md)
- Full-stack web app with [ORM](../../backend/data/orm.md), admin, and auth — use [Django](django.md)
- Raw [ASGI](../../backend/architecture/asgi.md) [middleware](../../backend/middleware.md) or framework building — use [Starlette](starlette.md)

## Related

- [FastAPI](fastapi.md) — Flask's async-native successor for API work
- [Django](django.md) — full-stack Python framework with [ORM](../../backend/data/orm.md), admin, and auth
- [Starlette](starlette.md) — [ASGI](../../backend/architecture/asgi.md) toolkit, underlies [FastAPI](fastapi.md)
- [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) — comparison overview
- [Python Overview](../../../overviews/programming/python-overview.md)
- [Dependency Injection](../fundamentals/dependency-injection.md)
