# Singleton Pattern

The Singleton pattern restricts a class to a single instance and provides one global access point to it — every part of the program that asks for the singleton gets back the *same* object, rather than a fresh one.

## Basic Implementation

```typescript
class Configuration {
  private static instance: Configuration;
  private settings: Record<string, string> = {};

  // private constructor — nothing outside the class can call `new Configuration()`
  private constructor() {}

  static getInstance(): Configuration {
    if (!Configuration.instance) {
      Configuration.instance = new Configuration();
    }
    return Configuration.instance;
  }

  set(key: string, value: string) {
    this.settings[key] = value;
  }

  get(key: string): string | undefined {
    return this.settings[key];
  }
}

const a = Configuration.getInstance();
const b = Configuration.getInstance();
a.set("env", "production");

console.log(a === b);          // true — same object
console.log(b.get("env"));     // "production" — set through `a`, visible through `b`
```

Two things make this a singleton rather than an ordinary class: the constructor is `private` (nothing outside the class can create a second instance directly), and `getInstance()` lazily creates the one instance on first call and returns that same instance every time after.

## Why Use It

A singleton is the right tool when a resource genuinely needs to be shared and coordinated across an entire application, not duplicated per use:

- A single database [connection pool](../../databases/relational/connection-pooling.md) — creating a second pool wastes connections and defeats the pooling itself.
- A shared in-memory cache — two caches with the same name but different contents is a correctness bug, not just waste.
- An application-wide logger or config object — needs one consistent view of settings everywhere it's read.

## The Pitfalls

| Problem | Why it matters |
|---|---|
| **Global mutable state** | A singleton is effectively a global variable with extra ceremony — any code, anywhere, can read or mutate its state, making data flow hard to trace |
| **Hidden dependencies** | A class that calls `Configuration.getInstance()` internally doesn't declare that dependency in its constructor — it's invisible from the outside, unlike a dependency that's passed in |
| **Hard to test** | Because the instance is shared and often persists for the life of the process, tests can leak state into each other unless the singleton is explicitly reset between tests |
| **Concurrency races** | In multi-threaded runtimes (JVM, .NET), two threads can both pass the `if (!instance)` check before either finishes construction, creating two instances — solved with double-checked locking or eager initialization. Node.js's single-threaded [event loop](../javascript/event-loop.md) mostly sidesteps this for synchronous construction, but an async factory (e.g. `getInstance()` that awaits a DB connection) can still race if called concurrently before the first call resolves |

## Singleton vs. Dependency Injection

Manually calling `Configuration.getInstance()` throughout a codebase is the classic naive singleton — it works, but it hardcodes *how* an instance is obtained into every consumer. [Dependency Injection](../fundamentals/dependency-injection.md) solves the same underlying problem (share one instance) without the downsides: a [DI](../fundamentals/dependency-injection.md) container creates the instance once and *injects* it wherever it's needed, so consumers just declare "I need a `ConfigService`" in their constructor instead of reaching out to a global accessor. The class under test can then be given a mock/fake instance instead of being permanently wired to the real global one.

This is exactly what NestJS providers do by default — see [NestJS's Provider Scope](../../backend/nestjs/providers.md#provider-scope): a provider registered without an explicit `scope` is created **once** and shared everywhere it's injected, which is the Singleton pattern, but implemented through the framework's [IoC](../fundamentals/inversion-of-control.md) container rather than a manually-written `getInstance()` method. The container, not the class itself, owns and enforces the "only one instance" guarantee.

## Common Questions

**Is a NestJS `@Injectable()` provider a Singleton in the GoF sense?**
> Functionally yes — by default NestJS creates one instance per provider per application and injects that same instance everywhere it's requested. It differs from the classic GoF implementation in that the class itself doesn't enforce single-instantiation (no private constructor, no static `getInstance()`) — the [IoC](../fundamentals/inversion-of-control.md) container enforces it externally, which is why it doesn't inherit the "hidden dependency" and "hard to test" downsides of a manually-written singleton.

**Is Singleton an anti-pattern?**
> It's controversial rather than universally condemned. The pattern itself (share one instance) is legitimate and necessary; the criticism is usually really aimed at the *global-accessor* implementation style (`getInstance()` called from anywhere), which introduces hidden coupling. Using [DI](../fundamentals/dependency-injection.md) to manage the single instance instead of a static accessor keeps the benefit while avoiding most of the criticism.

**Easy way to remember:** Singleton = one instance, one global door to it. If a framework's container is handing you that one instance through your constructor instead of you calling a static method to fetch it, you get the same guarantee without the global-state baggage.

## Related

- [Dependency Injection](../fundamentals/dependency-injection.md)
- [Factory Pattern](factory.md)
- [Providers (NestJS)](../../backend/nestjs/providers.md)
- [Services (NestJS)](../../backend/nestjs/services.md#singleton-behavior)
