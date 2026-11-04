# Memory Leaks in JavaScript

A memory leak happens when memory that is no longer needed is **not** released by the application. Over time, memory usage increases, the application slows down, and the browser tab or Node.js server can eventually crash.

## First, Understand Garbage Collection (GC)

JavaScript has automatic memory management: the garbage collector removes objects that are no longer reachable.

```javascript
let user = { name: "Amr" };

user = null;
```

Once `user` is set to `null`, the object becomes unreachable and GC removes it later.

A memory leak happens when something **still references** an object accidentally, so GC thinks the object is still needed and does not remove it.

## Common Causes of Memory Leaks

### 1. Global Variables

```javascript
users = [];
```

Without `let`/`const`, this becomes a global variable accidentally. Global objects stay alive for the entire app lifetime.

### 2. Forgotten Timers

```javascript
setInterval(() => {
  console.log("running");
}, 1000);
```

If a timer is never cleared, it keeps its references alive forever.

**Solution:**

```javascript
const interval = setInterval(...);

clearInterval(interval);
```

### 3. Event Listeners Not Removed

Very common in React/frontend code.

**Bad:**

```javascript
window.addEventListener("resize", handler);
```

If the component is removed but the listener isn't, it keeps references alive.

**Solution:**

```javascript
window.removeEventListener("resize", handler);
```

**React example:**

```javascript
useEffect(() => {
  window.addEventListener("resize", handler);

  return () => {
    window.removeEventListener("resize", handler);
  };
}, []);
```

### 4. Closures Holding References

[Closures](closures.md) can accidentally keep large objects alive.

```javascript
function createHandler() {
  const largeData = new Array(1000000);

  return function () {
    console.log(largeData.length);
  };
}
```

The returned function still references `largeData`, so that memory is never released. See [closures](closures.md) for more on how this works.

### 5. Detached DOM Nodes

A frontend-specific issue: a DOM element can be removed visually while JS still references it, so it can't be garbage collected.

```javascript
const element = document.getElementById("app");

element.remove();
```

If a variable still references `element`, GC cannot clean it up.

### 6. Caches Growing Forever

```javascript
const cache = {};
```

Adding data to this forever means memory grows infinitely. Use an LRU cache, expiration, or another cleanup strategy instead.

### 7. Unresolved Promises

Long-running async references — sockets, streams, subscriptions — can remain alive if never cleaned up.

## Node.js Memory Leaks

A very important backend topic. Common causes:

- Event emitters
- Unclosed DB connections
- Huge in-memory caches
- Infinite arrays/maps
- WebSocket subscriptions
- Timers

```javascript
connections.push(socket);
```

If entries are never removed, memory grows forever.

## Memory Leak Symptoms

**Browser:** tab becomes slow, freezing, high RAM usage.

**Node.js:** increasing heap memory, high GC activity, process crashes, out-of-memory (OOM) errors.

## Memory Leak vs. High Memory Usage

An important distinction:

- **High memory usage** — the app legitimately uses a lot of memory, but it stabilizes.
- **Memory leak** — memory continuously grows and is never released.

```text
Healthy app: memory up/down normally
Memory leak: memory keeps climbing upward until crash
```

## Detecting Memory Leaks

**Browser tools:** Chrome DevTools — Memory tab, heap snapshots, allocation timeline. See the [Chrome DevTools memory docs](https://developer.chrome.com/docs/devtools/memory-problems).

**Node.js tools:** `heapdump`, `clinic.js`, Chrome inspector, Node heap snapshots.

## Garbage Collection Internals

GC mainly uses a **mark-and-sweep** algorithm:

1. Mark all reachable objects.
2. Remove unreachable objects.

A memory leak happens because objects remain reachable accidentally.

## WeakMap / WeakSet

An advanced topic: these allow references that do **not** prevent [garbage collection](../fundamentals/garbage-collection.md), which makes them useful for caches.

```javascript
const cache = new WeakMap();
```

## React Memory Leak Example

**Bad:**

```javascript
useEffect(() => {
  setInterval(() => {
    fetchData();
  }, 1000);
}, []);
```

The interval is never cleaned up.

**Good:**

```javascript
useEffect(() => {
  const timer = setInterval(fetchData, 1000);

  return () => clearInterval(timer);
}, []);
```

## EventEmitter Leak (Node.js)

A very common backend issue.

**Bad:**

```javascript
emitter.on("data", handler);
```

If many listeners are added and never removed, Node emits a warning:

```text
MaxListenersExceededWarning
```

## Common Questions

**What is a memory leak?**
> A memory leak occurs when memory that is no longer needed remains referenced and cannot be garbage collected.

**Common JS memory leak causes?**
Global variables, timers, event listeners, [closures](closures.md), detached DOM nodes, caches.

**Why can [closures](closures.md) cause leaks?**
Because [closures](closures.md) retain references to outer scope variables.

**How do you prevent memory leaks in React?**
Clean up listeners, intervals, and subscriptions inside the `useEffect` cleanup function.

**Difference between a leak and high memory usage?**
Leaks continuously grow over time and never stabilize.

**How does the garbage collector work?**
It tracks reachable objects and frees unreachable memory.

## Senior-Level Understanding

Memory leaks are reference lifecycle problems, not simply "large memory." Senior engineers think about ownership, cleanup, subscription lifecycle, cache eviction, and resource management.

> A memory leak in JavaScript occurs when object references unintentionally persist beyond their useful lifecycle, preventing [garbage collection](../fundamentals/garbage-collection.md) and causing progressive heap growth, degraded performance, and eventual resource exhaustion.

## Easy Way to Remember

```text
Memory leak =
memory that should die
but stays alive
```

## Related

- [Debounce vs Throttle](debounce-vs-throttle.md)
- [Closures](closures.md)
- [Mutation](../fundamentals/mutation.md)
- [The Event Loop](event-loop.md)
