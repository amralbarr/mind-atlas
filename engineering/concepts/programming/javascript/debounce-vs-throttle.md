# Debounce vs Throttle

A widely used frontend/backend technique, used heavily in search inputs, scrolling, resize events, API optimization, and performance engineering.

## The Problem

Some browser events fire very frequently — typing, scrolling, mouse movement, resize — potentially hundreds of times per second. Without control, this causes too many API calls, lag, and wasted CPU.

## Debounce

**Definition:** wait until events stop happening before executing the function.

### Real-Life Example

A search input. As the user types `a`, `am`, `amr`, you don't want three API requests. Instead, wait (say) 500ms after typing stops, then send one request.

```text
Typing:  a   m   r
          |   |   |
Timer:   reset reset reset

(after stop typing)
→ execute once
```

### Debounce Implementation

```javascript
function debounce(fn, delay) {
  let timer;

  return function (...args) {
    clearTimeout(timer);

    timer = setTimeout(() => {
      fn(...args);
    }, delay);
  };
}
```

**Usage:**

```javascript
const search = debounce(() => {
  console.log("API CALL");
}, 500);
```

If the user types continuously, the timer keeps resetting, and the function only executes after inactivity.

### Debounce Use Cases

- Search bars
- Auto-save
- Window resize
- Input validation
- Expensive calculations

## Throttle

**Definition:** limit function execution to at most once every X milliseconds.

### Real-Life Example

A scroll event can fire hundreds of times per second. Throttling allows only one execution every 200ms, for example.

```text
Events: |||||||||||||||||||

Throttle(1 sec):

Execute → wait → execute → wait
```

### Throttle Implementation

```javascript
function throttle(fn, delay) {
  let waiting = false;

  return function (...args) {
    if (waiting) return;

    fn(...args);

    waiting = true;

    setTimeout(() => {
      waiting = false;
    }, delay);
  };
}
```

**Usage:**

```javascript
const onScroll = throttle(() => {
  console.log("scroll");
}, 200);
```

## Debounce vs Throttle

| Debounce | Throttle |
|---|---|
| Wait until stop | Execute periodically |
| One final execution | Continuous limited execution |
| Good for typing | Good for scrolling |

```text
Debounce:
typing typing typing STOP
                    ↓
               execute once

Throttle:
scroll scroll scroll scroll
↓ every 200ms
execute
```

### Search Example (Debounce)

**Bad:** every keystroke triggers an API request.
**Good:** wait until the user finishes typing.

### Scroll Example (Throttle)

**Bad:** scroll event fires 500 times/sec, and every one triggers work.
**Good:** execute at most every 100ms.

## Advanced Debounce Variants

- **Leading edge** — execute immediately on the first call.
- **Trailing edge** — execute after inactivity (the default behavior above).

## Lodash Utilities

Lodash's implementations are the most commonly used in practice: [Lodash debounce docs](https://lodash.com/docs/#debounce), [Lodash throttle docs](https://lodash.com/docs/#throttle).

```javascript
import debounce from 'lodash/debounce';
```

### In React

Very common for search, resize, and filtering:

```javascript
const debouncedSearch = useMemo(
  () => debounce(searchFn, 500),
  []
);
```

## Backend Use Cases

Throttling is commonly used for [rate limiting](../../backend/architecture/rate-limiting.md) and API protection, e.g. capping requests at 10/sec. Debouncing is used less often on the backend, but can apply to batching or delayed processing.

## Common Questions

**What is debounce?**
> Debounce delays function execution until a period of inactivity occurs.

**What is throttle?**
> Throttle limits how often a function can execute within a time interval.

**Difference between debounce and throttle?**

| Debounce | Throttle |
|---|---|
| Waits for inactivity | Executes periodically |

**When would you use debounce?**
Search input, autosave, validation.

**When would you use throttle?**
Scroll events, resize events, mouse tracking, [rate limiting](../../backend/architecture/rate-limiting.md).

**Why do these techniques matter?**
They improve performance, responsiveness, and API efficiency.

## Senior-Level Understanding

These techniques control event frequency and reduce render storms, API flooding, CPU spikes, and unnecessary computation.

> Debouncing and throttling are event rate-control techniques used to optimize high-frequency event handling. Debounce consolidates bursts into a single execution after inactivity, while throttle guarantees controlled periodic execution over time.

## Easy Way to Remember

```text
Debounce = wait until calm
Throttle = limit speed
```

## Related

- [Memory Leaks in JavaScript](memory-leaks-js.md)
- [The Event Loop](event-loop.md)
- [Closures](closures.md)
