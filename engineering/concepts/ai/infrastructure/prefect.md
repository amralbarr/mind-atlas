# Prefect

Prefect is a modern workflow orchestration tool — a Python-native alternative to [Airflow](airflow.md), where pipelines are defined as plain Python functions decorated with `@flow`/`@task` rather than a separate DAG-definition DSL, aiming for less boilerplate and configuration overhead. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [Airflow](airflow.md) and the agent-oriented frameworks.

## Core Concepts

| Term | Meaning |
|---|---|
| **Flow** | A Python function decorated with `@flow` — the top-level pipeline definition |
| **Task** | A Python function decorated with `@task` — a unit of work within a flow, with automatic retry/caching/logging support |
| **Dependencies inferred from code** | Task order comes from normal Python function calls and data flow, not a separately declared dependency graph the way [Airflow](airflow.md)'s `>>` syntax requires |
| **Deployment** | A flow packaged with its schedule/infrastructure config so it can run on a schedule or be triggered remotely, rather than only running locally |
| **Prefect Cloud / Server** | The UI and orchestration backend showing flow run history, logs, and status — self-hosted (Server) or managed (Cloud) |

## Defining a Flow

```python
from prefect import flow, task
from datetime import timedelta

@task(retries=3, retry_delay_seconds=30)
def fetch_data():
    ...
    return raw_data

@task
def clean_data(raw_data):
    ...
    return cleaned_data

@task
def train_model(cleaned_data):
    ...

@flow(name="nightly-model-training")
def train_pipeline():
    raw = fetch_data()
    cleaned = clean_data(raw)
    train_model(cleaned)

if __name__ == "__main__":
    train_pipeline()
```

Task dependencies here are implicit in the code itself — `clean_data(raw)` can't run until `fetch_data()` returns, so Prefect infers the execution order from normal Python data flow rather than a separately declared graph.

## Scheduling a Deployment

```python
from prefect import flow

@flow
def train_pipeline():
    ...

if __name__ == "__main__":
    train_pipeline.serve(name="nightly-training", cron="0 2 * * *")
```

`serve()` registers the flow with a schedule and keeps a process running to execute it — the equivalent of [Airflow](airflow.md)'s scheduler, but declared directly alongside the flow's own code.

## Common Questions

**Why would a team choose Prefect over [Airflow](airflow.md) for a new pipeline?**
> When the team is already Python-heavy and wants pipelines that read like normal Python code (implicit dependencies, native retries/caching as decorators) rather than learning a separate DAG-authoring model — Prefect generally has a gentler learning curve and less configuration ceremony for straightforward pipelines, at the cost of [Airflow](airflow.md)'s much larger, more battle-tested plugin/operator ecosystem for existing enterprise integrations.

**Does Prefect replace the need for [Airflow](airflow.md) entirely?**
> Not universally — Airflow's maturity, breadth of pre-built operators, and long production track record still matter for large, complex, multi-team pipeline estates. Prefect is a strong default for new, Python-centric pipelines, especially smaller teams that don't need Airflow's full operator ecosystem.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [Airflow](airflow.md)
- [Pipeline Orchestration](pipeline-orchestration.md)
