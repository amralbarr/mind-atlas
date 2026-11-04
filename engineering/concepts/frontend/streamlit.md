# Streamlit

Streamlit is an open-source Python framework for building interactive data apps and internal tools — no HTML, CSS, or JavaScript required. You write a Python script; Streamlit renders it as a web UI and re-runs the script top-to-bottom on every user interaction.

## When to Use Streamlit

| Good fit | Poor fit |
|---|---|
| Data dashboards & exploration | Production-grade public-facing apps |
| ML model demos & prototypes | Complex multi-page apps with auth flows |
| Internal tooling | High-traffic or real-time streaming UIs |
| [RAG](../ai/rag/rag.md) / AI chat interfaces | Apps needing fine-grained JS control |

## Core Mental Model

```text
User interaction → full script re-run → UI update
```

Every widget call (slider, button, text input) returns a value. When the user changes a widget, Streamlit re-executes the entire script with the new value. Use `st.session_state` to persist data across re-runs.

## Installation

```bash
pip install streamlit
```

Run an app:

```bash
streamlit run app.py
```

## Basic App Structure

```python
import streamlit as st

st.title("My App")

name = st.text_input("Your name")
if name:
    st.write(f"Hello, {name}!")

number = st.slider("Pick a number", 0, 100, 50)
st.write(f"You picked: {number}")
```

## Common Widgets

```python
# Input
st.text_input("label")
st.number_input("label", min_value=0)
st.selectbox("label", ["option1", "option2"])
st.multiselect("label", options)
st.checkbox("label")
st.button("Click me")
st.file_uploader("Upload", type=["csv", "pdf"])

# Display
st.write(anything)          # smart renderer (text, df, chart)
st.dataframe(df)
st.table(df)
st.json(dict)
st.code("...", language="python")
st.image("path_or_url")
st.metric("label", value, delta)

# Layout
col1, col2 = st.columns(2)
with col1:
    st.write("left")

with st.expander("More details"):
    st.write("hidden until expanded")

with st.sidebar:
    st.selectbox("Filter", options)
```

## Session State (Persist Data Across Re-runs)

```python
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write(st.session_state.count)
```

## Caching (Avoid Re-running Expensive Operations)

```python
@st.cache_data           # for data / pure functions (serializable output)
def load_data(path):
    return pd.read_csv(path)

@st.cache_resource       # for connections, models (non-serializable, shared)
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))
```

`cache_data` caches per-argument and is safe to reuse across users.  
`cache_resource` creates one shared instance — use for DB connections and ML models.

## Connecting to PostgreSQL

```python
import streamlit as st
import psycopg2
import os

@st.cache_resource
def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

conn = get_conn()
df = pd.read_sql("SELECT * FROM records LIMIT 100", conn)
st.dataframe(df)
```

## Connecting to a FastAPI Backend

Streamlit can act as a frontend calling a [FastAPI](../programming/python/fastapi.md) service:

```python
import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

query = st.text_input("Search")
if query:
    resp = httpx.get(f"{API_URL}/search", params={"q": query})
    st.json(resp.json())
```

## Chat / RAG Interface Pattern

```python
st.title("Ask the docs")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call your RAG pipeline here
    answer = rag_pipeline(prompt)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
```

## Environment Variables

Never hardcode secrets. Use `.env` + `python-dotenv` or Streamlit Secrets:

```toml
# .streamlit/secrets.toml  (gitignored)
DATABASE_URL = "postgresql://user:pass@localhost/db"
OPENAI_API_KEY = "sk-..."
```

```python
import streamlit as st
db_url = st.secrets["DATABASE_URL"]
```

Or with `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("DATABASE_URL")
```

## Multi-Page Apps

```
app/
├── app.py               # entry point (st.Page / st.navigation)
└── pages/
    ├── 1_Dashboard.py
    ├── 2_Upload.py
    └── 3_Settings.py
```

```python
# app.py
import streamlit as st

pg = st.navigation([
    st.Page("pages/1_Dashboard.py", title="Dashboard"),
    st.Page("pages/2_Upload.py", title="Upload"),
])
pg.run()
```

## Deployment

| Target | Command / Notes |
|---|---|
| Local dev | `streamlit run app.py` |
| [Docker](../containers/docker.md) | `EXPOSE 8501` + `CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]` |
| Streamlit Community Cloud | Push to GitHub → connect repo at share.streamlit.io |
| Self-hosted ([reverse proxy](../networking/reverse-proxy.md)) | [Nginx](../backend/api-gateways/nginx.md) → `localhost:8501`, set `server.headless = true` |

### Minimal Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Related Concepts

- [FastAPI](../backend/architecture/asgi.md) — use as the API layer behind Streamlit
- [Vector Databases](../ai/retrieval/vector-database.md) — Chroma, pgvector for [RAG](../ai/rag/rag.md) apps
- [Object Storage](../cloud/infrastructure/object-storage.md) — MinIO for file uploads
- [python-dotenv / .env](../../installation/linux/python.md) — secret management
