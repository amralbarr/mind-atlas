# interface vs type

Both `interface` and `type` describe the shape of data in TypeScript, but they have important differences.

## Quick Summary

| Feature | `interface` | `type` |
|---|---|---|
| Object shape | Yes | Yes |
| Extendable | Yes | Yes |
| Declaration merging | Yes | No |
| Union types | No | Yes |
| Tuples | No | Yes |
| Primitive aliases | No | Yes |
| Function types | Yes | Yes |
| Recommended for objects/classes | Yes | Possible |
| Complex type transformations | Limited | Powerful |

## Basic Example

```typescript
// interface
interface User {
  name: string;
  age: number;
}

// type
type User = {
  name: string;
  age: number;
};
```

Both work equivalently for simple object shapes.

## 1. Declaration Merging

Only `interface` supports this. Two declarations with the same name are automatically merged:

```typescript
interface User {
  name: string;
}

interface User {
  age: number;
}

const user: User = {
  name: "Amr",
  age: 28
};
```

`type` does **not** allow this — a duplicate `type User` is a compile error.

This matters most for library and framework extension points, such as augmenting Express's request object in a NestJS/Express backend:

```typescript
declare global {
  namespace Express {
    interface Request {
      user: JwtPayload;
    }
  }
}
```

## 2. Union Types

`type` is significantly more powerful here — `interface` cannot express a union at all:

```typescript
type Status = "success" | "error" | "loading";
```

## 3. Primitive Aliases

```typescript
type ID = string; // fine

interface ID = string; // not possible
```

## 4. Tuples

```typescript
type Point = [number, number]; // fine with type

// interface is not a good fit for tuples
```

## 5. Function Types

Both support function types:

```typescript
interface Add {
  (a: number, b: number): number;
}

type Add = (a: number, b: number) => number;
```

## 6. Extending

Both support composition, with different syntax:

```typescript
// interface extends
interface Animal {
  name: string;
}

interface Dog extends Animal {
  breed: string;
}

// type intersection
type Animal = {
  name: string;
};

type Dog = Animal & {
  breed: string;
};
```

## 7. Classes

Interfaces are the natural fit for defining a contract that a class implements:

```typescript
interface Vehicle {
  start(): void;
}

class Car implements Vehicle {
  start() {
    console.log("Started");
  }
}
```

This pairs naturally with [OOP](../fundamentals/oop.md) principles like [polymorphism](../fundamentals/polymorphism.md), where multiple classes implement the same interface differently.

## Which Should You Use?

**Use `interface` for:**
- Object shapes
- Classes
- Public APIs
- [OOP](../fundamentals/oop.md)-style architecture

**Use `type` for:**
- Unions
- Tuples
- Utility types
- Complex type transformations
- Advanced generics, e.g. `type Nullable<T> = T | null;`

## Real-World Examples

A NestJS [DTO](../../backend/api/dto.md) shape is typically an `interface`:

```typescript
interface UserPayload {
  id: string;
  email: string;
}
```

Frontend state that models a finite set of values is typically a `type` union:

```typescript
type LoadingState = "idle" | "loading" | "success" | "error";
```

## Is `interface` Faster?

Historically, interfaces had minor compiler optimizations. Today there's practically no runtime difference, because TypeScript types are erased entirely at compile time — the distinction is purely about developer ergonomics and expressiveness.

## Senior-Level Answer

> `interface` is primarily designed for defining object contracts and supports declaration merging, making it ideal for [OOP](../fundamentals/oop.md) and extensible APIs. `type` is more flexible and can represent unions, primitives, tuples, and advanced mapped types.

**Easy way to remember:** `interface` = object contract. `type` = type manipulation tool.

## Related

- [Object-Oriented Programming (OOP)](../fundamentals/oop.md)
- [Abstraction](../fundamentals/abstraction.md)
- [Dependency Injection](../fundamentals/dependency-injection.md)
