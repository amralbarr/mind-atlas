# Promise Chaining

Promise chaining means executing asynchronous operations sequentially by returning promises from `.then()`. It is a core JavaScript async concept.

## Why It's Needed

Async operations often depend on the previous async result, for example:

1. Log in the user.
2. Get their profile.
3. Get their orders.

Each step waits for the previous step to complete.

## Simple Promise Example

```javascript
const promise = fetch('/users');
```

A Promise represents a **future result**.

## Promise Chaining Example

```javascript
fetchUser()
  .then(user => {
    return fetchOrders(user.id);
  })
  .then(orders => {
    return fetchProducts(orders);
  })
  .then(products => {
    console.log(products);
  })
  .catch(error => {
    console.error(error);
  });
```

Flow:

```text
fetchUser
    ↓
fetchOrders
    ↓
fetchProducts
```

This is sequential async execution.

## The Important Rule: Return the Promise

Every `.then()` returns a **new** promise, so the chain only continues correctly if you return the next promise from inside the handler.

**Correct:**

```javascript
.then(user => {
  return fetchOrders(user.id);
})
```

**Wrong:**

```javascript
.then(user => {
  fetchOrders(user.id);
})
```

Without `return`, the chain breaks — the next `.then()` won't wait for `fetchOrders` to resolve.

```text
Promise
   ↓ then
Promise
   ↓ then
Promise
```

## Example with Values

```javascript
Promise.resolve(5)
  .then(num => {
    return num * 2;
  })
  .then(result => {
    console.log(result);
  });
```

Output:

```text
10
```

## async/await Equivalent

Promise chaining:

```javascript
fetchUser()
  .then(user => fetchOrders(user.id))
  .then(orders => console.log(orders));
```

Is equivalent to:

```javascript
async function run() {
  const user = await fetchUser();
  const orders = await fetchOrders(user.id);
  console.log(orders);
}
```

## Why async/await Was Introduced

Long promise chains become hard to read — known as **callback pyramid** or **promise hell**.

**Promise hell:**

```javascript
fetchUser()
  .then(user => {
    return fetchOrders(user.id)
      .then(orders => {
        return fetchProducts(orders)
          .then(products => {
            console.log(products);
          });
      });
  });
```

**Better, flat chaining:**

```javascript
fetchUser()
  .then(user => fetchOrders(user.id))
  .then(orders => fetchProducts(orders))
  .then(products => console.log(products));
```

## Error Handling

### A Single `.catch()` Handles the Whole Chain

```javascript
fetchUser()
  .then(user => fetchOrders(user.id))
  .then(orders => console.log(orders))
  .catch(error => {
    console.error(error);
  });
```

Any rejection or thrown error jumps straight to the nearest `.catch()`. Internally, a rejected promise skips remaining `.then()` handlers.

```javascript
Promise.reject("fail")
  .then(() => {
    console.log("never runs");
  })
  .catch(err => {
    console.log(err);
  });
```

## Returning Values vs. Returning Promises

**Return a normal value:**

```javascript
.then(value => {
  return 5;
})
```

This is automatically wrapped into a resolved promise.

**Return a promise:**

```javascript
.then(value => {
  return fetchData();
})
```

The chain waits for that promise to resolve before continuing.

### Promise States

| State | Meaning |
|---|---|
| Pending | Waiting |
| Fulfilled | Success |
| Rejected | Failed |

## Chaining and Microtasks

Promise callbacks (`.then`) execute in the [microtask queue](microtask-vs-macrotask.md) — an important [event loop](event-loop.md) topic.

```javascript
console.log(1);

Promise.resolve().then(() => {
  console.log(2);
});

console.log(3);
```

Output:

```text
1
3
2
```

Synchronous code runs first; microtasks run once the stack is empty.

## Promise Chaining vs. Callback Hell

Old callback style:

```javascript
getUser(user => {
  getOrders(user, orders => {
    getProducts(orders, products => {
      // ...
    });
  });
});
```

This produces deep nesting. Promises flatten the async flow instead.

## Promise Utility Methods

- **`Promise.all`** — runs promises concurrently and waits for all to resolve: `Promise.all([fetchUsers(), fetchOrders()])`.
- **`Promise.race`** — resolves/rejects as soon as the first promise settles.
- **`Promise.allSettled`** — waits for all promises regardless of success or failure.
- **`Promise.any`** — resolves as soon as the first promise succeeds.

## Common Questions

**What is promise chaining?**
> Promise chaining is sequential asynchronous execution achieved by returning promises from `.then()` handlers.

**Why is `return` inside `.then()` important?**
Because the returned promise or value becomes the input to the next step in the chain.

**Difference between chaining and nesting?**
Chaining creates a flat, readable async flow; nesting creates callback hell.

**How do errors propagate?**
Rejected promises skip remaining `.then()` handlers and jump to the nearest `.catch()`.

**Promise chaining vs. async/await?**
`async/await` is syntactic sugar over promises and chaining.

**Where do `.then()` callbacks execute?**
Inside the microtask queue.

## Senior-Level Understanding

Promise chaining enables deterministic async sequencing, centralized error propagation, and composable async workflows. It forms the foundation for async/await, modern JS concurrency patterns, and event-loop scheduling.

> Promise chaining is the composition of asynchronous operations through successive promise resolution, where each `.then()` returns a new promise enabling controlled sequencing, transformation, and centralized rejection propagation within the JavaScript [event loop](event-loop.md)'s microtask model.

## Easy Way to Remember

```text
Promise chaining =
async step-by-step pipeline
```

## Related

- [Asynchronous / Non-Blocking Execution](../fundamentals/asynchronous-non-blocking-execution.md) — the general, language-agnostic promise/future pattern this file specializes into JavaScript's `.then()` chaining syntax
- [The Event Loop](event-loop.md)
- [Microtasks vs Macrotasks](microtask-vs-macrotask.md)
- [Closures](closures.md)
