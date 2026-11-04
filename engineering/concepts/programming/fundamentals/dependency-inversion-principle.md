# Dependency Inversion Principle (DIP)

The **Dependency Inversion Principle** is the "D" in **SOLID** — a design principle, not a technique or a tool, stating:

> High-level modules should not depend on low-level modules. Both should depend on **abstractions** (interfaces), not on concrete implementations.

It's the single most confused-with-[dependency-injection](dependency-injection.md) concept in object-oriented design — DIP is the *rule*; [dependency injection](dependency-injection.md) is just the most common *technique* for satisfying it. You can follow DIP without any [DI](dependency-injection.md) framework at all (pass an interface manually), and you can use a [DI](dependency-injection.md) framework while still violating DIP (inject a concrete class directly instead of an interface).

## The Problem DIP Solves

```
Without DIP:
  High-level business logic  →  depends directly on  →  a specific low-level implementation
  (OrderService)                                          (PostgresOrderRepository)
```

If `OrderService` imports and constructs `PostgresOrderRepository` directly, two problems follow: swapping the database requires editing `OrderService` itself, and testing `OrderService` requires a real Postgres connection — there's no way to substitute a fake. The dependency points the wrong direction: important business logic depends on a low-level storage detail.

```
With DIP:
  High-level business logic  →  depends on  →  an abstraction (interface)
  (OrderService)                                (OrderRepository interface)
                                                        ↑
                                      a low-level implementation depends on it too
                                            (PostgresOrderRepository)
```

Both the high-level and low-level code now depend on the **same [abstraction](abstraction.md)**, pointing toward it from opposite directions — hence "inversion": the traditional dependency arrow (high-level → low-level) is flipped so both sides depend on an interface neither of them owns outright.

## A Worked Example

```typescript
// ❌ Violates DIP: OrderService depends directly on a concrete, low-level class
class PostgresOrderRepository {
  save(order: Order) { /* raw SQL against Postgres */ }
}

class OrderService {
  private repo = new PostgresOrderRepository();  // tightly coupled, hardcoded
  placeOrder(order: Order) {
    this.repo.save(order);
  }
}
```

```typescript
// ✅ Follows DIP: both sides depend on an abstraction
interface OrderRepository {
  save(order: Order): void;
}

class PostgresOrderRepository implements OrderRepository {
  save(order: Order) { /* raw SQL against Postgres */ }
}

class OrderService {
  constructor(private repo: OrderRepository) {}  // depends on the interface, not the implementation
  placeOrder(order: Order) {
    this.repo.save(order);
  }
}

// A test can now substitute a fake with zero changes to OrderService itself
class FakeOrderRepository implements OrderRepository {
  saved: Order[] = [];
  save(order: Order) { this.saved.push(order); }
}
```

Notice: the second version doesn't require a DI framework at all — manually passing `new OrderService(new PostgresOrderRepository())` already satisfies DIP, because `OrderService` only ever references the `OrderRepository` interface, never the concrete class. A [dependency injection](dependency-injection.md) container (NestJS, Spring, ASP.NET) just automates *which* implementation gets passed in — it doesn't change *whether* DIP is being followed.

## DIP vs. Dependency Injection — The Distinction That Matters

| | Dependency Inversion Principle | [Dependency Injection](dependency-injection.md) |
|---|---|---|
| **What it is** | A design *principle* — depend on abstractions, not concretions | A *technique* for supplying a class's dependencies from outside |
| **Scope** | A rule about the *direction* of dependencies in a design | A mechanism for *wiring* dependencies together at runtime |
| **Requires a framework?** | No — can be satisfied with plain interfaces and manual construction | No — can be done manually (constructor arguments) or via a framework/container |
| **Can you have one without the other?** | Yes — satisfy DIP manually, with no DI container at all | Yes — a DI container can still inject a concrete class directly, violating DIP |

They're frequently used together (a DI container resolving interface-typed constructor parameters is both DIP-compliant *and* using DI), but neither implies the other.

## Where This Shows Up in This Handbook

[Database abstraction](../../backend/data/database-abstraction.md)'s repository pattern is DIP applied directly to the data layer: business logic depends on a `UserRepository` interface, never on Prisma/TypeORM/EF Core directly. The [Python Assistant API code sample](../../../code-samples/python-assistant-api/)'s `Retriever`/`LLMClient` Protocols are the exact same pattern in Python — the pipeline depends on the protocol, and a real implementation or a test fake can be swapped in without the pipeline ever changing.

## Common Questions

**Does "inversion" mean dependencies flow backward?**
> Not quite — it means the *ownership* of the [abstraction](abstraction.md) inverts. In a naive design, the high-level module depends on the low-level module's own interface (if any). Under DIP, the **high-level module defines the interface it needs**, and the low-level module must conform to it — the abstraction is owned by the high-level/business side, not the low-level/implementation side.

**Is every interface automatically DIP-compliant?**
> No — defining `interface PostgresOrderRepository` and having only Postgres-specific methods on it doesn't help; the interface still leaks a low-level concern (which database) into the abstraction. A DIP-compliant interface is defined in terms the high-level module cares about (`save`, `findById`), not in terms of the low-level implementation's own vocabulary.

## Related

- [Dependency Injection](dependency-injection.md) — the most common technique for satisfying this principle, but not the same thing
- [Database Abstraction](../../backend/data/database-abstraction.md) — the repository pattern is DIP applied to the data layer
- [Abstraction](abstraction.md) — the general concept DIP is built on
- [interface vs type](../typescript/interface-vs-type.md) — the TypeScript-level mechanism used to express the abstraction DIP requires
- [Python Assistant API](../../../code-samples/python-assistant-api/) — a runnable example using `Protocol` classes as the DIP abstraction
