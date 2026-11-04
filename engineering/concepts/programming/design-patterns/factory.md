# Factory Pattern (Factory Method & Abstract Factory)

Both are creational patterns that move object creation out of calling code and into a dedicated method/object — the caller asks for "a thing that does X" without knowing (or caring) which concrete class gets constructed. They're the same core idea applied at two different scopes: **Factory Method** creates one product; **Abstract Factory** creates a whole *family* of related products that need to stay consistent with each other.

## Factory Method — One Product, Many Possible Types

A single creation method that subclasses (or a `type` parameter) can override/branch on to decide which concrete class actually gets instantiated:

```typescript
interface Notification {
  send(message: string): void;
}

class EmailNotification implements Notification {
  send(message: string) {
    console.log(`Email: ${message}`);
  }
}

class SmsNotification implements Notification {
  send(message: string) {
    console.log(`SMS: ${message}`);
  }
}

class PushNotification implements Notification {
  send(message: string) {
    console.log(`Push: ${message}`);
  }
}

type NotificationType = "email" | "sms" | "push";

function notificationFactory(type: NotificationType): Notification {
  switch (type) {
    case "email":
      return new EmailNotification();
    case "sms":
      return new SmsNotification();
    case "push":
      return new PushNotification();
  }
}

const notifier = notificationFactory("sms");
notifier.send("Your order has shipped");
```

Calling code never writes `new SmsNotification()` directly — it asks the factory for "a notification of this type" and gets back something satisfying the `Notification` interface. Adding a new notification channel means adding one class and one `case`, not hunting down every place `new EmailNotification()` was hardcoded.

## Abstract Factory — Families of Related Products

Abstract Factory is a factory *of factories*: one interface groups several creation methods that each return a different product, but all products from one concrete factory are guaranteed to belong to the same family (i.e. mutually compatible).

```typescript
interface Button {
  render(): string;
}
interface Checkbox {
  render(): string;
}

// Family 1: Windows-style
class WindowsButton implements Button {
  render() { return "[Windows Button]"; }
}
class WindowsCheckbox implements Checkbox {
  render() { return "[Windows Checkbox]"; }
}

// Family 2: Mac-style
class MacButton implements Button {
  render() { return "(Mac Button)"; }
}
class MacCheckbox implements Checkbox {
  render() { return "(Mac Checkbox)"; }
}

interface UIFactory {
  createButton(): Button;
  createCheckbox(): Checkbox;
}

class WindowsUIFactory implements UIFactory {
  createButton(): Button { return new WindowsButton(); }
  createCheckbox(): Checkbox { return new WindowsCheckbox(); }
}

class MacUIFactory implements UIFactory {
  createButton(): Button { return new MacButton(); }
  createCheckbox(): Checkbox { return new MacCheckbox(); }
}

function renderUI(factory: UIFactory) {
  const button = factory.createButton();
  const checkbox = factory.createCheckbox();
  console.log(button.render(), checkbox.render());
}

renderUI(new MacUIFactory());
// (Mac Button) (Mac Checkbox) — never a mismatched WindowsButton + MacCheckbox
```

The guarantee Abstract Factory provides that a plain Factory Method doesn't: swapping `MacUIFactory` for `WindowsUIFactory` changes *every* product it creates consistently — there's no code path where the button comes from one family and the checkbox from another.

## Factory Method vs. Abstract Factory

| | Factory Method | Abstract Factory |
|---|---|---|
| Creates | One product | A family of related products |
| Mechanism | One method, often overridden by subclasses or branching on a parameter | One interface with several creation methods, implemented once per family |
| Typical structure | Inheritance (subclass decides the concrete type) | Composition (a factory object is passed in and used) |
| Adds a new variant | Add one class + one branch | Add one new factory class implementing the whole interface |
| Guarantees cross-product consistency | No | Yes — one factory instance produces only compatible products |

## When a Factory Isn't Worth It

If there's only ever one concrete implementation, or the choice never needs to vary at runtime, a factory is unnecessary indirection — just call the constructor directly. Factories earn their place once the concrete type is chosen dynamically (config, user input, environment) and calling code shouldn't need to know about every possible concrete class to make that choice.

## Common Questions

**Isn't a factory just a function that returns different classes?**
> At its simplest, yes — `notificationFactory()` above is exactly that. The pattern name mostly matters for communicating intent (and for Abstract Factory, for enforcing family consistency) rather than requiring specific ceremony; in TypeScript/JavaScript, a plain function is a completely legitimate Factory Method implementation.

**How does this relate to NestJS's `useFactory` providers?**
> Directly — [`useFactory` providers](../../backend/nestjs/providers.md#3-factory-providers) are the Factory pattern applied to NestJS's [DI](../fundamentals/dependency-injection.md) container: instead of the container instantiating a class directly, it calls your factory function (sync or async) and injects whatever that function returns. This is commonly used for values that need runtime computation to construct, like a database connection or a config object assembled from environment variables.

**When do I need Abstract Factory instead of Factory Method?**
> When more than one related object needs to be created together and they must come from the same family — e.g. a database factory that must return a matching connection, query builder, and migration runner for whichever database engine is configured, never a mismatched combination.

**Easy way to remember:** Factory Method = "give me one of these, you decide which subtype." Abstract Factory = "give me a whole matching set."

## Related

- [Singleton Pattern](singleton.md)
- [Providers (NestJS)](../../backend/nestjs/providers.md#3-factory-providers)
- [Dependency Injection](../fundamentals/dependency-injection.md)
