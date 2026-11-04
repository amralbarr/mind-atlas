# Polymorphism

Polymorphism means **"one interface, many implementations"** — the same method name produces different behavior depending on the object that calls it.

## Basic Example

```python
class Dog:
    def speak(self):
        print("Bark")

class Cat:
    def speak(self):
        print("Meow")
```

Both classes define `speak()`, but its behavior differs per class. That same interface lets you treat different objects uniformly:

```python
animals = [Dog(), Cat()]

for animal in animals:
    animal.speak()
# Bark
# Meow
```

## What's Happening Internally: Duck Typing

Python doesn't check the object's type before calling `speak()` — it only checks whether the method exists, and calls it if so. This is **duck typing**:

> "If it walks like a duck and quacks like a duck, it is a duck."

Python doesn't care about the class; it only cares whether the method is present.

## Types of Polymorphism

- **Compile-time** — method overloading (common in Java, C++; not really a Python-native concept)
- **Runtime** — method overriding and duck typing (the Python-idiomatic form)

## Real-World Example: A Payment System

```python
class CreditCard:
    def pay(self):
        print("Pay using credit card")

class PayPal:
    def pay(self):
        print("Pay using PayPal")

def checkout(payment_method):
    payment_method.pay()

checkout(CreditCard())  # Pay using credit card
checkout(PayPal())      # Pay using PayPal
```

## Why Polymorphism Is Powerful

- **Flexibility** — you don't have to change existing logic when adding a new class.
- **Scalability** — new types can be added without touching callers.
- **Clean code** — no `if/else` explosion checking object types.

Without polymorphism, code tends to look like this:

```python
def pay(method):
    if method == "card":
        print("card payment")
    elif method == "paypal":
        print("paypal payment")
```

This is hard to extend and violates the open/closed principle — every new payment type requires editing this function. With polymorphism, adding `ApplePay` just means adding a new class with a `pay()` method; the `checkout()` caller never changes.

## Relation to the Other OOP Pillars

Polymorphism is one of the four pillars of [OOP](oop.md), alongside encapsulation, inheritance, and [abstraction](abstraction.md).

## Definition

> Polymorphism is an [OOP](oop.md) concept where different classes implement the same method interface, allowing objects to be treated uniformly while exhibiting different behaviors at runtime.

**One-line memory trick:** Same method name → different behavior per object.

## Related

- [Object-Oriented Programming (OOP)](oop.md)
- [Abstraction](abstraction.md)
- [interface vs type](../typescript/interface-vs-type.md)
