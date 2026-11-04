# CrewAI

CrewAI is a framework for role-based multi-agent orchestration — each agent is defined with a job title, a goal, and a set of tools, tasks are assigned to specific agents, and a **crew** runs them as a coordinated team, closer to how a human team divides labor by role than to [AutoGen](autogen.md)'s open-ended conversation model. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [AutoGen](autogen.md) and [LangGraph](langgraph.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **Agent** | An [LLM](../generation/llm.md)-powered worker defined by a `role` (job title), `goal` (what it's trying to achieve), an optional `backstory` (system-prompt enrichment shaping its behavior/tone), and a set of `tools` |
| **Task** | A unit of work assigned to a specific agent, with an expected output description |
| **Crew** | The full team — a set of agents and tasks assembled together, plus a `process` defining how work flows between them |
| **Process** | `sequential` (tasks run in order, each getting prior tasks' output as context) or `hierarchical` (a manager agent delegates and reviews) |
| **Tool** | A function an agent can call (web search, a calculator, a custom API) — same underlying idea as [tool calling](tool-calling.md) elsewhere in this vault |

## Defining Agents and Tasks

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, up-to-date information on the given topic",
    backstory="You are a meticulous analyst who double-checks every fact.",
)

writer = Agent(
    role="Technical Writer",
    goal="Turn research into a clear, well-structured report",
    backstory="You write concise, engaging technical content.",
)

research_task = Task(
    description="Research recent trends in {topic}.",
    expected_output="A bulleted list of 5 key findings.",
    agent=researcher,
)

write_task = Task(
    description="Write a short report based on the research findings.",
    expected_output="A 3-paragraph report.",
    agent=writer,
    context=[research_task],   # writer receives research_task's output
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

result = crew.kickoff(inputs={"topic": "vector database adoption"})
```

## YAML-Based Configuration (Recommended for Larger Crews)

```yaml
# agents.yaml
researcher:
  role: Research Analyst
  goal: Find accurate, up-to-date information on the given topic
  backstory: You are a meticulous analyst who double-checks every fact.
```

Defining agents/tasks in [YAML](../../devops/yaml.md) rather than inline Python keeps the crew's configuration decoupled from application logic — the same pattern many infrastructure tools ([Ansible](../../cloud/iac/ansible.md), [Helm](../../distributed-systems/kubernetes/helm.md)) use for the same reason.

## Common Questions

**How is CrewAI's "role-based" model different from just prompting one agent with different personas?**
> Each CrewAI agent is a genuinely separate execution context with its own scoped goal/backstory/tools and, critically, its own conversation history — it doesn't see the full context every other agent has seen unless explicitly passed via `context=`. This is the same [context isolation](multi-agent-systems.md) benefit that motivates splitting work across agents generally, not something a single agent switching personas achieves.

**When does CrewAI's structure become limiting?**
> For highly dynamic workflows where the sequence of steps genuinely can't be known ahead of time (branches, loops based on runtime state), [LangGraph](langgraph.md)'s explicit graph model gives more control. CrewAI's role/task model is best suited to workflows where the division of labor is knowable in advance, even if the content varies per run.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [AutoGen](autogen.md)
- [LangGraph](langgraph.md)
- [Multi-Agent Systems](multi-agent-systems.md)
- [Tool / Function Calling](tool-calling.md)
