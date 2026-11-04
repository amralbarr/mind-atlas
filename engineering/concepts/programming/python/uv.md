# uv

uv is an extremely fast Python package and project manager, written in Rust by [Astral](https://astral.sh) (the same team behind the `ruff` linter). It's designed as a single drop-in replacement for the fragmented Python tooling stack — `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, and `virtualenv` — unifying dependency resolution, virtual environments, Python version management, and packaging into one tool and one command-line interface.

## Why uv Instead of pip/poetry

| Problem with the old stack | What uv does about it |
|---|---|
| `pip` has no lockfile — installs aren't reproducible across machines | `uv lock` generates a lockfile (`uv.lock`) pinning every resolved dependency |
| Managing virtual envs, Python versions, and packages needs 3+ separate tools (`venv`, `pyenv`, `pip`) | One tool handles all three: `uv venv`, `uv python install`, `uv add` |
| `pip install` and `poetry install` are slow, especially on cold cache | uv's resolver and installer are 10–100x faster than pip, and roughly 10x faster than Poetry, in Astral's benchmarks |
| Poetry has its own non-standard `pyproject.toml` dependency format (in older versions) | uv uses the standard PEP 621 `[project]` table in `pyproject.toml` |

## Core Concepts

| Term | Meaning |
|---|---|
| **`pyproject.toml`** | Standard Python project metadata + dependency declarations (PEP 621) |
| **`uv.lock`** | The lockfile uv generates — pins exact resolved versions for reproducible installs across machines |
| **Project mode** | `uv init`/`uv add`/`uv run` manage a full project (like Poetry) — creates and maintains a `.venv` automatically |
| **`pip` interface** | `uv pip install`/`uv pip compile` — a drop-in faster replacement for existing pip-based workflows, without adopting project mode |
| **Tool mode (`uvx`)** | Run a CLI tool from PyPI in an ephemeral, isolated environment without installing it into your project — analogous to `npx` |

## Installation

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip / pipx / Homebrew
pipx install uv
brew install uv
```

## Starting a New Project

```bash
uv init my-project
cd my-project
```

This scaffolds a `pyproject.toml` and a starter file. A `.venv` is created automatically the first time you add a dependency or run something.

## Adding and Managing Dependencies

```bash
uv add fastapi uvicorn          # adds to pyproject.toml, resolves, updates uv.lock, installs
uv add pytest --dev             # dev-only dependency
uv remove uvicorn

uv sync                          # install exactly what uv.lock specifies (e.g. after cloning a repo)
uv lock                          # (re)generate uv.lock without installing
```

`uv sync` is the command you run after `git clone` — it creates the `.venv` and installs the exact locked versions, the same role `npm ci` plays for Node.js.

## Running Code in the Project Environment

```bash
uv run python main.py
uv run pytest
uv run uvicorn main:app --reload
```

`uv run` executes a command inside the project's virtual environment without needing to manually `source .venv/bin/activate` first — uv resolves and syncs the environment on the fly if it's out of date.

## Python Version Management

```bash
uv python install 3.12          # download and install a specific Python version
uv python pin 3.12              # pin this project to that version (writes .python-version)
uv venv --python 3.12           # create a venv with a specific Python version
```

This replaces `pyenv` for most workflows — uv downloads and manages standalone Python builds itself.

## Drop-in pip Replacement (No Project Mode)

For existing projects using a plain `requirements.txt` workflow, uv can be used as a faster pip without adopting the lockfile/project model at all:

```bash
uv venv                                    # create a .venv
uv pip install -r requirements.txt         # much faster than `pip install -r ...`
uv pip compile requirements.in -o requirements.txt   # like pip-tools
```

## Installing Standalone CLI Tools

```bash
uvx ruff check .                # run a tool once, ephemeral env, no install
uv tool install ruff            # install it persistently, available as a global command
```

## uv vs Alternatives

| | uv | pip | Poetry | pyenv |
|---|---|---|---|---|
| Speed | 10–100x faster than pip | Baseline | Slower than uv | N/A (not a package manager) |
| Lockfile | Yes (`uv.lock`) | No (needs pip-tools) | Yes (`poetry.lock`) | N/A |
| Python version management | Yes (`uv python install`) | No | No | Yes (its whole purpose) |
| Virtual env management | Built in | Manual (`venv`) | Built in | N/A |
| `pyproject.toml` format | Standard PEP 621 | N/A | Own `[tool.poetry]` table (legacy) or PEP 621 (newer) | N/A |
| Publish to PyPI | Yes (`uv build`, `uv publish`) | No | Yes | N/A |

## Related Concepts

- [Python Overview](../../../overviews/programming/python-overview.md) — where uv sits in the broader Python tooling landscape
- [Python for AI Engineering](../../ai/infrastructure/python-ai-engineering.md) — virtual environments as a core Python fundamental for AI/backend work
- [ASGI](../../backend/architecture/asgi.md) — `uv run uvicorn ...` is a common way to launch a [FastAPI](fastapi.md) app during development
