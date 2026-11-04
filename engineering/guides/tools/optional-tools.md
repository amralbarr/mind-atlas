# Optional Tools

These tools are not required but improve the development experience. Install any that suit your workflow.

## Windows Terminal

A modern terminal emulator for Windows with tabs, split panes, and themes. Supports PowerShell, Command Prompt, WSL2, and [Azure](../../concepts/cloud/azure/azure.md) Cloud Shell in a single window.

**Install:**

```powershell
winget install Microsoft.WindowsTerminal
# Or: Microsoft Store → search "Windows Terminal"
```

**Why use it:** Lets you have PowerShell, WSL2 Ubuntu, and [SSH](../../concepts/protocols/ssh.md) sessions in tabs side by side — avoids juggling multiple windows.

## GitHub CLI (`gh`)

Manage GitHub from the terminal — create pull requests, view issues, check CI status — without opening a browser.

**Install:**

| OS | Method |
|---|---|
| Windows | `winget install GitHub.cli` |
| Mac | `brew install gh` |
| Linux / WSL2 | `sudo apt install gh` |

**Login:**

```bash
gh auth login
```

**Common commands:**

```bash
gh pr create --title "feat: add chunking pipeline" --body "..."
gh pr list
gh pr view <number>
gh issue list
gh repo clone owner/repo
```

## Oh My Zsh

A framework for the Zsh shell that adds themes, plugins, and quality-of-life improvements. Makes the terminal significantly more usable — git branch in the prompt, auto-suggestions, command history search.

Applies to Linux, Mac, and WSL2 only.

**Install Zsh first (WSL2/Linux):**

```bash
sudo apt install zsh
```

**Install Oh My Zsh:**

```bash
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

**Useful plugins (add to `~/.zshrc`):**

```
plugins=(git docker terraform python zsh-autosuggestions)
```

## DBeaver (Database GUI)

A free, universal database GUI client. Use it to inspect the [PostgreSQL](../../concepts/databases/relational/postgresql.md) database that backs Nextcloud — browse tables, run queries, and verify data without command-line [SQL](../../concepts/databases/relational/sql.md).

**Install:** Download from https://dbeaver.io/download/ (Community Edition — free).

**Connect to [PostgreSQL](../../concepts/databases/relational/postgresql.md) in [Docker](../../concepts/containers/docker.md):**

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` (or whichever port is mapped in [docker](../../concepts/containers/docker.md)-compose) |
| Database | `nextcloud` |
| Username | from your `.env` |
| Password | from your `.env` |

> Only use this for local development. Never expose the database port on the production server.

## Ollama (Local LLM)

Runs [large language models](../../concepts/ai/generation/llm.md) locally on your machine — no [API key](../../concepts/security/auth/api-key.md), no internet, no cost. Useful for testing the [RAG](../../concepts/ai/rag/rag.md) pipeline's [LLM](../../concepts/ai/generation/llm.md) integration without spending money on OpenAI API calls.

**Install:** Download from https://ollama.com/download.

**Pull and run a model:**

```bash
ollama pull llama3        # download Llama 3 (4.7 GB)
ollama run llama3         # start interactive chat
ollama serve              # start as a local API server on port 11434
```

**Use as a drop-in for the OpenAI API (local):**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",   # required by the library, value is ignored
)

response = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Summarize this document..."}]
)
```

**Minimum hardware:** 8 GB RAM for 7B models; 16 GB RAM for 13B models. Uses CPU if no GPU is available (slower but works).

## Tips
- Windows Terminal + WSL2 is the recommended local terminal setup for Windows users.
- `gh` CLI saves significant time when working with pull requests daily.
- Ollama is valuable for offline [RAG](../../concepts/ai/rag/rag.md) testing — run the full pipeline without an internet connection or API costs.

## Related
- [local-development-tools.md](local-development-tools.md)
- [development-workflow.md](development-workflow.md)
- [vscode.md](vscode.md)
