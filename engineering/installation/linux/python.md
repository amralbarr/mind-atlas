# Installing Python (Linux)

## What Is It?

Python is a high-level, general-purpose programming language widely used for data science, AI/ML, web development, and automation. It is the standard language for building AI pipelines — document processing, [embeddings](../../concepts/ai/ingestion/embeddings.md), vector search, and [LLM](../../concepts/ai/generation/llm.md) integration.

## Install

| OS | Method |
|---|---|
| Windows | Download from https://www.python.org/downloads/ — check **"Add Python to PATH"** during install |
| Mac | `brew install python@3.11` |
| Linux / WSL2 | `sudo apt install python3.11 python3.11-venv python3-pip` |

**Verify:**

```bash
python3 --version    # should show 3.11.x or higher
pip3 --version
```

> **Minimum version:** Python 3.11. Do not use Python 3.9 or earlier — some libraries require 3.10+.

## Virtual Environments

Always use a virtual environment. Never install packages globally — it causes version conflicts between projects.

```bash
# Create a virtual environment in the project folder
python3 -m venv .venv

# Activate
source .venv/bin/activate          # Linux / Mac / WSL2
.venv\Scripts\activate             # Windows Command Prompt
.venv\Scripts\Activate.ps1         # Windows PowerShell

# Verify you are inside the venv (prompt shows (.venv))
which python    # should point to .venv/bin/python

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## Managing Dependencies

```bash
# Install a package
pip install requests

# Install from a requirements file
pip install -r requirements.txt

# Save current environment to a requirements file
pip freeze > requirements.txt

# Upgrade a package
pip install --upgrade openai

# List installed packages
pip list
```

## `requirements.txt` Template

A clean starting point for a Python AI / [RAG](../../concepts/ai/rag/rag.md) project:

```
# Document extraction
pymupdf>=1.23.0          # PDF text extraction
python-docx>=1.1.0       # Word document extraction

# HTTP / API calls
requests>=2.31.0

# Embeddings
sentence-transformers>=2.7.0   # local embedding models
openai>=1.30.0                 # OpenAI API (embeddings + LLM)

# Vector store — choose one
chromadb>=0.5.0                # simple local vector store
# faiss-cpu>=1.8.0             # faster, Meta's library

# Web interface — choose one (optional)
flask>=3.0.0
# fastapi>=0.111.0
# uvicorn>=0.30.0

# Utilities
python-dotenv>=1.0.0     # load .env files
tqdm>=4.66.0             # progress bars
```

## Loading `.env` Files

Never hardcode secrets. Use `python-dotenv` to load from a `.env` file:

```python
from dotenv import load_dotenv
import os

load_dotenv()   # reads .env from the current directory

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

## `.gitignore` Entries for Python

```gitignore
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
```

## Tips

- Always activate your virtual environment before running any Python command.
- Commit `requirements.txt` to Git — not the `.venv/` folder.
- Use `python-dotenv` for secrets — never hardcode API keys.
- Run `pip install --upgrade pip` after creating a new venv.

## Related
- [../../concepts/containers/docker.md](../../concepts/containers/docker.md)
- [../../guides/tools/local-development-tools.md](../../guides/tools/local-development-tools.md)
