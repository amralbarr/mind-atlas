# FastAPI

FastAPI is a modern Python web framework built for building APIs quickly — async-native, type-hint-driven, and the current default choice for AI startups and [LLM](../../ai/generation/llm.md)-serving backends, in large part because it generates interactive [OpenAPI](../../backend/api/openapi.md) documentation and request validation automatically from ordinary Python type hints. See [Python Overview](../../../overviews/programming/python-overview.md) for how it fits alongside the rest of the Python ecosystem, and [NestJS Overview](../../backend/nestjs/nestjs-overview.md) for the closest equivalent in the Node.js ecosystem.

## Core Concepts

| Term | Meaning |
|---|---|
| **Path operation** | A function decorated with `@app.get`/`@app.post`/etc., mapping an [HTTP](../../networking/http.md) route to a handler |
| **[Pydantic](pydantic.md) model** | A typed class defining a request/response shape — FastAPI uses it to validate incoming data and serialize outgoing data automatically |
| **[Dependency injection](../fundamentals/dependency-injection.md)** | FastAPI's `Depends()` system — shared logic (DB sessions, auth checks) declared once and injected into any route that needs it |
| **Automatic [OpenAPI](../../backend/api/openapi.md) docs** | FastAPI introspects route signatures and [Pydantic](pydantic.md) models to generate a live, interactive API doc (Swagger UI at `/docs`) with zero manual annotation |
| **[ASGI](../../backend/architecture/asgi.md)** | FastAPI is built on the [ASGI](../../backend/architecture/asgi.md) standard (via [Starlette](starlette.md)), which is what makes native `async def` route handlers possible, unlike WSGI-based frameworks like [Flask](flask.md)/[Django](django.md) (pre-async support) |

## Installation

```bash
pip install fastapi uvicorn[standard]
```

`uvicorn` is the [ASGI](../../backend/architecture/asgi.md) server that actually runs a FastAPI app — FastAPI itself is just the framework, not a server.

## A Minimal API

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    item: str
    quantity: int

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    return {"order_id": order_id}

@app.post("/orders")
async def create_order(order: Order):
    return {"item": order.item, "quantity": order.quantity, "status": "created"}
```

```bash
uvicorn main:app --reload
```

Requesting `/docs` immediately shows an interactive UI for both routes, generated entirely from the type hints above — no separate [OpenAPI](../../backend/api/openapi.md) spec to hand-write or keep in sync.

## Dependency Injection

```python
from fastapi import Depends

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/orders")
async def list_orders(db=Depends(get_db)):
    return db.query(OrderModel).all()
```

`get_db` runs once per request, and its cleanup code (`db.close()`) runs after the response is sent — the same request-scoped lifecycle pattern [dependency injection](../fundamentals/dependency-injection.md) provides in other frameworks (see [Dependency Injection](../fundamentals/dependency-injection.md)).

## A Streaming Response (Common for LLM Output)

```python
from fastapi.responses import StreamingResponse

@app.get("/chat")
async def chat(query: str):
    async def token_stream():
        async for token in call_llm_streaming(query):
            yield token
    return StreamingResponse(token_stream(), media_type="text/event-stream")
```

This is the common shape behind an [LLM](../../ai/generation/llm.md) chat endpoint that streams tokens to the client as they're generated, rather than waiting for the full response — see [Server-Sent Events](../../protocols/sse.md) for the underlying protocol this pattern typically uses.

## JWT Authentication

The standard pattern: a `get_current_user` dependency that validates the access token, injected into any protected route.

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "your-secret"   # load from env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- Token helpers ---

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    payload = data | {"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- Dependency (guard) ---

class TokenData(BaseModel):
    user_id: str
    roles: list[str] = []

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
        return TokenData(user_id=user_id, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_error


# --- Routes ---

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await verify_user(form.username, form.password)   # your DB lookup
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = create_access_token({"sub": str(user.id), "roles": user.roles})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    return {"user_id": current_user.user_id, "roles": current_user.roles}
```

**Role guard** — extend `get_current_user` with a role check via a closure:

```python
def require_role(role: str):
    async def guard(user: TokenData = Depends(get_current_user)) -> TokenData:
        if role not in user.roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return guard

@app.delete("/documents/{doc_id}")
async def delete_doc(doc_id: str, user: TokenData = Depends(require_role("admin"))):
    ...
```

**Refresh token endpoint** — refresh tokens are long-lived opaque tokens stored in the DB (see [Access Token + Refresh Token Pattern](../../security/auth/access-refresh-tokens.md)):

```python
from fastapi import Cookie

@app.post("/auth/refresh")
async def refresh(refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    record = await db.refresh_tokens.find_valid(refresh_token)  # hash + active check
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")
    await db.refresh_tokens.rotate(record)   # invalidate old, issue new
    new_access = create_access_token({"sub": record.user_id, "roles": record.roles})
    return {"access_token": new_access, "token_type": "bearer"}
```

## Common Questions

**Why is FastAPI specifically favored for AI/[LLM](../../ai/generation/llm.md) backends over [Flask](flask.md) or [Django](django.md)?**
> Native `async def` support matters directly for AI workloads, which spend most of their time waiting on [I/O](../fundamentals/io.md) (calling an [LLM](../../ai/generation/llm.md) API, a [vector database](../../ai/retrieval/vector-database.md), an external service) rather than doing CPU-bound work — async handlers let one process handle many concurrent waiting requests efficiently. [Flask](flask.md)/[Django](django.md) historically ran on WSGI (blocking, one thread per request by default), though both have since added partial async support.

**Does FastAPI replace the need for [Pydantic](pydantic.md) knowledge?**
> No — [Pydantic](pydantic.md) is a separate library FastAPI is built around, not something FastAPI reimplements. Understanding [Pydantic](pydantic.md) models (validation, [serialization](../fundamentals/serialization.md), nested models) directly transfers to using FastAPI well, and [Pydantic](pydantic.md) is equally useful outside FastAPI for structured [LLM](../../ai/generation/llm.md) output validation — see [Structured Output](../../ai/generation/structured-output.md).

## Related

- [OpenAPI / Swagger](../../backend/api/openapi.md) — the spec FastAPI generates automatically: spec structure, Swagger UI vs ReDoc, client generation, contract testing
- [Python Web Frameworks](../../../overviews/programming/python-web-frameworks.md) — comparison of FastAPI, [Flask](flask.md), [Django](django.md), [Starlette](starlette.md), and alternatives
- [Python Overview](../../../overviews/programming/python-overview.md)
- [NestJS Overview](../../backend/nestjs/nestjs-overview.md)
- [ASGI](../../backend/architecture/asgi.md)
- [Dependency Injection](../fundamentals/dependency-injection.md)
- [asyncio](../../backend/architecture/asyncio.md)
- [Pydantic](pydantic.md) — FastAPI is built on [Pydantic](pydantic.md); every request/response body is a Pydantic model
- [Structured Output](../../ai/generation/structured-output.md)
- [JWT](../../security/auth/jwt.md)
- [Access Token + Refresh Token Pattern](../../security/auth/access-refresh-tokens.md)
- [JWT vs API Key](../../../overviews/security/jwt-vs-api-key.md)
