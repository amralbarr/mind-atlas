# REST

REST stands for **Representational State Transfer**. It is an architectural style for designing APIs over [HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP).

## Simple Meaning

> Resources are accessed using standard [HTTP](../../networking/http.md) methods in a predictable way.

## Core Idea

Everything is treated as a **resource** — for example, users, products, orders, posts.

Example resources:

```text
/users
/products
/orders
```

## REST Uses HTTP Methods

| Method | Meaning |
| --- | --- |
| GET | Read data |
| POST | Create data |
| PUT | Replace data |
| PATCH | Update partial data |
| DELETE | Remove data |

## Example REST API

**Get all users:**

```http
GET /users
```

**Get one user:**

```http
GET /users/1
```

**Create user:**

```http
POST /users
```

Body:

```json
{
  "name": "Amr"
}
```

**Update user:**

```http
PATCH /users/1
```

**Delete user:**

```http
DELETE /users/1
```

## Why Called "Representational"

The server sends a **representation** of a resource, usually [JSON](../../programming/fundamentals/json.md):

```json
{
  "id": 1,
  "name": "Amr"
}
```

This [JSON](../../programming/fundamentals/json.md) represents the user resource.

## Why Called "State Transfer"

The client changes server state through requests. For example, `POST /orders` changes system state by creating an order.

## REST Principles

### 1) Stateless

Very important: each request must contain ALL required information. The server should NOT remember client session state between requests.

Example — every request includes:

```http
Authorization: Bearer token
```

**Why it matters:** scalability, easier [load balancing](../../networking/load-balancing.md), simpler servers.

### 2) Client-Server Separation

Frontend and backend are independent. Frontend owns the UI; backend owns data/business logic.

### 3) Uniform Interface

Consistent API design, e.g.:

```text
GET /users
GET /products
GET /orders
```

Predictable structure.

### 4) Resource-Based

Endpoints represent nouns.

Good:

```text
/users
/orders
```

Less RESTful:

```text
/getUsers
/createOrder
```

### 5) Cacheable

Responses may be cached, improving performance.

## REST API Example in NestJS

```typescript
@Controller('users')
export class UsersController {

  @Get()
  findAll() {}

  @Post()
  create() {}

}
```

REST endpoints like this are typically implemented via [controllers](../nestjs/controllers.md), which delegate to [services](../nestjs/services.md) for business logic.

## REST vs RPC

**REST** is resource-oriented:

```http
GET /users/1
```

**RPC** is action/function-oriented:

```http
POST /getUser
```

## REST Advantages

- Simple
- Standardized
- Scalable
- Easy integration
- Works well with browsers

## REST Disadvantages

- Over-fetching sometimes
- Under-fetching sometimes
- Multiple requests may be needed

## REST vs GraphQL

See [GraphQL](graphql.md) for the full comparison.

| REST | [GraphQL](graphql.md) |
| --- | --- |
| Multiple endpoints | Single endpoint |
| Fixed responses | Flexible queries |
| Easier caching | More complex caching |

## Common HTTP Status Codes

| Code | Meaning |
| --- | --- |
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

See [HTTP Status Codes](http-status-codes.md) for the full list by class, plus why `401` and `403` are so easily confused.

## Example Full REST Flow

**Request:**

```http
GET /users/1
```

**Response:**

```json
{
  "id": 1,
  "name": "Amr"
}
```

## REST Naming Best Practices

Use nouns:

```text
/users
/products
```

Avoid verbs:

```text
/getUsers
/deleteProduct
```

## Common Questions

**What is REST?**

> REST is an architectural style for designing stateless resource-oriented APIs over [HTTP](../../networking/http.md) using standard [HTTP](../../networking/http.md) methods.

**Why are REST APIs stateless?**

> Because each request contains all required information, allowing servers to scale independently without storing client session state.

**Difference between PUT and PATCH?**

| Method | Meaning |
| --- | --- |
| PUT | Replace entire resource |
| PATCH | Partial update |

### Senior-Level Answer

> REST is a stateless architectural style that models application data as resources accessible through uniform [HTTP](../../networking/http.md) interfaces. It promotes scalability, simplicity, and decoupled client-server communication through standardized operations and resource representations.

### Easy Way to Remember

```text
REST = resources + HTTP methods + stateless APIs
```

## Related

- [API](api.md) — the general contract concept REST is one style of implementing
- [GraphQL](graphql.md)
- [gRPC](grpc.md)
- [Controllers](../nestjs/controllers.md)
- [Services](../nestjs/services.md)
- [NestJS Overview](../nestjs/nestjs-overview.md)
- [HTTP Status Codes](http-status-codes.md)
- [HTTP](../../networking/http.md)
- [API Versioning](api-versioning.md)
- [Pagination](pagination.md)
- [curl Commands](../../../commands/curl.md)
