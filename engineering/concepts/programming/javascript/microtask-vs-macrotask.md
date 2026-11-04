# Microtasks vs Macrotasks

This is one of the most common JavaScript topics. The difference is mainly about **execution priority** inside the [event loop](event-loop.md).

## Quick Summary

| Type      | Examples                    | Priority |
| --------- | --------------------------- | -------- |
| Microtask | `Promise`, `queueMicrotask` | Higher   |
| Macrotask | `setTimeout`, `setInterval` | Lower    |

## Event Loop Order

JavaScript executes in this order, and this rule is extremely important:

```text
1. Synchronous code
2. ALL microtasks
3. ONE macrotask
4. Repeat
```

## Macrotasks (Task Queue)

These are normal async tasks: `setTimeout()`, `setInterval()`, `setImmediate()` (Node.js), DOM events. They go to the **callback queue / task queue**.

## Microtasks

These have higher priority: `Promise.then()`, `Promise.catch()`, `Promise.finally()`, `queueMicrotask()`, `MutationObserver`. They go to the **microtask queue**.

### The Important Rule

Before JavaScript executes any macrotask, it empties the **entire** microtask queue first.

## Example 1

```javascript
console.log("1");

setTimeout(() => {
  console.log("2");
}, 0);

Promise.resolve().then(() => {
  console.log("3");
});

console.log("4");
```

Output:

```text
1
4
3
2
```

Walking through it:

1. `console.log("1")` runs synchronously → `1`.
2. `setTimeout(...)` schedules its callback on the macrotask queue for later.
3. `Promise.resolve().then(...)` schedules its callback on the microtask queue.
4. `console.log("4")` runs synchronously → `4`.
5. The stack is now empty. [The event loop](event-loop.md) drains the microtask queue first → `3`, then moves to the macrotask queue → `2`.

```text
Call Stack Empty

Microtask Queue:
  Promise.then()

Macrotask Queue:
  setTimeout()

↓ Execute microtasks first
```

## Example 2 — Multiple Microtasks

```javascript
console.log("start");

Promise.resolve().then(() => {
  console.log("microtask 1");
});

Promise.resolve().then(() => {
  console.log("microtask 2");
});

setTimeout(() => {
  console.log("timeout");
}, 0);

console.log("end");
```

Output:

```text
start
end
microtask 1
microtask 2
timeout
```

JavaScript empties **all** microtasks before moving on to macrotasks.

## Dangerous Example — Starvation

```javascript
function loop() {
  Promise.resolve().then(loop);
}

loop();

setTimeout(() => {
  console.log("timeout");
}, 0);
```

`setTimeout` may **never** execute here, because the microtask queue never becomes empty. This is called **[event loop](event-loop.md) starvation**.

## `queueMicrotask` Example

```javascript
queueMicrotask(() => {
  console.log("microtask");
});

setTimeout(() => {
  console.log("timeout");
}, 0);
```

Output:

```text
microtask
timeout
```

## Browser Rendering Note

Browser rendering usually happens between macrotasks. Too many microtasks can delay UI updates.

## Node.js Special Cases

Node.js also has `process.nextTick()`, which has **even higher** priority than Promise microtasks. Order in Node.js:

```text
1. Sync code
2. process.nextTick
3. Promise microtasks
4. Macrotasks
```

## Detailed Definitions

**Microtask**
> A high-priority async task executed immediately after the current call stack completes and before macrotasks.

**Macrotask**
> A standard async task scheduled to run in a future [event loop](event-loop.md) iteration, after all microtasks have completed.

## Common Questions

**Which executes first, `setTimeout` or `Promise`?**
The Promise, because the microtask queue has higher priority than the macrotask queue.

**Does `setTimeout(fn, 0)` execute immediately?**
No — it waits for the current stack to finish and for all microtasks to drain first.

## Senior-Level Real Usage

Microtasks matter for React state batching, async rendering, promise chains, streaming systems, and Node.js performance optimization.

## Easy Way to Remember

```text
Microtask = urgent queue
Macrotask = normal queue
```

Or simply: **Promise before `setTimeout`.**

## Related

- [The Event Loop](event-loop.md)
- [Promise Chaining](promise-chaining.md)
- [Closures](closures.md)
