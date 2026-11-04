# Azure API Management (APIM)

Azure API Management is Microsoft's fully managed [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway) and API lifecycle platform — it fronts backend APIs ([Azure](../../cloud/azure/azure.md)-hosted or external), enforces policies (auth, [rate limiting](../architecture/rate-limiting.md), transformation) at the gateway without touching backend code, and publishes a developer portal for API consumers. Its defining difference from [Kong](kong.md)/[NGINX](nginx.md)/[Traefik](traefik.md) is *how* behavior is configured: not plugins, but a declarative **XML policy pipeline** applied per-API or per-operation.

## Core Concepts

| Term | Meaning |
|---|---|
| **API** | A logical grouping of operations (routes) fronting one backend — can wrap an [Azure](../../cloud/azure/azure.md) Function, App Service, AKS service, [Azure OpenAI](../../cloud/azure/azure-openai.md) endpoint, or any external [HTTP](../../networking/http.md) backend |
| **Operation** | One route + method within an API (`GET /orders/{id}`), the finest granularity policies can target |
| **Product** | A bundle of one or more APIs exposed together to consumers under one subscription — the unit developers actually subscribe to |
| **Subscription** | A consumer's access grant to a Product, identified by a subscription key ([API key](../../security/auth/api-key.md)-equivalent) sent as a header or query param |
| **Policy** | An XML snippet defining what happens to a request/response at a given stage — the mechanism behind auth, [rate limiting](../architecture/rate-limiting.md), caching, and transformation, applied in the portal/ARM template, never in backend code |
| **Named Value** | A reusable, optionally Key-Vault-backed config value (a secret, an endpoint URL) referenced inside policies, kept out of the policy XML itself |
| **Backend** | A reusable reference to the actual service an API's operations forward to, including its own circuit-breaker and retry configuration |

## The Policy Pipeline

Every request flows through up to four policy sections, each independently configurable at the global, Product, API, or Operation level (more specific scopes override broader ones):

```
Client request
     │
     ▼
inbound    ← auth checks, rate limiting, request transformation, caching lookup
     │
     ▼
backend    ← the actual call to the backend service
     │
     ▼
outbound   ← response transformation, caching store
     │
     ▼
Client response

on-error   ← runs instead of outbound if any prior section throws
```

### Worked Example: JWT Validation + Rate Limiting

```xml
<policies>
  <inbound>
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
      <openid-config url="https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration" />
      <audiences>
        <audience>api://orders-api</audience>
      </audiences>
    </validate-jwt>
    <rate-limit-by-key calls="100" renewal-period="60"
        counter-key="@(context.Request.Headers.GetValueOrDefault("Authorization",""))" />
  </inbound>
  <backend>
    <forward-request />
  </backend>
  <outbound />
  <on-error>
    <set-body>@{ return "{\"error\":\"" + context.LastError.Message + "\"}"; }</set-body>
  </on-error>
</policies>
```

`validate-jwt` here checks a [Microsoft Entra ID](../../cloud/azure/microsoft-entra-id.md)-issued token's signature, expiry, and audience **before** the request reaches the backend — the same "[authorization](../../security/authorization/authorization.md) enforced at the gateway, not trusted from the caller" principle covered generally in [JWT](../../security/auth/jwt.md), just expressed as APIM's declarative policy syntax instead of application [middleware](../middleware.md). `rate-limit-by-key` implements per-caller [rate limiting](../architecture/rate-limiting.md) keyed on the token itself, so limits are per-identity rather than per-IP.

## Where It Fits vs. Other Gateways

| | Azure API Management | [Kong](kong.md) / [NGINX](nginx.md) / [Traefik](traefik.md) | [AWS API Gateway](aws-api-gateway.md) |
|---|---|---|---|
| **Hosting** | Fully managed ([Azure](../../cloud/azure/azure.md)) | Self-hosted (or [Kong](kong.md) Konnect managed) | Fully managed ([AWS](../../cloud/infrastructure/aws.md)) |
| **Configuration model** | Declarative XML policies | Plugins (Lua/custom) or config files | Console/API-defined integrations |
| **Natural fit** | [Azure](../../cloud/azure/azure.md)-native backends, [Azure OpenAI](../../cloud/azure/azure-openai.md)/AI Search fronting, Entra ID auth | Cloud-agnostic or self-hosted requirement | Lambda/serverless-first [AWS](../../cloud/infrastructure/aws.md) backends |
| **Developer portal** | Built-in, auto-generated from the API's [OpenAPI](../api/openapi.md) spec | Not built-in ([Kong](kong.md) has a separate dev portal product) | Not built-in |

