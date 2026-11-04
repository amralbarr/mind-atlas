# GraphQL

> A query language and runtime for APIs that allows clients to request exactly the data they need.

Created by [Meta (Facebook)](https://graphql.org/).

## Simple Idea

Instead of multiple [REST](rest.md) endpoints:

```text
GET /users
GET /posts
GET /comments
```

GraphQL usually has ONE endpoint:

```text
/graphql
```

The client decides what fields, what nested data, and what structure it wants.

## The REST Problems GraphQL Solves

### Over-fetching

Suppose the frontend needs only the user's name. [REST](rest.md) may return:

```json
{
  "id": 1,
  "name": "Amr",
  "email": "...",
  "phone": "...",
  "address": "...",
  "posts": [...]
}
```

Too much data. This is called **over-fetching**.

**GraphQL solution:** the client requests only the needed fields.

```graphql
query {
  user(id: 1) {
    name
  }
}
```

Response:

```json
{
  "data": {
    "user": {
      "name": "Amr"
    }
  }
}
```

Only the requested data is returned.

### Under-fetching

Sometimes the frontend needs user + posts + comments, which may require multiple [HTTP](../../networking/http.md) requests. This is called **under-fetching**.

**GraphQL solution:** a single query can fetch everything.

```graphql
query {
  user(id: 1) {
    name
    posts {
      title
      comments {
        text
      }
    }
  }
}
```

Response:

```json
{
  "data": {
    "user": {
      "name": "Amr",
      "posts": [
        {
          "title": "Post 1",
          "comments": [
            {
              "text": "Nice"
            }
          ]
        }
      ]
    }
  }
}
```

## Core Concepts

### 1) Schema

GraphQL APIs define a strongly typed schema:

```graphql
type User {
  id: ID!
  name: String!
}
```

### 2) Query

Used to READ data:

```graphql
query {
  users {
    name
  }
}
```

### 3) Mutation

Used to CREATE / UPDATE / DELETE:

```graphql
mutation {
  createUser(name: "Amr") {
    id
    name
  }
}
```

### 4) Subscription

Used for real-time updates, usually via [WebSockets](../../networking/websockets.md):

```graphql
subscription {
  messageAdded {
    text
  }
}
```

## GraphQL Resolvers

Resolvers are functions that fetch data. Example in [NestJS GraphQL](https://docs.nestjs.com/graphql/quick-start):

```typescript
@Query(() => User)
getUser() {
  return this.userService.find();
}
```

GraphQL flow:

```text
Client Query
     ↓
GraphQL Server
     ↓
Resolvers
     ↓
Database / Services
```

## REST vs GraphQL

Worth understanding well.

| Feature | [REST](rest.md) | GraphQL |
| --- | --- | --- |
| Endpoints | Multiple | Single |
| Data shape | Fixed | Client-defined |
| Over-fetching | Common | Avoided |
| Under-fetching | Common | Avoided |
| Typing | Weak | Strong schema |
| Caching | Easier | Harder |
| Complexity | Lower | Higher |

**[REST](rest.md) example** — fetching user + posts + comments may require 3 requests.

**GraphQL example** — usually 1 query.

### Why Frontend Developers Love GraphQL

Frontend controls fields, nesting, and response shape. Very flexible.

### Why Backend Engineers Sometimes Prefer REST

[REST](rest.md) is simpler, has easier caching, easier monitoring, and simpler debugging.

## GraphQL Advantages

- Exact data fetching
- Strong typing
- Single endpoint
- Excellent frontend flexibility
- Nested queries

## GraphQL Disadvantages

- More complex backend
- Harder caching
- Query complexity attacks
- Can become slow if poorly designed

## N+1 Query Problem

A common GraphQL issue — see [The N+1 Problem](../data/n-plus-1-problem.md) for the general concept.

Example: fetching users, then posts for each user can accidentally create `1 + N` database queries. Bad performance.

**Solution:** use DataLoader, batching, and caching.

## GraphQL Server Frameworks

**Apollo Server** — popular GraphQL server framework. See [Apollo GraphQL](https://www.apollographql.com/).

**NestJS GraphQL Module** — [supports](https://docs.nestjs.com/graphql/quick-start) both code-first and schema-first approaches.

Code-first example:

```typescript
@ObjectType()
class User {

  @Field()
  name: string;

}
```

Schema-first means writing a `.graphql` schema manually.

## Does GraphQL Connect Directly to the Database?

Usually **no**. GraphQL normally sits in front of a services layer:

```text
Frontend
   ↓
GraphQL Server
   ↓
Resolvers
   ↓
Services
   ↓
Database
```

Example real-world architecture:

```text
React/Next.js
     ↓
GraphQL API
     ↓
NestJS Resolver
     ↓
Service Layer
     ↓
PostgreSQL/MongoDB
```

GraphQL is an **API layer**, not the database itself.

Resolver example in [NestJS GraphQL](https://docs.nestjs.com/graphql/quick-start):

```typescript
@Query(() => User)
getUser(@Args('id') id: string) {
  return this.userService.findById(id);
}
```

Service layer:

```typescript
findById(id: string) {
  return this.prisma.user.findUnique({
    where: { id }
  });
}
```

GraphQL does NOT automatically expose the database — you decide what queries exist, what tables are accessible, and what fields are visible. This is a very important security point.

## Does GraphQL Restrict Access to Specific Tables?

Yes — if you design it that way. This is one of GraphQL's strengths.

Example database: `users`, `payments`, `admin_logs`, `passwords`. You may expose ONLY `users` through the GraphQL schema:

```graphql
type User {
  id: ID!
  name: String!
}
```

Notice: no password, no admin logs, no payment data.

The frontend CANNOT query fields not defined in the schema. If it tries:

```graphql
query {
  users {
    password
  }
}
```

the server returns an error, because the field does not exist in the schema.

**Very important security concept:** GraphQL exposes only what resolvers + schema allow — not the whole database automatically.

Think of it like a controlled window:

```text
Database = huge building
GraphQL schema = allowed windows
```

The frontend sees only the allowed windows.

## How Many GraphQL Endpoints Exist?

Usually only one — typically `/graphql`. All queries/mutations go there because the request body contains the query itself.

**[REST](rest.md)** uses many endpoints:

```text
/users
/orders
/products
/payments
```

**GraphQL** usually uses one:

```text
/graphql
```

Example requests — same endpoint, different query bodies:

```graphql
query {
  users {
    name
  }
}
```

```graphql
mutation {
  createUser(name: "Amr") {
    id
  }
}
```

### Can There Be Multiple GraphQL Endpoints?

Yes, but it's uncommon. Sometimes public API, admin API, and internal API use separate GraphQL servers/endpoints, e.g. `/graphql`, `/admin-graphql`, `/internal-graphql`. Most systems, however, use a single endpoint.

## Does the Frontend Send SQL Queries?

No. The frontend sends a GraphQL query like:

```graphql
query {
  users {
    name
  }
}
```

not:

```sql
SELECT * FROM users;
```

The backend resolver converts the request into a DB query. Flow internally:

```text
Frontend Query
     ↓
GraphQL Parser
     ↓
Resolver
     ↓
ORM/Database Query
     ↓
Response
```

## Does GraphQL Replace the Backend?

No — this is an important misconception. GraphQL is a backend API layer. You still need [authentication](../../security/auth/authentication.md), [authorization](../../security/authorization/authorization.md), services, validation, database logic, caching, and business rules.

Example real architecture:

```text
Next.js Frontend
      ↓
GraphQL API (NestJS)
      ↓
Auth Guards
      ↓
Resolvers
      ↓
Services
      ↓
Prisma ORM
      ↓
PostgreSQL
```

## Can GraphQL Become Dangerous?

Yes, if poorly designed — because the frontend can ask for huge nested queries or expensive operations.

Example dangerous query (deep nesting can overload the server):

```graphql
users {
  posts {
    comments {
      user {
        posts {
          # ...continues nesting
        }
      }
    }
  }
}
```

### Protection Techniques

- query depth limits
- complexity analysis
- [rate limiting](../architecture/rate-limiting.md)
- [authentication](../../security/auth/authentication.md)
- [pagination](pagination.md)

Very important senior topic.

## Is GraphQL Better Than REST?

Depends on the system.

**GraphQL better for:**

- Complex frontend apps
- Mobile apps
- Many frontend teams
- Flexible UI requirements
- Nested relational data

**[REST](rest.md) better for:**

- Simpler systems
- CRUD APIs
- Easy caching
- Public APIs
- Simpler backend maintenance

### Modern Reality

Many companies use both:

```text
REST → simple APIs
GraphQL → frontend aggregation layer
```

## When To Use GraphQL

Good for frontend-heavy applications, mobile apps, complex nested data, and multiple frontend clients.

## When REST Is Better

Good for simple APIs, CRUD systems, caching-heavy systems, and simpler architectures.

## Common Questions

**Q1) What problem does GraphQL solve?**

> GraphQL solves over-fetching and under-fetching by allowing clients to request exactly the data they need.

**Q2) Difference between [REST](rest.md) and GraphQL?**

> [REST](rest.md) uses multiple resource endpoints with fixed responses, while GraphQL uses a single endpoint with flexible client-defined queries.

**Q3) What is a resolver?**

> A function responsible for fetching GraphQL field data.

**Q4) What are queries, mutations, subscriptions?**

| Operation | Purpose |
| --- | --- |
| Query | Read |
| [Mutation](../../programming/fundamentals/mutation.md) | Write |
| Subscription | Real-time |

**Q5) What is the N+1 problem?**

