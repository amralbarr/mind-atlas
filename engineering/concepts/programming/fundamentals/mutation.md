# Mutation vs Immutability

**Mutation** means changing data directly after it has already been created, rather than creating a new copy with the changed value.

```javascript
const user = { name: "Amr" };

user.name = "Ali"; // mutation — same object, new value
```

Before: `{ name: "Amr" }`. After: `{ name: "Ali" }` — same object reference, different contents.

## Primitive vs. Reference Types

**Primitives** (string, number, boolean, null, undefined) can only be *reassigned*, not mutated:

```javascript
let x = 5;
x = 10; // reassignment, not mutation
```

**Reference types** (objects, arrays, functions) *can* be mutated in place:

```javascript
const arr = [1, 2];
arr.push(3); // array mutated
```

## Mutation vs. Immutable Update

- **Mutation** changes the original data: `user.name = "Ali";`
- **Immutable update** creates a new object and leaves the original untouched:

```javascript
const newUser = {
  ...user,
  name: "Ali"
};
```

## Why React Cares About Mutation

React relies on **reference comparison** to detect state changes efficiently. If you mutate state directly, the reference stays the same and React may not detect the change or re-render.

```jsx
// BAD — same object reference, React may skip re-render
const [user, setUser] = useState({ name: "Amr" });
user.name = "Ali";
setUser(user);

// GOOD — new object, React detects the change
setUser({
  ...user,
  name: "Ali"
});
```

The same principle applies to arrays:

```javascript
// BAD — mutates the original array
items.push(newItem);

// GOOD — creates a new array
setItems([...items, newItem]);
```

### Common Array Methods

**Mutating** — change the original array in place:

| Method | Returns | Notes |
|---|---|---|
| `push(item)` | New length | Adds to the end |
| `pop()` | Removed element | Removes from the end |
| `unshift(item)` | New length | Adds to the start |
| `shift()` | Removed element | Removes from the start |
| `splice(start, count, ...items)` | Array of removed elements | Insert/remove/replace at any index |
| `sort(compareFn)` | The same array | Sorts in place — see gotcha below |
| `reverse()` | The same array | Reverses in place — see gotcha below |
| `fill(value)` | The same array | Overwrites elements with a static value |
| `copyWithin()` | The same array | Rarely used; copies part of the array over itself |

**Non-mutating** — return a new array or value, leave the original untouched:

| Method | Returns |
|---|---|
| `map(fn)` | New array |
| `filter(fn)` | New array |
| `slice(start, end)` | New array (shallow copy of a range) |
| `concat(...arrays)` | New array |
| `flat(depth)` / `flatMap(fn)` | New array |
| `reduce(fn, initial)` | Accumulated value (any type) |
| `find(fn)` / `findIndex(fn)` | Element / index |
| `includes(value)` / `indexOf(value)` | Boolean / index |
| `some(fn)` / `every(fn)` | Boolean |
| `join(separator)` | String |

**Gotcha — `sort` and `reverse` mutate *and* return the array**, so this looks immutable but isn't:

```javascript
const sorted = arr.sort(); // arr itself is now sorted too — not a copy
```

Copy first if the original must stay untouched:

```javascript
const sorted = [...arr].sort();
```

**Modern non-mutating alternatives (ES2023):** `toSorted()`, `toReversed()`, `toSpliced()`, and `with(index, value)` behave like their mutating counterparts but return a new array instead of touching the original. Check runtime/browser support before relying on them in older environments.

## Reference Comparison

```javascript
const a = { name: "Amr" };
const b = a;
a === b; // true — same reference

const c = { ...a };
a === c; // false — different reference, even with identical values
```

## Why Immutability Matters

- Predictable state
- Easier debugging
- Enables React's rendering optimizations (e.g., memoization)
- Enables undo/redo support
- Redux, in particular, strictly avoids mutation and relies entirely on immutable updates

## Deep Mutation

Nested objects are easy to mutate accidentally:

```javascript
// BAD — mutates a nested object
user.address.city = "Riyadh";

// BETTER — immutable update at every level that changed
setUser({
  ...user,
  address: {
    ...user.address,
    city: "Riyadh"
  }
});
```

The same pattern applies to arrays inside state:

```javascript
// BAD
state.users.push(user);

// GOOD
state.users = [...state.users, user];
```

## Common Questions

**Why avoid mutation in React?**
> React relies on immutable updates and reference comparison to efficiently detect state changes and trigger re-renders.

**What is an immutable update?**
> Creating new objects or arrays instead of modifying existing ones.

**Senior-level answer:**
> Mutation is the direct modification of existing data structures. In React and modern frontend architectures, immutable updates are preferred because they enable predictable state management and efficient change detection through reference comparison.

**Easy way to remember:** Mutation = change the existing object. Immutability = create a new object.

## Related

- [Closures](../javascript/closures.md)
- [var vs let vs const](../javascript/var-let-const.md)
