# AutoGen

AutoGen, created by Microsoft, is a framework for building [multi-agent systems](multi-agent-systems.md) around **agent-to-agent conversation** — agents exchange messages with each other (and optionally a human) in a structured chat loop, rather than one central process explicitly calling each agent in sequence. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [CrewAI](crewai.md) and [LangGraph](langgraph.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **ConversableAgent** | AutoGen's base agent class — any agent ([LLM](../generation/llm.md)-backed, human-backed, or code-executing) that can send and receive messages |
| **AssistantAgent** | An [LLM](../generation/llm.md)-backed agent that generates responses/code based on the conversation |
| **UserProxyAgent** | Represents a human or an automated executor — can relay human input, or automatically execute code the assistant produces and report results back into the conversation |
| **GroupChat** | Coordinates a conversation among more than two agents, with a manager deciding which agent speaks next each turn |
| **Human-in-the-loop** | `UserProxyAgent` can be configured to pause for real human input at each turn, only occasionally, or never (fully autonomous) |

## A Two-Agent Conversation

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="coder",
    llm_config={"model": "gpt-4o", "api_key": "..."},
)

user_proxy = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",              # fully autonomous
    code_execution_config={"work_dir": "coding", "use_docker": False},
)

user_proxy.initiate_chat(
    assistant,
    message="Write a Python function that reverses a string, then test it.",
)
```

`user_proxy` here automatically executes any code `assistant` produces and reports the result (success, error, output) back into the conversation — the assistant can then fix its own code based on that feedback, without a human relaying results manually.

## A Multi-Agent Group Chat

```python
from autogen import GroupChat, GroupChatManager

reviewer = AssistantAgent(name="reviewer", llm_config={"model": "gpt-4o"}, system_message="You review code for bugs.")

group_chat = GroupChat(agents=[user_proxy, assistant, reviewer], messages=[], max_round=10)
manager = GroupChatManager(groupchat=group_chat, llm_config={"model": "gpt-4o"})

user_proxy.initiate_chat(manager, message="Build and review a function that validates an email address.")
```

The `GroupChatManager` decides which agent responds next each round — `coder` writes, `reviewer` critiques, `coder` revises — without the calling code hardcoding that sequence.

## Common Questions

**How does AutoGen differ from [CrewAI](crewai.md)?**
> AutoGen models collaboration as an open-ended, [LLM](../generation/llm.md)-mediated *conversation* between agents (including automatic code execution), which suits research/experimentation and dynamic problem-solving. [CrewAI](crewai.md) models collaboration as a more structured set of predefined *roles and tasks* handed off in sequence, which suits production workflows where the division of labor is known ahead of time.

**Does AutoGen require a human in the loop?**
> No — `human_input_mode="NEVER"` makes a conversation fully autonomous, useful for automated pipelines. Setting it to `ALWAYS` or `TERMINATE` (only ask at natural stopping points) is what enables genuine human-in-the-loop review for higher-stakes workflows.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [CrewAI](crewai.md)
- [LangGraph](langgraph.md)
- [Multi-Agent Systems](multi-agent-systems.md)