> A performance issue where nested queries generate excessive database calls.

**Does GraphQL expose the entire database automatically?**

> No. GraphQL only exposes fields and operations explicitly defined in the schema and implemented by resolvers.

**Why does GraphQL usually use one endpoint?**

> Because the query itself specifies requested resources and fields dynamically.

**Does GraphQL replace [SQL](../../databases/relational/sql.md)?**

> No. GraphQL is an API query language, not a database query language.

### Senior-Level Answer

> GraphQL is a strongly typed API query language and execution runtime that enables clients to request precisely structured data through a single endpoint, improving frontend flexibility while introducing additional backend complexity around query execution, caching, and performance optimization. It is best understood as a typed API gateway layer between the frontend and backend services/databases.

### Easy Way to Remember

```text
REST = server decides response
GraphQL = client decides response

REST: many URLs
GraphQL: one URL + flexible query body
```

## Related

- [API](api.md) — the general contract concept GraphQL is one style of implementing
- [REST](rest.md)
- [gRPC](grpc.md)
- [The N+1 Problem](../data/n-plus-1-problem.md)
- [Controllers](../nestjs/controllers.md)
- [Services](../nestjs/services.md)
- [NestJS Overview](../nestjs/nestjs-overview.md)
- [Pagination](pagination.md)
- [WebSockets](../../networking/websockets.md) (subscriptions typically run over these)
- [Rate Limiting](../architecture/rate-limiting.md)