The practical decision mirrors any cloud-vendor-gateway choice: APIM is the natural default inside an Azure-centric architecture — especially one already using [Azure AI Search](../../cloud/azure/azure-ai-search.md), [Azure OpenAI](../../cloud/azure/azure-openai.md), or Entra ID — while a self-hosted gateway remains preferable for a cloud-agnostic or multi-cloud system.

## Fronting an Azure OpenAI / RAG Endpoint

A common enterprise AI pattern: put APIM in front of an [Azure OpenAI](../../cloud/azure/azure-openai.md) deployment (or any model endpoint) rather than letting every client call it directly —

- **Per-consumer [rate limiting](../architecture/rate-limiting.md)** on token-expensive model calls, via `rate-limit-by-key`, preventing one noisy workload from exhausting a shared quota
- **Subscription-key-based access** so different internal teams/apps each get their own key, usage tracking, and revocable access, without touching the underlying model deployment's own access controls
- **Response caching** (`cache-lookup`/`cache-store` policies) for repeated identical prompts, cutting cost on cacheable traffic
- **Centralized Entra ID validation** once at the gateway, instead of every calling service re-implementing token validation

This is the same "gateway enforces cross-cutting policy, backend stays simple" principle [Spring Cloud Gateway](spring-cloud-gateway.md) and [Kong](kong.md) apply generally, specialized to the token-cost-sensitive shape of fronting an [LLM](../../ai/generation/llm.md) endpoint specifically.

## Common Questions

**Does APIM replace the need for [authorization](../../security/authorization/authorization.md) inside the backend service?**
> No — `validate-jwt` confirms the token is genuinely signed by the expected issuer and not expired; it does not know whether *this specific user* is allowed *this specific resource*. Resource-level [authorization](../../security/authorization/authorization.md) (can this user see this document, this record) still has to be enforced in the backend service itself, using claims the gateway has already validated as trustworthy.

**When would a self-hosted gateway win over APIM despite the operational overhead?**
> When the system must stay cloud-agnostic, when a required plugin/extension only exists in a self-hosted gateway's ecosystem, or when latency-sensitive internal east-west traffic shouldn't route through a managed external control plane at all — APIM is built for the client-facing, cross-cutting-policy use case, not necessarily every internal service-to-service call.

**What's the difference between a "Product" and an "API" in APIM?**
> An API is the technical grouping of operations against one backend; a Product is the commercial/access grouping a consumer actually subscribes to — one Product can bundle several APIs together (e.g. an "Orders" Product exposing both the orders API and the shipping API under one subscription key), and one API can appear in multiple Products with different policies per Product.

## Related

- [Kong](kong.md) / [NGINX](nginx.md) / [Traefik](traefik.md) — the self-hosted alternatives APIM's managed model trades flexibility for
- [AWS API Gateway](aws-api-gateway.md) — the equivalent managed offering on [AWS](../../cloud/infrastructure/aws.md), for the direct cross-cloud comparison
- [Microsoft Entra ID](../../cloud/azure/microsoft-entra-id.md) — the identity provider APIM's `validate-jwt` policy checks tokens against
- [JWT](../../security/auth/jwt.md) — the token format and validation principles APIM's policy syntax implements declaratively
- [Rate Limiting](../architecture/rate-limiting.md) — the general pattern APIM's `rate-limit`/`rate-limit-by-key` policies implement
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) / [Azure AI Services](../../cloud/azure/azure-ai-services.md) — common backends an enterprise AI architecture fronts with APIM
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md) — the API gateway pattern this is one managed implementation of
