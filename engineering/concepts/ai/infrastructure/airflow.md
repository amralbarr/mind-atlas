# Apache Airflow

Airflow is a workflow/data-[pipeline orchestration](pipeline-orchestration.md) platform — pipelines are defined as **DAGs** (directed acyclic graphs) of tasks with explicit dependencies, then scheduled, retried, and monitored by Airflow's own scheduler and web UI. It solves a different problem than an AI agent framework: recurring, dependency-ordered batch jobs (ETL, model training) rather than a model deciding its own next step at runtime. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [Prefect](prefect.md) and the agent-oriented frameworks.

## Core Concepts

| Term | Meaning |
|---|---|
| **DAG** | A Directed Acyclic Graph — the pipeline definition itself, a set of tasks and the dependencies between them (task B can't start until task A finishes) |
| **Task / Operator** | A single unit of work in a DAG; an Operator is a reusable task type (`PythonOperator`, `BashOperator`, `PostgresOperator`) |
| **Scheduler** | The component that triggers DAG runs on their configured schedule (cron-like) and hands ready tasks to workers |
| **XCom** | Airflow's mechanism for passing small pieces of data between tasks in the same DAG run |
| **Backfill** | Running a DAG for past scheduled intervals it missed or hasn't run yet — useful when adding a new pipeline retroactively |

## Defining a DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def fetch_data(): ...
def clean_data(): ...
def train_model(): ...

with DAG(
    dag_id="nightly_model_training",
    schedule="0 2 * * *",         # every night at 2 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    fetch = PythonOperator(task_id="fetch_data", python_callable=fetch_data)
    clean = PythonOperator(task_id="clean_data", python_callable=clean_data)
    train = PythonOperator(task_id="train_model", python_callable=train_model)

    fetch >> clean >> train   # explicit dependency chain
```

The `>>` operator declares that `clean` only runs after `fetch` succeeds, and `train` only after `clean` — if `fetch` fails, downstream tasks don't run, and Airflow's UI shows exactly which task in the chain broke.

## Retries and Alerting

```python
default_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
}

with DAG(dag_id="nightly_model_training", default_args=default_args, ...) as dag:
    ...
```

## Common Questions

**Why not just use a cron job for a nightly pipeline?**
> Cron runs a script on a schedule with no built-in dependency graph, retry logic, failure visibility, or backfill support — a pipeline with multiple ordered steps that can each independently fail needs exactly what Airflow adds: per-task retry, a UI showing which step failed and why, and the ability to re-run just the failed portion instead of the whole script.

**Is Airflow suitable for real-time or agentic workflows?**
> No — Airflow is built for scheduled, mostly-batch, dependency-ordered pipelines with a known structure ahead of time. Real-time, [LLM](../generation/llm.md)-driven decision-making belongs to agent frameworks like [LangGraph](../agents/langgraph.md); Airflow is the right tool for "train this model every night," not "let an agent decide what to do next."

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [Prefect](prefect.md)
- [Pipeline Orchestration](pipeline-orchestration.md)
