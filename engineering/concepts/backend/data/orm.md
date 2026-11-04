# ORM (Object-Relational Mapping)

ORM stands for **Object-Relational Mapping**. It is a technique/tool that lets applications interact with [SQL](../../databases/relational/sql.md) databases using objects, classes, and methods instead of writing raw [SQL](../../databases/relational/sql.md) manually.

## Simple Idea

Instead of writing:

```sql
SELECT * FROM users;
```

you write:

```typescript
userRepository.find()
```

or:

```typescript
prisma.user.findMany()
```

An ORM maps a **database table** to a **programming object/class**.

### Example

[SQL](../../databases/relational/sql.md) table:

| id | name |
| --- | --- |
| 1 | Amr |

Application object:

```typescript
{
  id: 1,
  name: "Amr"
}
```

The ORM converts between database rows and application objects automatically.

## Why ORMs Exist

Without an ORM, you get:

- lots of raw [SQL](../../databases/relational/sql.md) to write
- manual row-to-object mapping
- repetitive boilerplate code

**Without ORM:**

```typescript
const result = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [id]
);
```

**With ORM:**

```typescript
const user = await prisma.user.findUnique({
  where: { id }
});
```

Cleaner and safer.

## Popular ORMs

**JavaScript / TypeScript**

| ORM       | Ecosystem         |
| --------- | ----------------- |
| Prisma    | Modern TypeScript |
| TypeORM   | NestJS common     |
| Sequelize | Node.js           |
| Drizzle   | Modern TypeScript — [SQL](../../databases/relational/sql.md)-like syntax, lightweight, edge/serverless-friendly (no heavy runtime) |

**Python**

| ORM                                              | Ecosystem                                    |
| ------------------------------------------------ | -------------------------------------------- |
| SQLAlchemy                                       | Python                                       |
| [Django](../../programming/python/django.md) ORM | [Django](../../programming/python/django.md) |

**Java**

| ORM | Ecosystem |
| --- | --- |
| Hibernate | Java/Spring |

## ORM Core Concept

An ORM maps:

| Database | Application |
| -------- | ----------- |
| Table    | Class/Model |
| Row      | Object      |
| Column   | Property    |

### Example in Prisma

Schema:

```prisma
model User {
  id    Int    @id
  name  String
}
```

Query:

```typescript
const users = await prisma.user.findMany();
```

### Example in TypeORM

Entity:

```typescript
@Entity()
export class User {

  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

}
```

Query:

```typescript
userRepository.find();
```

## ORM Responsibilities

An ORM handles:

- [SQL](../../databases/relational/sql.md) generation
- mapping rows to objects
- relationships
- migrations
- transactions
- validation helpers

## Relationships in ORM

This is a very important area. ORMs manage joins/relations automatically.

**One-to-Many example:**

```typescript
@OneToMany(() => Order, order => order.user)
orders: Order[];
```

Without an ORM, you would manually write the JOINs, mappings, and relation-handling code yourself.

## ORM Advantages

1. **Faster development** — less [SQL](../../databases/relational/sql.md) boilerplate.
2. **Type safety** — especially in TypeScript ORMs, giving autocomplete and compile-time validation.
3. **Easier maintenance** — cleaner code structure.
4. **[Database Abstraction](database-abstraction.md)** — can sometimes switch databases more easily.
5. **Security** — ORMs usually help prevent [SQL injection](../../security/attacks/sql-injection.md) through parameterized queries.

## ORM Disadvantages

This is a very important senior-level topic.

1. **Hidden [SQL](../../databases/relational/sql.md) complexity** — developers may not understand the actual generated [SQL](../../databases/relational/sql.md).
2. **Performance problems** — bad ORM usage can generate inefficient queries, [N+1 problems](n-plus-1-problem.md), or unnecessary joins.
3. **Less control** — raw [SQL](../../databases/relational/sql.md) is sometimes still needed for optimization or advanced queries.
4. **Learning curve** — complex ORMs can become difficult to master.

## N+1 Query Problem

A common ORM comparison topic. See [The N+1 Problem](n-plus-1-problem.md) for a full treatment.

**Example:** fetching users and orders for each user. Bad ORM usage produces:

```text
1 query for users
+
N queries for orders
```

This is a huge performance issue.

**Solution:** use eager loading, joins, or batching.

## ORM vs Query Builder vs Raw SQL

| Layer | [Abstraction](../../programming/fundamentals/abstraction.md) | Example |
| --- | --- | --- |
| ORM | Higher [abstraction](../../programming/fundamentals/abstraction.md) | `prisma.user.findMany()` |
| Query Builder | More [SQL](../../databases/relational/sql.md)-like | `qb.select().from(User)` |
| Raw [SQL](../../databases/relational/sql.md) | Lowest level | `SELECT * FROM users;` |

```text
Raw SQL → Query Builder → ORM
```

More [abstraction](../../programming/fundamentals/abstraction.md) as you move up.

### Do Senior Engineers Still Use Raw SQL?

Yes — very commonly, for analytics, optimization, complex reporting, and performance-critical queries.

**Modern reality:** most production systems use ORM for the bulk of CRUD operations, and raw [SQL](../../databases/relational/sql.md) for advanced cases.

## ORM and Migrations

ORMs often manage schema changes:

```bash
npx prisma migrate dev
```

## ORM and Transactions

```typescript
await prisma.$transaction([
  // ...
]);
```

## Common Questions

**Q1) What is ORM?**

> ORM is a layer that maps relational database tables to application objects, allowing developers to interact with databases using programming language constructs instead of raw [SQL](../../databases/relational/sql.md).

**Q2) ORM advantages?**

- faster development
- type safety
- cleaner code
- relationship handling

**Q3) ORM disadvantages?**

- hidden complexity
- performance issues
- inefficient generated queries

**Q4) What is the N+1 problem?**

An ORM issue where related-data fetching generates excessive database queries.

**Q5) Should developers still know SQL if using an ORM?**

Absolutely yes. Senior engineers must understand SQL, indexes, joins, and query optimization.

**Q6) ORM vs query builder?**

An ORM abstracts tables as objects; query builders remain closer to SQL syntax.

### Senior-Level Answer

> ORM is an [abstraction](../../programming/fundamentals/abstraction.md) layer that maps relational data models to application-level objects, improving developer productivity and maintainability while introducing tradeoffs around query transparency, optimization, and [abstraction](../../programming/fundamentals/abstraction.md) overhead.

### Easy Way to Remember

```text
ORM = database translated into objects/classes
```

## Related

- [Database Abstraction](database-abstraction.md) — the general pattern ORM is the most common concrete implementation of, including the repository pattern layered on top
- [The N+1 Problem](n-plus-1-problem.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [Services](../nestjs/services.md)
- [Monolith vs Microservices](../architecture/monolith-vs-microservices.md)
- [SQL Injection](../../security/attacks/sql-injection.md)
- [Connection Pooling](../../databases/relational/connection-pooling.md)
