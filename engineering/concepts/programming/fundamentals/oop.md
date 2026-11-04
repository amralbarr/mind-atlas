# Object-Oriented Programming (OOP)

## What Is OOP?

Object-Oriented Programming means organizing code around **objects and classes** instead of relying only on standalone functions. It's foundational for backend systems, APIs, and scalable applications.

A useful real-world analogy is a car. A car has:

- **Properties** — color, speed, brand
- **Behaviors** — `start()`, `stop()`, `accelerate()`

In OOP terms:

- properties → **attributes**
- behaviors → **methods**

## Classes and Objects

A **class** is a blueprint/template for creating objects. An **object** is an instance created from that class.

```python
class Car:
    pass

car1 = Car()  # car1 is now an object
```

### Attributes and the Constructor

```python
class Car:
    def __init__(self, brand, color):
        self.brand = brand
        self.color = color

car1 = Car("Toyota", "Black")
print(car1.brand)  # Toyota
```

`__init__` is the **constructor** — it runs automatically whenever a new object is created.

### Methods and `self`

Methods are functions defined inside a class. `self` refers to the current object instance — `self.brand` means "this object's brand."

```python
class Car:
    def __init__(self, brand):
        self.brand = brand

    def show_brand(self):
        print(self.brand)

car1 = Car("BMW")
car1.show_brand()  # BMW
```

## The Four Pillars of OOP

### 1. Encapsulation

Encapsulation hides internal details and protects data from direct, uncontrolled modification. A double-underscore prefix makes an attribute private-like in Python:

```python
class BankAccount:
    def __init__(self):
        self.__balance = 0

    def deposit(self, amount):
        self.__balance += amount
```

Callers interact with `deposit()` rather than mutating `__balance` directly.

### 2. Inheritance

One class inherits attributes and methods from another, enabling code reuse, hierarchy, and extensibility.

```python
class Animal:
    def speak(self):
        print("Animal sound")

class Dog(Animal):
    pass

dog = Dog()
dog.speak()  # Animal sound (inherited)
```

### 3. Polymorphism

Different classes implement the same method name with different behavior:

```python
class Dog:
    def speak(self):
        print("Bark")

class Cat:
    def speak(self):
        print("Meow")

animals = [Dog(), Cat()]
for animal in animals:
    animal.speak()
# Bark
# Meow
```

See [Polymorphism](polymorphism.md) for a deeper treatment, including duck typing and the open/closed principle.

### 4. Abstraction

[Abstraction](abstraction.md) hides implementation complexity and exposes only what's essential — a driver calls `start()` without knowing how the engine works internally.

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        print("Bark")
```

See [Abstraction](abstraction.md) for more, including how it differs from encapsulation.

## Class Variables vs. Instance Variables

| | Class Variable | Instance Variable |
|---|---|---|
| Scope | Shared across all objects | Unique per object |
| Example | `wheels = 4` (defined on the class) | `self.brand` (set per instance) |

```python
class Car:
    wheels = 4          # class variable — shared

    def __init__(self, brand):
        self.brand = brand  # instance variable — unique
```

## Static Methods and Class Methods

**Static methods** don't access instance or class state:

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b

Math.add(1, 2)
```

**Class methods** operate on the class itself via `cls`:

```python
class Car:
    total = 0

    @classmethod
    def count(cls):
        return cls.total
```

## Magic Methods

Python's "dunder" methods customize how objects behave with built-in operations:

| Method | Purpose |
|---|---|
| `__init__` | Constructor |
| `__str__` | String representation |
| `__len__` | Length |
| `__repr__` | Debugging representation |

```python
class User:
    def __str__(self):
        return "User object"
```

## Composition vs. Inheritance

- **Inheritance** — `Dog IS-A Animal`
- **Composition** — `Car HAS-A Engine`

| Inheritance | Composition |
|---|---|
| IS-A | HAS-A |
| Tight coupling | Flexible |

Composition is usually preferred where flexibility matters more than a strict hierarchy — it avoids locking classes into rigid parent/child relationships.

## Common Questions

**What is OOP?**
> A programming paradigm that organizes code using classes and objects to improve modularity, reusability, and maintainability.

**What are the four pillars of OOP?**
Encapsulation, Inheritance, [Polymorphism](polymorphism.md), [Abstraction](abstraction.md).

**What is `self` in Python?**
It represents the current object instance.

**Why use encapsulation?**
To protect internal data and enforce controlled access to it.

**Senior-level answer:**
> OOP in Python structures applications around classes and objects, enabling encapsulation, inheritance, [polymorphism](polymorphism.md), and [abstraction](abstraction.md) for scalable, reusable, and maintainable software design.

**Easy way to remember:** Class = blueprint. Object = real instance.

## Related

- [Polymorphism](polymorphism.md)
- [Abstraction](abstraction.md)
- [interface vs type](../typescript/interface-vs-type.md)
- [Dependency Injection](dependency-injection.md)
- [Singleton Pattern](../design-patterns/singleton.md) · [Factory Pattern](../design-patterns/factory.md) · [Observer Pattern](../design-patterns/observer.md) · [Strategy Pattern](../design-patterns/strategy.md)
