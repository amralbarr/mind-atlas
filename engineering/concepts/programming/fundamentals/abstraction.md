# Abstraction

Abstraction means hiding implementation details and exposing only the essential features — you use something without knowing how it works internally.

## Real-Life Example

You use a car by pressing the accelerator to move and the brake to stop. You don't need to know how engine combustion works internally — that hidden complexity is abstraction.

In programming terms: expose **what** something does, hide **how** it does it.

## Example: Abstract Classes in Python

```python
from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def pay(self):
        pass
```

Concrete subclasses provide the actual implementation:

```python
class CreditCard(Payment):
    def pay(self):
        print("Pay using Credit Card")

class PayPal(Payment):
    def pay(self):
        print("Pay using PayPal")

def checkout(payment: Payment):
    payment.pay()

checkout(CreditCard())  # Pay using Credit Card
checkout(PayPal())      # Pay using PayPal
```

The caller only sees `pay()` — it doesn't care about API calls, encryption, database checks, or validation logic happening underneath.

## Why Abstraction Matters

1. **Reduces complexity** — callers don't deal with internal logic.
2. **Improves maintainability** — internal code can change without affecting consumers.
3. **Improves scalability** — new implementations can be added without touching existing code.

Without abstraction, code tends to accumulate type-checking branches:

```python
class Payment:
    def pay(self, type):
        if type == "card":
            print("card logic")
        elif type == "paypal":
            print("paypal logic")
```

This is messy, hard to extend, and violates the open/closed principle. With abstraction, each class handles its own logic and the caller just calls `payment.pay()`.

## Abstraction vs. Encapsulation

These two are frequently confused:

| Concept | Focus |
|---|---|
| Abstraction | Hides *complexity* — focuses on **what** an object does |
| Encapsulation | Hides *data* — focuses on **protecting** internal state |

```python
class BankAccount:
    def __init__(self):
        self.__balance = 0       # encapsulation — restrict access to data

    def deposit(self, amount):   # abstraction — expose a simple operation
        self.__balance += amount
```

## A System-Level Example

In a typical web architecture, the frontend calls an API and doesn't know how the backend works — it only sees the endpoint and the response. The backend hides validation, database queries, and business logic behind that interface. That's abstraction applied at the system level, not just the class level.

## Relation to the Other OOP Pillars

Abstraction is one of the four pillars of [OOP](oop.md), alongside encapsulation, inheritance, and [polymorphism](polymorphism.md).

## Definition

> Abstraction is an [OOP](oop.md) principle that hides internal implementation details and exposes only essential functionalities to the user, allowing focus on what an object does rather than how it does it.

**One-line memory trick:** Abstraction = hide complexity, show usage.

## Related

- [Database Abstraction](../../backend/data/database-abstraction.md) — a specific, named application of this principle to the data layer
- [Object-Oriented Programming (OOP)](oop.md)
- [Polymorphism](polymorphism.md)
- [Dependency Injection](dependency-injection.md)
- [interface vs type](../typescript/interface-vs-type.md)
