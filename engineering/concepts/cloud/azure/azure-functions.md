# Azure Functions

Azure Functions is Microsoft's serverless compute service — you deploy a single function (a piece of code), and [Azure](azure.md) handles provisioning, scaling, and running it in response to triggers, without you managing a server at all. It's Microsoft's answer to the same serverless-functions category as [AWS](../infrastructure/aws.md) Lambda or Google Cloud Functions, and one of the most common ways to react to an event happening in [Azure Blob Storage](azure-blob-storage.md) or [ADLS](adls.md).

## Core concepts

| Term | Meaning |
|---|---|
| **Function** | A single unit of code — one trigger, one piece of logic, deployed and scaled independently |
| **Trigger** | What causes the function to run — an [HTTP](../../networking/http.md) request, a new blob landing in storage, a message on a queue, a schedule (timer trigger), an Event Grid event |
| **Binding** | A declarative way to connect a function's [input/output](../../programming/fundamentals/io.md) to another [Azure](azure.md) service (e.g. "write the output straight to this Blob container") without writing the SDK plumbing by hand |
| **Hosting plan** | Consumption (pay only per execution, scales to zero), Premium (pre-warmed instances, no cold start), or Dedicated (runs on an App Service plan you already pay for) |
| **Cold start** | The latency penalty the first request pays when a function hasn't run recently and a new instance has to spin up — the main trade-off of the Consumption plan's scale-to-zero behavior |

## A blob-triggered function

```python
import logging
import azure.functions as func

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="raw/{name}", connection="AzureWebJobsStorage")
def process_uploaded_document(myblob: func.InputStream):
    logging.info(f"New blob: {myblob.name}, size: {myblob.length} bytes")
    # parse, chunk, embed, write to the processed/ container...
```

This is the serverless alternative to a scheduled batch job for reacting to new files — the function only runs (and only costs anything, on the Consumption plan) when a document actually lands in storage, rather than polling on a schedule.

## When to reach for it vs. a scheduled pipeline

| | Azure Functions (event-driven) | [Azure Data Factory](azure-data-factory.md) / scheduled job |
|---|---|---|
| **Trigger model** | Reacts immediately to an event (a new blob, an [HTTP](../../networking/http.md) call, a queue message) | Runs on a schedule or a coarser trigger, often processing in batches |
| **Best for** | Low-latency reactions to individual events; lightweight transformations | Large batch ETL, multi-step pipelines with many activities, orchestrating other services |
| **Cost model** | Pay per execution (Consumption plan) | Pay for pipeline runs / data movement |

In practice the two are often combined: a Functions trigger kicks off a larger Data Factory pipeline, or a Data Factory pipeline's final step calls a Function for logic that doesn't warrant its own pipeline activity.

## Related

- [Azure Blob Storage](azure-blob-storage.md) — one of the most common trigger/binding sources
- [ADLS](adls.md) — can trigger functions the same way Blob Storage does
- [Azure Data Factory](azure-data-factory.md) — the scheduled/batch alternative, often used alongside Functions rather than instead of it
- [Microsoft Entra ID](microsoft-entra-id.md) — identity for a function's own Managed Identity, used to authenticate to other [Azure](azure.md) resources without stored secrets
- [Azure Compute Hosting Options](../../../overviews/cloud/azure-compute-hosting-options.md) — Functions as the single-event-trigger option, compared against Container Apps/App Service/AKS for a full containerized service
