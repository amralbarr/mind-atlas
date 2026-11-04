# The Event Loop

The **event loop** is what allows JavaScript to handle async operations, timers, API calls, promises, and user events even though JavaScript itself is single-threaded.

## Core Idea

JavaScript can only execute one thing at a time, using the **call stack**. Async tasks are handled outside the stack and later returned to it via the **event loop**.

## Main Components

1. Call Stack
2. Web APIs / Node APIs
3. Callback Queue (Macrotask Queue)
4. Microtask Queue
5. Event Loop

### 1. Call Stack

This is where functions execute. Functions are pushed onto the stack when called and popped off when they return.

```javascript
function a() {
  b();
}

function b() {
  console.log("Hello");
}

a();
```

```text
Call Stack

a()
b()
console.log()
```

### 2. Web APIs (Browser) / Node APIs

JavaScript itself does NOT handle timers, [HTTP](../../networking/http.md) requests, or DOM events — the browser or Node.js runtime handles them.

```javascript
setTimeout(() => {
  console.log("Done");
}, 1000);
```

`setTimeout` is handled by the browser (or Node) API, not the JS engine itself.

### 3. Callback Queue (Macrotask Queue)

After async tasks finish, their callbacks wait here. Examples: `setTimeout`, `setInterval`, DOM events.

### 4. Microtask Queue (Higher Priority)

Used for Promises, `queueMicrotask`, and `MutationObserver`. Microtasks run **before** callback queue tasks.

### 5. Event Loop

The event loop constantly checks whether the call stack is empty. If it is:

1. Execute all pending microtasks first.
2. Then execute one task from the callback queue.

## Example: Basic Async

```javascript
console.log("1");

setTimeout(() => {
  console.log("2");
}, 0);

console.log("3");
```

Output:

```text
1
3
2
```

Step by step:

1. `console.log("1")` runs synchronously → prints `1`.
2. `setTimeout(...)` hands its callback to the Web API; the browser starts the timer and the callback is moved to the callback queue once it fires.
3. `console.log("3")` runs synchronously → prints `3`.
4. The stack is now empty, so the event loop pushes the timer callback from the callback queue onto the stack → prints `2`.

```text
Call Stack       Web APIs         Callback Queue

console.log(1)
setTimeout() --> timer
console.log(3)
Stack Empty
callback -----------> queue
Event Loop pushes callback
```

## Example: Promises vs setTimeout

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

Because microtasks (Promises) have higher priority than the callback queue (`setTimeout`):

1. Synchronous code first: `1`, `4`.
2. Then all microtasks: `3`.
3. Then the callback queue: `2`.

## The Core Rule

```text
1. Run sync code
2. Run ALL microtasks
3. Run ONE macrotask
4. Repeat
```

Microtask examples: `Promise.resolve().then(...)`, `queueMicrotask(...)`.

Macrotask examples: `setTimeout(...)`, `setInterval(...)`, DOM events.

## Advanced Example

```javascript
console.log("start");

setTimeout(() => {
  console.log("timeout");
}, 0);

Promise.resolve().then(() => {
  console.log("promise");
});

queueMicrotask(() => {
  console.log("microtask");
});

console.log("end");
```

Output:

```text
start
end
promise
microtask
timeout
```

## Node.js Event Loop (Advanced)

Node.js has its own phases: timers, pending callbacks, poll, check, and close callbacks. It also adds `process.nextTick()` and `setImmediate()`. This is important for backend engineers to understand — see the [microtask vs. macrotask](microtask-vs-macrotask.md) breakdown of Node's priority ordering.

## Common Questions

**Is JavaScript multithreaded?**
> JavaScript execution is single-threaded, but browsers and Node.js provide asynchronous APIs handled outside the main thread.

**Why isn't `setTimeout(fn, 0)` immediate?**
Because it waits until the call stack is empty, and waits for all pending microtasks too.

**Promise vs. `setTimeout` — which runs first?**
The Promise runs first, because the microtask queue has higher priority than the callback (macrotask) queue.

**What causes blocking?**
Heavy synchronous operations, such as `while (true) {}`, block the event loop completely.

## Real-World Importance

Understanding the event loop is critical for:

- React rendering behavior
- Node.js performance tuning
- [WebSockets](../../networking/websockets.md) and streaming
- API scalability
- Debugging async bugs
- General performance optimization

## Senior-Level Definition

> The event loop is a scheduling mechanism that coordinates execution between the call stack, microtask queue, and task queue, enabling asynchronous non-blocking behavior in JavaScript.

## Related

- [Asynchronous / Non-Blocking Execution](../fundamentals/asynchronous-non-blocking-execution.md) — the general, language-agnostic concept this file specializes for JavaScript's own scheduling mechanics
- [Microtasks vs Macrotasks](microtask-vs-macrotask.md)
- [Promise Chaining](promise-chaining.md)
- [Closures](closures.md)
- [asyncio (Python's async equivalent of this JS concept)](../../backend/architecture/asyncio.md)
