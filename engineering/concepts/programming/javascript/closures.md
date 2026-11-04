# Closures

A **closure** happens when a function remembers variables from its outer (lexical) scope even after the outer function has finished executing.

## Basic Example

```javascript
function outer() {
  let count = 0;

  function inner() {
    count++;
    console.log(count);
  }

  return inner;
}

const counter = outer();

counter(); // 1
counter(); // 2
counter(); // 3
```

## What's Happening Here?

When `outer()` runs, `count` is created. Normally you'd expect `count` to disappear once `outer()` returns — but because `inner()` is returned and still references `count`, JavaScript keeps that variable alive in memory. That preserved reference is a **closure**.

```text
outer()
 ├── count = 0
 └── returns inner()

inner() remembers:
 └── count variable
```

## Common Uses of Closures

### 1. Private Variables

```javascript
function bankAccount() {
  let balance = 1000;

  return {
    deposit(amount) {
      balance += amount;
      console.log(balance);
    },
    getBalance() {
      return balance;
    }
  };
}

const account = bankAccount();

account.deposit(500);           // 1500
console.log(account.getBalance()); // 1500
console.log(account.balance);   // undefined — not accessible directly
```

The closure creates private state that can only be touched through the returned methods.

### 2. React Hooks and Event Handlers

```javascript
function Component() {
  let name = "Amr";

  function handleClick() {
    console.log(name);
  }

  return <button onClick={handleClick}>Click</button>;
}
```

`handleClick()` remembers `name` from the enclosing scope — this is closure behavior, and it's the mechanism [React hooks](../../frontend/hooks.md) rely on internally.

### 3. `setTimeout` Example

```javascript
function test() {
  let message = "Hello";

  setTimeout(() => {
    console.log(message);
  }, 1000);
}

test();
```

Even after `test()` finishes, the timeout callback still remembers `message`.

## The Classic Question: `var` in a Loop

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => {
    console.log(i);
  }, 100);
}
// 3
// 3
// 3
```

All three callbacks share the *same* `i`, because `var` is function-scoped, not block-scoped. By the time the timeouts run, the loop has finished and `i` is `3`.

Fixing it with `let`:

```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => {
    console.log(i);
  }, 100);
}
// 0
// 1
// 2
```

`let` creates a new block-scoped binding on every iteration, so each closure captures its own `i`. See [var vs let vs const](var-let-const.md) for the full scoping picture.

## Closures and Memory Leaks

Closures can accidentally keep large objects alive if an inner function still references them:

```javascript
function bigData() {
  let hugeArray = new Array(1_000_000).fill("data");

  return function () {
    console.log(hugeArray.length);
  };
}
```

`hugeArray` stays in memory for as long as the returned function does, because the inner function still references it.

## Another Example: Currying

```javascript
function multiply(x) {
  return function (y) {
    return x * y;
  };
}

const double = multiply(2);
console.log(double(5)); // 10
```

`double()` remembers `x = 2` — closure again, this time powering a curried function.

## Key Terms

| Term | Meaning |
|---|---|
| Lexical scope | Scope determined by where code is physically written |
| Closure | A function plus the outer variables it remembers |
| Persistent state | Variables that stay alive in memory via a closure |

## Where Closures Show Up

[React hooks](../../frontend/hooks.md), event handlers, timers, [middleware](../../backend/middleware.md), currying, memoization, factory functions, encapsulation, async callbacks.

## Definition

> A closure is when a function retains access to variables from its lexical scope even after the outer function has completed execution.

**Easy way to remember:** Closure = a function remembers outer variables after the outer function is gone.

## Related

- [Mutation vs Immutability](../fundamentals/mutation.md)
- [var vs let vs const](var-let-const.md)
- [Event Loop](event-loop.md)
- [Microtask vs Macrotask](microtask-vs-macrotask.md)
- [Promise Chaining](promise-chaining.md)
