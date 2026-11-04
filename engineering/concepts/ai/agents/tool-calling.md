# Function / Tool Calling

## What is it?

Function calling (also called tool calling or tool use) is the mechanism by which an [LLM](../generation/llm.md) can request that a specific external function be executed on its behalf, instead of only producing text. The model itself never runs any code — it can only output text — but it can output *structured text describing an intended function call*, which the calling application then actually executes and feeds the result back in. This is the concrete mechanism that turns a text-in/text-out model into something that can look things up, take actions, and interact with real systems, and it's the foundation the entire [agent harness](ai-agent-harness.md) loop is built on.

```
Model = Model + Harness

Harness gives the model a list of available tools with descriptions.
Model decides (as part of its normal text generation) whether to
respond directly, or to request a tool call.
Harness parses that request, executes the real function, and
feeds the result back into the model's context.
```

## How it works: the request/response shape

1. **Tool definitions are sent with the request.** The caller describes each available tool — name, description, and a [JSON](../../programming/fundamentals/json.md) Schema for its parameters — alongside the prompt.

```json
{
  "name": "get_weather",
  "description": "Get the current weather for a given city",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "City name" },
      "unit": { "type": "string", "enum": ["celsius", "fahrenheit"] }
    },
    "required": ["city"]
  }
}
```

2. **The model decides whether to call a tool**, based on the user's request and the available tool descriptions. If it decides to, instead of returning plain text it returns a structured tool-call request:

```json
{
  "tool_calls": [
    {
      "name": "get_weather",
      "arguments": { "city": "Cairo", "unit": "celsius" }
    }
  ]
}
```

3. **The calling application (the harness) executes the real function** — an actual [HTTP](../../networking/http.md) call, database query, shell command, or any other real system action — using the arguments the model provided.

4. **The result is fed back into the conversation** as a new message (typically a "tool" or "function" role), and the model is called again with that result now part of its context, so it can either call another tool or produce a final natural-language answer.

```
User: "What's the weather in Cairo?"
   ↓
Model: [tool_call: get_weather(city="Cairo", unit="celsius")]
   ↓
Harness executes get_weather() → {"temp": 34, "condition": "sunny"}
   ↓
Model (with result in context): "It's 34°C and sunny in Cairo right now."
```

This request → execute → feed-back → repeat cycle is exactly the loop described in [AI Agent Harness](ai-agent-harness.md) — tool calling is the wire-format mechanism the harness's loop is built around; the harness is the software that actually runs that loop and dispatches the calls.

## Why this is the mechanism agent harnesses are built on

Without tool calling, an [LLM](../generation/llm.md) API call is a single stateless completion: text in, text out, nothing else happens. Tool calling is what makes it possible for a model's output to *cause* something to happen in the outside world — reading a file, querying a database, calling another API, searching the web. Every capability an "AI agent" appears to have beyond conversing — searching, editing, executing, remembering across a session via external storage — routes through this same underlying request/execute/feed-back pattern, whether or not the product calls it "tool calling" explicitly.

## Parallel and multi-step tool calls

Modern models can request multiple tool calls in a single turn (e.g. checking weather for three cities at once), and can chain tool calls across multiple turns — using the result of one call to decide the arguments for the next. This is what enables genuinely multi-step agent behavior (search → read a specific result → summarize) rather than a single fixed pipeline.

## Structured arguments, not free text

The core design choice that makes tool calling reliable is that **arguments are constrained to a schema**, not free-form text the caller has to parse with regex. The model is guided (and increasingly, at the sampling level, constrained) to only produce arguments that validate against the declared [JSON](../../programming/fundamentals/json.md) Schema for that tool — see [Structured Output](../generation/structured-output.md) for how that schema-conformance guarantee is actually enforced under the hood.

## Related

- [AI Agent Harness](ai-agent-harness.md) — the runtime loop that dispatches tool calls, validates them against permissions, and manages the conversation across the loop
- [Model Context Protocol (MCP)](model-context-protocol.md) — a standardized protocol for exposing tools to a model across different applications, rather than each application defining its own ad hoc tool list
- [Structured Output / JSON Mode](../generation/structured-output.md) — the schema-conformance mechanism tool-call arguments rely on
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — frameworks ([LangChain](langchain.md), [LangGraph](langgraph.md)) that wrap tool calling into higher-level agent abstractions
