# Garbage Collection

Garbage collection (GC) is an automatic memory management process. Instead of a developer manually freeing memory, the runtime (e.g., the JavaScript engine, the JVM, Python's interpreter) periodically scans for objects that are no longer reachable from any active reference and removes them, freeing the memory they occupied.

## Why It Matters

Without garbage collection, a program has to explicitly allocate and free memory for every object. Forgetting to free memory causes it to accumulate over the life of the process — this is a **memory leak**. Garbage collection removes most of that manual burden, but it doesn't make leaks impossible: if something still holds a reference to an object (a forgotten timer, an unremoved event listener, a growing cache), the collector considers it "in use" and keeps it alive anyway.

## How It Works (Mark-and-Sweep)

Most modern garbage collectors, including the one in JavaScript engines like V8, use a **mark-and-sweep** algorithm:

1. **Mark** — starting from a set of root references (global scope, active call stack), walk every reachable object and mark it as "in use."
2. **Sweep** — anything left unmarked is unreachable, so it's safe to free.

```text
roots → reachable objects (kept)
unreachable objects → freed
```

## Example

```javascript
let user = { name: "Amr" };

user = null;
```

Once `user` is reassigned to `null`, the original object has no remaining references. It becomes unreachable, and the garbage collector will eventually reclaim its memory.

## Definition

> Garbage collection is an automatic process that manages memory by removing objects that are no longer in use, helping prevent memory leaks and reducing the need for manual memory management.

## Related

- [Memory Leaks in JavaScript](../javascript/memory-leaks-js.md)
- [Closures](../javascript/closures.md)
