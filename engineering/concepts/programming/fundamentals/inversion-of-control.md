# Inversion of Control (IoC)

**Inversion of Control** is the general principle that a framework — not your own code — controls the flow of execution and object creation. [Dependency Injection](dependency-injection.md) is the most common and most visible *implementation* of IoC, but IoC as a principle is broader than [DI](dependency-injection.md) alone; several other patterns also invert control in the same spirit.

## The Core Idea: Who Calls Whom?

```
Traditional control flow:
  Your code  →  calls  →  a library function
  (your code decides when and what to call)

Inverted control flow:
  A framework  →  calls  →  your code
  (the framework decides when and what to call — you just plug code in)
```

In a traditional library, your application is in charge: it calls `library.doSomething()` whenever it wants, on its own terms. Under IoC, that relationship flips — the framework owns the control flow, and your code is invoked *by* the framework at the points the framework decides matter (a lifecycle hook, a route handler, an event callback). This is sometimes summarized as "the Hollywood principle": *don't call us, we'll call you*.

## IoC vs. Dependency Injection — The Distinction

|                                                   | Inversion of Control                                                                                              | [Dependency Injection](dependency-injection.md)                                           |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **What it is**                                    | A general principle about *who controls the flow*                                                                 | One specific, common technique that implements IoC for *dependency creation* specifically |
| **Scope**                                         | Broad — covers object creation, lifecycle, and execution flow generally                                           | Narrow — specifically about how a class gets its dependencies                             |
| **Examples beyond [DI](dependency-injection.md)** | Template method pattern, event-driven callbacks, a plugin/hook system, a web framework calling your route handler | —                                                                                         |

[DI](dependency-injection.md) answers one specific question IoC raises — "who creates my dependencies?" — but IoC as a principle also covers questions [DI](dependency-injection.md) doesn't touch, like "who decides when my code runs at all?"

## Other Implementations of IoC, Beyond DI

IoC shows up in forms that have nothing to do with dependency creation:

- **The Template Method pattern** — a base class defines an algorithm's overall structure and calls abstract "hook" methods a subclass fills in; the base class controls the flow, the subclass only supplies the pieces.
- **Event-driven callbacks** — registering an event handler (`button.addEventListener('click', handler)`) hands control to the browser/runtime, which decides *when* to call your handler — you never call it yourself.
- **A web framework's request lifecycle** — you write a route handler function, but [NestJS](../../backend/nestjs/nestjs-overview.md)/[Spring Boot](../java/spring-boot.md)/[ASP.NET Core](../csharp/asp-net.md) decide when to invoke it, in what order [middleware](../../backend/middleware.md) runs around it, and how its return value gets serialized — none of which your handler function controls.
- **A plugin system** — a host application calls into plugin code at defined extension points, rather than the plugin driving its own execution.

[Dependency injection](dependency-injection.md) containers are themselves IoC in action for one specific concern: instead of a class calling `new SomeDependency()` itself (the class controlling its own dependency creation), the **container** decides what instance to construct and hands it over — control over *object creation* has been inverted from the class to the container.

## Why "IoC Container" Is the Common Framework Term

[NestJS](../../backend/nestjs/nestjs-overview.md), [Spring Boot](../java/spring-boot.md), and [Angular](../../frontend/angular.md) all describe their [DI](dependency-injection.md) mechanism as an **"IoC container"** rather than just a "DI container" — a deliberate naming choice reflecting that the container's job is broader than *just* injecting constructor arguments: it also controls object **lifecycle** (when an instance is created, initialized, and destroyed — see [Provider Scope](provider-scope.md)), which is a form of control beyond dependency creation alone.

## Common Questions

**Is every framework callback an example of IoC?**
> Yes, in the general sense — any time a framework, not your own code, decides when your function runs, control has been inverted. This is why IoC is considered the umbrella principle and DI one specific, narrower application of it, focused specifically on dependency construction rather than execution timing in general.

**If I'm not using a DI framework, am I avoiding IoC entirely?**
> Not necessarily — a plain web framework that calls your route handler, or a test framework that calls your test functions, is already applying IoC to your code's execution flow, even with zero [dependency injection](dependency-injection.md) involved. IoC and DI are independent axes; you can have either without the other.

## Related

- [Dependency Injection](dependency-injection.md) — the most common implementation of IoC, specifically for dependency creation
- [Dependency Inversion Principle (DIP)](dependency-inversion-principle.md) — a related but distinct SOLID design principle about depending on abstractions, often confused with IoC due to the similar name
- [Provider Scope](provider-scope.md) — the lifecycle-control half of what an "IoC container" manages, beyond just injecting dependencies
- [NestJS Overview](../../backend/nestjs/nestjs-overview.md), [Spring Boot](../java/spring-boot.md), [ASP.NET Core](../csharp/asp-net.md), [Angular](../../frontend/angular.md) — the frameworks in this handbook whose DI mechanism is explicitly named an "IoC container"
