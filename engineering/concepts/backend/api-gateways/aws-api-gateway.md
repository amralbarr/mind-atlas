# AWS API Gateway

AWS API Gateway is a fully managed [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway) service — there's no gateway server to run, patch, or scale; routes, auth, and rate limits are configured against the [AWS](../../cloud/infrastructure/aws.md) API/console and [AWS](../../cloud/infrastructure/aws.md) operates the actual proxying infrastructure. It's most often paired with [AWS](../../cloud/infrastructure/aws.md) Lambda for a fully serverless backend.

## Core Concepts

| Term | Meaning |
|---|---|
| **[REST](../api/rest.md) API / [HTTP](../../networking/http.md) API** | Two API Gateway product types — [HTTP](../../networking/http.md) APIs are newer, cheaper, and lower-latency; [REST](../api/rest.md) APIs have a larger, older feature set (request/response transformation, API keys, usage plans) |
| **Resource & Method** | A resource is a URL path (`/orders`); a method (`GET`, `POST`) on it defines what integration handles that request |
| **Integration** | What actually handles a matched request — commonly a Lambda function, but also an [HTTP](../../networking/http.md) backend, another [AWS](../../cloud/infrastructure/aws.md) service, or a mock response |
| **Stage** | A named, independently deployed snapshot of an API's configuration (e.g. `dev`, `prod`), each with its own URL and can have its own throttling/logging settings |
| **Usage plan / [API key](../../security/auth/api-key.md)** | Per-consumer [rate limiting](../architecture/rate-limiting.md) and quota enforcement, tied to an issued [API key](../../security/auth/api-key.md) |

## Defining a Route with a Lambda Integration (AWS CLI)

```bash
aws apigatewayv2 create-api \
  --name orders-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:123456789012:function:get-orders
```

For an [HTTP](../../networking/http.md) API, `--target` alone wires a catch-all route straight to a Lambda function — no separate resource/method/integration setup needed for the simplest case.

## Infrastructure as Code (Serverless Framework Example)

```yaml
# serverless.yml
functions:
  getOrders:
    handler: handler.getOrders
    events:
      - httpApi:
          path: /orders
          method: get
  createOrder:
    handler: handler.createOrder
    events:
      - httpApi:
          path: /orders
          method: post
```

Each Lambda function is deployed and wired to its route in one declarative file — this pattern (API Gateway + Lambda, defined as code) is the common shape of an [AWS](../../cloud/infrastructure/aws.md) serverless [HTTP](../../networking/http.md) API.

## Common Questions

**When does AWS API Gateway make sense over [Kong](kong.md)/[NGINX](nginx.md)/[Traefik](traefik.md)?**
> When the backend is already Lambda-based/serverless and staying fully managed (no gateway infrastructure to operate at all) outweighs the flexibility of a self-hosted gateway's plugin ecosystem. It's a natural fit inside an all-[AWS](../../cloud/infrastructure/aws.md) architecture, and a poor fit if the system needs to stay cloud-agnostic or self-hosted.

**[REST](../api/rest.md) API or [HTTP](../../networking/http.md) API — which should a new project use?**
> [HTTP](../../networking/http.md) API for most new use cases — it's cheaper and lower-latency, and covers the common case (routing to Lambda or an HTTP backend, [JWT](../../security/auth/jwt.md)/OAuth authorizers, [CORS](../../security/attacks/cors.md)). [REST](../api/rest.md) API is worth it specifically for older features HTTP API doesn't support, like request/response transformation templates or usage plans with API keys.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Kong](kong.md)
- [AWS](../../cloud/infrastructure/aws.md)
- [SQS](../../distributed-systems/messaging/sqs.md)
