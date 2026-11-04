# var vs let vs const

One of the most common JavaScript questions is the difference between `var`, `let`, and `const`.

## Quick Summary

| Feature | `var` | `let` | `const` |
|---|---|---|---|
| Scope | Function scope | Block scope | Block scope |
| Re-declare | Yes | No | No |
| Re-assign | Yes | Yes | No |
| Hoisted | Yes | Yes | Yes |
| Temporal Dead Zone | No | Yes | Yes |
| Attached to global object | Yes | No | No |

## 1. Scope

`var` is **function-scoped** — it ignores block (`{}`) boundaries:

```javascript
function test() {
  if (true) {
    var x = 10;
  }
  console.log(x); // 10
}
```

`let` and `const` are **block-scoped** — they only exist inside the block where they're declared:

```javascript
function test() {
  if (true) {
    let x = 10;
  }
  console.log(x); // ReferenceError
}
```

```text
{
   let a = 1;    ← inside block only
   const b = 2;  ← inside block only
   var c = 3;    ← leaks outside the block
}
```

## 2. Reassignment

```javascript
var name = "Amr";
name = "Ali"; // allowed

let age = 25;
age = 30; // allowed

const country = "Saudi";
country = "Egypt"; // Error
```

**Important nuance:** `const` means the *variable binding* can't be reassigned — it does not make the value itself immutable.

```javascript
const user = { name: "Amr" };
user.name = "Ali";        // works — object contents changed, not the reference
console.log(user.name);   // "Ali"

const user2 = {};
user2 = {};                // Error — this reassigns the reference itself
```

See [Mutation vs Immutability](../fundamentals/mutation.md) for more on the difference between changing a reference and changing what it points to.

## 3. Redeclaration

```javascript
var x = 1;
var x = 2; // allowed

let y = 1;
let y = 2; // Error

const z = 1;
const z = 2; // Error
```

## 4. Hoisting and the Temporal Dead Zone

All three are hoisted, but they behave differently once hoisted.

`var` is hoisted and initialized as `undefined`:

```javascript
console.log(a); // undefined
var a = 5;

// internally equivalent to:
var a;
console.log(a);
a = 5;
```

`let` and `const` are hoisted but **not initialized** — accessing them before their declaration throws:

```javascript
console.log(a); // ReferenceError
let a = 5;
```

This is the **Temporal Dead Zone (TDZ)**: the variable exists in memory but cannot be accessed before its declaration is reached.

```javascript
{
  console.log(a); // TDZ — throws here
  let a = 5;
}
```

## 5. Global Object Behavior

```javascript
var test = "hello";
console.log(window.test); // "hello" — exists on the global object (browser)

let test2 = "hello";
console.log(window.test2); // undefined
```

## The Classic Loop Example

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// 3
// 3
// 3
```

All callbacks share the same `i` because `var` is function-scoped — by the time the timeouts fire, the loop has already finished.

```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// 0
// 1
// 2
```

`let` creates a new block scope per iteration, so each callback closes over its own `i`. See [Closures](closures.md) for why this works.

## Recommended Usage

- **Use `const` by default.**
- **Use `let`** when the value needs to change.
- **Avoid `var`** — its function scoping, hoisting behavior, and loop-variable sharing are common sources of bugs.

```javascript
const → default choice
let   → when reassignment is needed
var   → avoid
```

## Detailed Explanation

> `var` is function-scoped and allows redeclaration, while `let` and `const` are block-scoped. `let` allows reassignment, `const` does not. `let` and `const` also have Temporal Dead Zone behavior, which prevents access before declaration.

## Related

- [Closures](closures.md)
- [Mutation vs Immutability](../fundamentals/mutation.md)
- [Event Loop](event-loop.md)
