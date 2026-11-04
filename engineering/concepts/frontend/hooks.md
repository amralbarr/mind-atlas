# React Hooks

Hooks are one of the most important topics in modern [React](https://react.dev/reference/react) development. They let functional components use state, lifecycle features, side effects, refs, context, and memoization — all without writing class components.

## What Are Hooks?

Hooks are special React functions that let functional components use React features, e.g. `useState()`, `useEffect()`, `useRef()`, `useContext()`.

## Why Hooks Were Created

Before hooks, only class components had state and lifecycle methods, code reuse between components was difficult, and lifecycle logic tended to become messy (related logic scattered across different lifecycle methods). Hooks solve this by letting you colocate related logic and reuse it via custom hooks.

## Most Important Hooks

| Hook            | Purpose                     |
| --------------- | ---------------------------- |
| `useState`        | component state                 |
| `useEffect`        | side effects                       |
| `useRef`             | DOM/reference storage without re-render |
| `useContext`           | shared global data                       |
| `useMemo`                | memoized values                            |
| `useCallback`              | memoized functions                            |
| `useReducer`                 | complex state logic                             |
| `useLayoutEffect`               | effects that must run before paint |

## useState

Used for component state.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

`useState(0)` creates a state variable (`count`) and an update function (`setCount`). Calling `setCount` updates state and triggers a re-render. See [Props vs State](props-vs-state.md) for more on how state behaves.

## useEffect

Used for side effects: API calls, timers, subscriptions, event listeners.

```jsx
useEffect(() => {
  console.log('Mounted');
}, []);
```

### Dependency Array

The dependency array controls when the effect runs — worth understanding precisely:

| Form                                | Behavior                        |
| -------------------------------------- | ---------------------------------- |
| `useEffect(() => {})`                     | runs after every render               |
| `useEffect(() => {}, [])`                    | runs once, after the initial mount        |
| `useEffect(() => {}, [count])`                  | runs whenever `count` changes                 |

### Cleanup Function

```jsx
useEffect(() => {
  const timer = setInterval(() => {}, 1000);

  return () => {
    clearInterval(timer);
  };
}, []);
```

The cleanup function runs on unmount, and again before the effect re-runs.

## useRef

Stores DOM references or mutable values without causing a re-render when they change.

```jsx
const inputRef = useRef();

<input ref={inputRef} />
```

```jsx
inputRef.current.focus();
```

| Hook         | Causes Re-render? |
| ------------ | -------------------- |
| `useState`     | Yes                     |
| `useRef`         | No                        |

## useContext

Used to share global state (theme, auth, language, user data) without prop drilling.

```jsx
const ThemeContext = createContext();
```

```jsx
const theme = useContext(ThemeContext);
```

## useMemo

Memoizes an expensive calculation's *value*, avoiding recomputation on every render.

```jsx
const expensiveValue = useMemo(() => {
  return heavyCalculation(data);
}, [data]);
```

## useCallback

Memoizes a *function*, which helps prevent unnecessary re-renders in child components that receive it as a prop.

```jsx
const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);
```

| Hook              | Memoizes    |
| ------------------- | -------------- |
| `useMemo`               | a value            |
| `useCallback`             | a function            |

## useReducer

An alternative to `useState` for complex state logic or multiple related state transitions — similar to the Redux reducer pattern.

```jsx
const [state, dispatch] = useReducer(reducer, initialState);
```

## Additional Hooks

Less commonly reached for, but worth knowing:

- **`useLayoutEffect`** — like `useEffect`, but fires synchronously before the browser paints:

  ```jsx
  useLayoutEffect(() => {
    console.log('Before paint');
  }, []);
  ```

- **`useImperativeHandle`** — customizes the instance value exposed by a ref, typically paired with `forwardRef`:

  ```jsx
  useImperativeHandle(ref, () => ({
    focus
  }));
  ```

- **`useTransition`** — marks state updates as non-blocking/low-priority, keeping the UI responsive during large updates:

  ```jsx
  const [isPending, startTransition] = useTransition();
  ```

- **`useDeferredValue`** — defers re-rendering for a fast-changing value (e.g. search input) until more urgent updates finish:

  ```jsx
  const deferredQuery = useDeferredValue(query);
  ```

- **`useId`** — generates a stable unique ID, useful for accessibility attributes:

  ```jsx
  const id = useId();
  ```

## Custom Hooks

You can extract reusable stateful logic into your own hooks, built out of the built-in ones:

```jsx
function useCounter() {
  const [count, setCount] = useState(0);
  return { count, setCount };
}
```

```jsx
const { count, setCount } = useCounter();
```

A slightly more realistic example — a data-fetching hook:

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData);
  }, [url]);

  return data;
}
```

Custom hooks enable reusable logic, cleaner components, and better [abstraction](../programming/fundamentals/abstraction.md) — because a hook is just a regular JavaScript function that closes over `useState`/`useEffect` calls, the same rules that govern [closures](../programming/javascript/closures.md) apply to what a hook "remembers" between renders (e.g. a stale value captured by a callback that wasn't included in a dependency array).

## Hooks Rules

1. **Only call hooks at the top level** — never inside conditionals, loops, or nested functions.

   ```jsx
   // Wrong
   if (x) {
     useState();
   }
   ```

2. **Only call hooks inside React functions** — components or custom hooks.

These rules exist because React relies on a consistent hook call order across renders to correctly associate each hook call with its internal state.

## Priority Order for Study

```text
1. useState
2. useEffect
3. useRef
4. useContext
5. useMemo
6. useCallback
7. useReducer
```

## Quick Reference

- **What are hooks?** Special React functions that allow functional components to use state, lifecycle features, refs, and other React capabilities.
- **Why were hooks introduced?** To replace class-component complexity and improve logic reuse.
- **`useState` vs `useRef`?** `useState` triggers a re-render on update; `useRef` does not.
- **What is `useEffect` used for?** Side effects — API calls, subscriptions, timers, DOM interactions.
- **`useMemo` vs `useCallback`?** `useMemo` returns a memoized value; `useCallback` returns a memoized function.
- **Why must hooks be called at the top level?** Because React relies on hook call order for state tracking.

> Hooks are React functions that enable functional components to manage state, side effects, refs, memoization, and shared context while promoting reusable logic and cleaner component architecture.

## Related

- [Components](components.md)
- [Props vs State](props-vs-state.md)
- [Next.js Overview](nextjs-overview.md)
- [Closures](../programming/javascript/closures.md)
- [Mutation](../programming/fundamentals/mutation.md)
