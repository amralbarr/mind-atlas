# Strategy Pattern

The Strategy pattern defines a family of interchangeable algorithms, encapsulates each one behind a common interface, and lets the calling code swap between them at runtime — without an `if`/`switch` chain scattered through the code that uses them.

## The Problem It Solves

Without Strategy, adding a new variant of a behavior usually means growing a conditional:

```typescript
function calculatePrice(base: number, customerType: string): number {
  if (customerType === "regular") {
    return base;
  } else if (customerType === "premium") {
    return base * 0.9;
  } else if (customerType === "vip") {
    return base * 0.8;
  }
  // every new tier means editing this function again
  return base;
}
```

Every new pricing tier means editing this function again — the function grows without bound, and testing one tier means understanding the whole `if` chain.

## Basic Implementation

```typescript
interface PricingStrategy {
  calculate(base: number): number;
}

class RegularPricing implements PricingStrategy {
  calculate(base: number) {
    return base;
  }
}

class PremiumPricing implements PricingStrategy {
  calculate(base: number) {
    return base * 0.9;
  }
}

class VipPricing implements PricingStrategy {
  calculate(base: number) {
    return base * 0.8;
  }
}

class PriceCalculator {
  constructor(private strategy: PricingStrategy) {}

  setStrategy(strategy: PricingStrategy) {
    this.strategy = strategy;
  }

  calculate(base: number): number {
    return this.strategy.calculate(base);
  }
}

const calculator = new PriceCalculator(new RegularPricing());
console.log(calculator.calculate(100)); // 100

calculator.setStrategy(new VipPricing());
console.log(calculator.calculate(100)); // 80
```

`PriceCalculator` doesn't know or care which concrete pricing rule it's running — it just delegates to whatever `PricingStrategy` it currently holds. Adding a new tier means adding one new class; `PriceCalculator` itself never changes.

## Strategy as a Plain Function

TypeScript/JavaScript have first-class functions, so a full interface + classes is often more ceremony than needed for a simple, stateless strategy:

```typescript
type PricingFn = (base: number) => number;

const regular: PricingFn = (base) => base;
const premium: PricingFn = (base) => base * 0.9;
const vip: PricingFn = (base) => base * 0.8;

function calculatePrice(base: number, strategy: PricingFn): number {
  return strategy(base);
}

calculatePrice(100, vip); // 80
```

This is the same pattern with less boilerplate — the "interface" is just the function signature. Reach for the class-based version instead when a strategy needs to carry its own state or expose more than one method (e.g. `validate()` and `apply()` on the same strategy object).

## When to Use It (and When Not To)

| Use Strategy when | Skip it when |
|---|---|
| The number of algorithm variants is likely to grow over time | There are only two variants and they're never going to grow — a single `if`/`else` is clearer |
| The choice of algorithm needs to be made or changed at runtime (config, user tier, feature flag) | The "algorithm" is trivial (e.g. `a + b` vs. `a - b`) — the [abstraction](../fundamentals/abstraction.md) costs more than the `if` it replaces |
| Each variant has enough internal logic/state that a plain function would need extra parameters to fake it | Variants share almost all their logic and differ only in one small parameter — a config value may be simpler than a whole class per variant |

## Strategy vs. Factory

These are often used together but solve different problems: [Factory](factory.md) is about **which object gets constructed**; Strategy is about **which behavior an already-constructed object executes**. A factory frequently constructs the correct strategy object based on some input:

```typescript
function pricingStrategyFactory(tier: "regular" | "premium" | "vip"): PricingStrategy {
  switch (tier) {
    case "regular": return new RegularPricing();
    case "premium": return new PremiumPricing();
    case "vip": return new VipPricing();
  }
}

const calculator = new PriceCalculator(pricingStrategyFactory("premium"));
```

## Common Questions

**How is this different from just passing a callback function?**
> For simple, stateless behavior, it isn't meaningfully different — a callback *is* a valid Strategy implementation in a language with first-class functions. The pattern earns the extra ceremony (interface + classes) once a strategy needs to hold its own configuration/state or expose multiple related methods that a bare function can't cleanly represent.

**Isn't this the same as [polymorphism](../fundamentals/polymorphism.md)?**
> Strategy is a specific *application* of [polymorphism](../fundamentals/polymorphism.md) (see [Polymorphism](../fundamentals/polymorphism.md)) — instead of subclassing to change behavior, an object is *composed* with an interchangeable strategy object at runtime. It gets you similar flexibility to inheritance-based overriding, without locking the behavior into a fixed class hierarchy.

**Easy way to remember:** Strategy = swap the *how*, keep the *what* the same. `PriceCalculator.calculate()` is always called the same way; which math actually runs depends entirely on which strategy object it's holding.

## Related

- [Factory Pattern](factory.md)
- [Polymorphism](../fundamentals/polymorphism.md)
- [Observer Pattern](observer.md)
