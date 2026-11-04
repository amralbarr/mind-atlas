# Python Assistant API — Runnable Example

A real, runnable version of the six-layer architecture described in
[the deep-dive writeup](../../interview/interview-01/20-python-assistant-api-deep-dive.md)
(companion to [How would you structure a Python assistant API?](../../interview/interview-01/07-python-api.md)).

This project exists to make that writeup's code **runnable and testable**, not just
readable — the markdown docs explain the *why*, this folder is the actual *what*.

## Layout

```
python-assistant-api/
├── main.py                 # app creation and connection lifecycle
├── api/
│   └── routes.py            # the /ask endpoint (thin: formatting only)
├── schemas.py               # request/response models (Pydantic)
├── auth.py                  # authentication and authorization
├── services/
│   ├── interfaces.py         # interfaces (Protocols)
│   ├── retriever.py          # a real search implementation (illustrative)
│   ├── llm.py                # a real model implementation (illustrative)
│   └── evidence.py           # evidence validation
├── pipeline.py              # wires the layers together
└── tests/
    ├── fakes.py               # fake implementations for testing
    └── test_ask.py
```

## Run the tests

```bash
cd code-samples/python-assistant-api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
```

All three tests run entirely against `tests/fakes.py` — no real search engine or
model endpoint required, fast and deterministic.

## Run the server

```bash
.venv/bin/uvicorn main:app --reload
```

This starts the real app with `SearchRetriever`/`AzureLLMClient` wired to
`SEARCH_BASE_URL`/`MODEL_BASE_URL` (see `services/retriever.py` and `services/llm.py`) —
point those at real endpoints to make `/ask` functional end to end. Without that,
the server starts and the dependency-injection wiring is correct, but an actual
`/ask` call will fail against whatever those URLs default to.

## Concepts this project demonstrates

- [Dependency Injection](../../concepts/programming/fundamentals/dependency-injection.md) — `services/interfaces.py`'s Protocols, swapped for fakes in tests
- [Connection Pooling](../../concepts/databases/relational/connection-pooling.md) — the shared `httpx.AsyncClient` created once in `main.py`'s lifespan
- [Authentication](../../concepts/security/auth/authentication.md) / [Authorization](../../concepts/security/authorization/authorization.md) — `auth.py`'s `get_current_user` dependency
- [Retrieval Metrics](../../concepts/ai/evaluation/retrieval-metrics.md) — the abstention pattern in `pipeline.py`
- [Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md) — what `services/retriever.py` would call in a real deployment
- [FastAPI](../../concepts/programming/python/fastapi.md) / [Pydantic](../../concepts/programming/python/pydantic.md)

## Related

- [Python Assistant API Deep Dive](../../interview/interview-01/20-python-assistant-api-deep-dive.md) — the full writeup this project implements
- [How would you structure a Python assistant API?](../../interview/interview-01/07-python-api.md) — the short-form interview answer
