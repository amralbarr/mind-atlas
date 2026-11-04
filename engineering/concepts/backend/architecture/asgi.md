# ASGI

ASGI stands for **Asynchronous Server Gateway Interface**. It is the modern successor to **WSGI** in Python.

## Why Was WSGI Created?

In web applications:

```text
Browser
   ↓
Web Server
   ↓
Python Application
```

A standard was needed so web servers could communicate with Python applications. That standard was **WSGI** (Web Server Gateway Interface), used by [Flask](../../programming/python/flask.md) and [Django](../../programming/python/django.md) (traditional mode).

## The Problem With WSGI

WSGI is **synchronous**. Request flow looks like:

```text
Request A → wait DB
Request B → wait
Request C → wait
```

This is not ideal for:

- [WebSockets](../../networking/websockets.md)
- Streaming
- Real-time apps
- High concurrency

## ASGI Solves This

ASGI supports `async` / `await` and allows:

- [HTTP](../../networking/http.md)
- [WebSockets](../../networking/websockets.md)
- [Server-Sent Events](../../protocols/sse.md) (SSE)
- Background async tasks

## Architecture

**WSGI:**

```text
Browser
   ↓
Gunicorn
   ↓
Flask/Django
```

One request handled synchronously.

**ASGI:**

```text
Browser
   ↓
Uvicorn
   ↓
FastAPI
```

Requests can be handled asynchronously.

## Example

[FastAPI](../../programming/python/fastapi.md) route:

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def home():
    await asyncio.sleep(5)
    return {"message": "done"}
```

While waiting on `sleep(5)`, ASGI can process other requests.

## Real Benefit

Imagine 1000 users calling APIs. With async, instead of blocking:

```text
Request 1 waiting on DB
Request 2 running
Request 3 running
Request 4 running
```

## Uvicorn's Role

Uvicorn is an ASGI server. It:

1. Receives [HTTP](../../networking/http.md) requests
2. Talks to [FastAPI](../../programming/python/fastapi.md)
3. Runs [the event loop](../../programming/javascript/event-loop.md)
4. Sends responses back

[FastAPI](../../programming/python/fastapi.md) startup:

```bash
uvicorn main:app --reload
```

Meaning: run the `app` object using the Uvicorn ASGI server.

## ASGI vs WSGI

| Feature | WSGI | ASGI |
| --- | --- | --- |
| Async support | No | Yes |
| [WebSockets](../../networking/websockets.md) | No | Yes |
| Long-lived connections | No | Yes |
| [FastAPI](../../programming/python/fastapi.md) support | No | Yes |
| [Django](../../programming/python/django.md) support | Yes | Yes |
| [Flask](../../programming/python/flask.md) support | Yes | Limited |
| Real-time apps | No | Yes |

## Common ASGI Servers

- **Uvicorn** — most popular for [FastAPI](../../programming/python/fastapi.md).
- **Hypercorn** — alternative ASGI server.
- **Daphne** — used with [Django](../../programming/python/django.md) Channels.

## Common Question

**What is ASGI?**

> ASGI (Asynchronous Server Gateway Interface) is the Python standard for asynchronous communication between web servers and applications. It supports async/await, [WebSockets](../../networking/websockets.md), and high-concurrency applications such as [FastAPI](../../programming/python/fastapi.md).

### Easy Memory Trick

```text
WSGI = Sync Python Web Apps
ASGI = Async Python Web Apps
```

## The Full Stack

Know this stack for AI/backend engineering:

```text
FastAPI
    ↓
ASGI
    ↓
Uvicorn
    ↓
asyncio Event Loop
```

And be able to explain the flow:

```text
async def endpoint
        ↓
await DB/API call
        ↓
event loop switches to another request
        ↓
high concurrency with fewer threads
```

This is one of the most common [FastAPI](../../programming/python/fastapi.md) topics.

## Related

- [Asyncio](asyncio.md)
- [Python for AI Engineering](../../ai/infrastructure/python-ai-engineering.md)
- [Event Loop](../../programming/javascript/event-loop.md)
