# Model Context Protocol (MCP)

## What is it?

The **Model Context Protocol (MCP)** is an open, standardized protocol — introduced by Anthropic in November 2024 — for connecting [LLMs](../generation/llm.md) to external tools, data sources, and services. Before MCP, every application that wanted to give a model access to, say, GitHub, Slack, or a database had to build and maintain its own bespoke integration for each one. MCP standardizes that connection into a single protocol, so a tool provider builds one MCP server and any MCP-compatible application (any model, any harness) can use it, instead of an N×M matrix of custom integrations between every app and every tool.

The often-used framing: MCP is "a USB-C port for AI applications" — a common connector, not a specific integration.

## Why it matters here

[Function/tool calling](tool-calling.md) is the mechanism an [LLM](../generation/llm.md) uses to request that a tool run — but [tool calling](tool-calling.md) alone says nothing about *where tool definitions come from* or *how they're discovered and connected*. MCP answers that: it's the standardized layer for exposing a set of tools (and data sources) to a model in a way that works the same regardless of which application or [agent harness](ai-agent-harness.md) is doing the calling. In effect, MCP is to "connecting an agent to tools/data" what [HTTP](../../networking/http.md) is to "connecting a browser to a website" — a shared protocol instead of a one-off integration per pair.

## Architecture

MCP uses a **client-server architecture** built on [JSON](../../programming/fundamentals/json.md)-RPC 2.0:

```
Host application (e.g. Claude Code, an IDE, a chat app)
   │
   ├── MCP Client session ──── MCP Server (e.g. GitHub)
   ├── MCP Client session ──── MCP Server (e.g. Postgres)
   └── MCP Client session ──── MCP Server (e.g. Slack)
```

- **Host** — the application the user actually interacts with (an IDE, a chat client, an agent harness). It creates and owns one or more client sessions.
- **MCP Client** — lives inside the host, maintains a stateful connection to exactly one MCP server.
- **MCP Server** — a lightweight program that exposes a specific system's capabilities — tools, data resources, and prompt templates — through the standardized protocol. A GitHub MCP server exposes GitHub operations; a Postgres MCP server exposes query capabilities; each server only knows about its own system, and doesn't need to know anything about the model or application connecting to it.

**Transports** — MCP supports two ways for a client and server to actually exchange messages:
- **Stdio** — standard [input/output](../../programming/fundamentals/io.md) between two local processes on the same machine (common for local tools like a filesystem or local database server).
- **Streamable [HTTP](../../networking/http.md)** — [HTTP](../../networking/http.md) POST for client→server messages, with optional [Server-Sent Events](../../protocols/sse.md) for streaming responses (used for remote/hosted servers).

## What an MCP server exposes

| Primitive | What it is |
|---|---|
| **Tools** | Functions the model can invoke — the same request/execute/respond pattern described in [Tool Calling](tool-calling.md), but discovered and connected through the standardized MCP interface rather than hardcoded per application |
| **Resources** | Read-only data the host can pull into context — files, database records, API responses |
| **Prompts** | Reusable prompt templates a server can offer to guide how it's used |

## Current status (2026)

MCP has been adopted well beyond Anthropic — OpenAI, Google DeepMind, Microsoft, and [AWS](../../cloud/infrastructure/aws.md) all support it, and the ecosystem includes MCP servers for most major developer tools and SaaS platforms (GitHub, Slack, Google Drive, Postgres, Notion, Jira, Salesforce, and hundreds more). In December 2025, Anthropic donated MCP to the Agentic AI Foundation under the Linux Foundation, making it a vendor-neutral, community-governed standard rather than an Anthropic-owned one.

## MCP vs. plain tool calling

| | Plain function/[tool calling](tool-calling.md) | MCP |
|---|---|---|
| **Scope** | A single application defines its own tool list for its own model calls | A standardized protocol any application can speak to any compliant server |
| **Reuse** | Each app rebuilds its own integration to, say, GitHub | One GitHub MCP server can be used by every MCP-compatible host |
| **Discovery** | The application hardcodes what tools exist | Clients can query a server for its available tools/resources/prompts at connection time |

MCP doesn't replace [tool calling](tool-calling.md) — it standardizes how the tools available for calling are packaged, discovered, and connected across applications.

## Related

- [Function / Tool Calling](tool-calling.md) — the underlying request/execute/respond mechanism MCP standardizes access to
- [AI Agent Harness](ai-agent-harness.md) — the harness is the "host" that manages MCP client sessions and dispatches calls to servers
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — frameworks that increasingly support MCP as a way to wire in tools rather than defining them ad hoc
