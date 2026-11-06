# Module: APIs & Backend Services

**Category:** Backend · **Typical duration:** 3–4 weeks (15–20 hrs/week) · **Prerequisite modules:** [Programming Fundamentals](../foundations/programming-fundamentals.md), [Version Control & CLI](../foundations/version-control-and-cli.md)

## Goal

Build a production-shaped backend API: authenticated, validated, tested, and ready to put behind a load balancer.

## Core topics

- [ ] [REST](../../../engineering/concepts/backend/api/rest.md) principles: resources, verbs, status codes, [pagination](../../../engineering/concepts/backend/api/pagination.md), versioning
- [ ] A modern web framework for your language (e.g. [FastAPI](../../../engineering/concepts/programming/python/fastapi.md), NestJS, [Spring Boot](../../../engineering/concepts/programming/java/spring-boot.md), [ASP.NET Core](../../../engineering/concepts/programming/csharp/asp-net.md))
- [ ] Request/response validation and schema definition (e.g. [Pydantic](../../../engineering/concepts/programming/python/pydantic.md), [class-validator](../../../engineering/concepts/backend/api/class-validator.md), [Zod](../../../engineering/concepts/programming/typescript/zod.md))
- [ ] [Authentication](../../../engineering/concepts/security/auth/authentication.md) (OAuth2/[JWT](../../../engineering/concepts/security/auth/jwt.md)) and role-based [authorization](../../../engineering/concepts/security/authorization/authorization.md)
- [ ] Async/concurrent request handling, background tasks, streaming responses ([SSE](../../../engineering/concepts/protocols/sse.md)/[websockets](../../../engineering/concepts/networking/websockets.md))
- [ ] [Dependency injection](../../../engineering/concepts/programming/fundamentals/dependency-injection.md), [middleware](../../../engineering/concepts/backend/middleware.md), structured logging
- [ ] API documentation ([OpenAPI](../../../engineering/concepts/backend/api/openapi.md)/Swagger)
- [ ] Integration testing for endpoints (test client + fixtures)

## Resources

- Your chosen framework's official tutorial, start to finish
- The OpenAPI specification's own docs
- A REST API design guide/book for naming and pagination conventions

## Milestone deliverable

An authenticated API service (JWT-protected, role-aware) with at least one streaming endpoint, OpenAPI docs, and 80%+ test coverage on the core routes.

## Related concepts

REST, [DTO](../../../engineering/concepts/backend/api/dto.md), [HTTP Status Codes](../../../engineering/concepts/backend/api/http-status-codes.md), JWT, Authorization, FastAPI, [Rate Limiting](../../../engineering/concepts/backend/architecture/rate-limiting.md)
