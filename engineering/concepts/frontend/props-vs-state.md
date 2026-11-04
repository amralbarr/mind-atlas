# Props vs State

Understanding props and state — and the difference between them — is fundamental to React architecture.

## Quick Summary

| Feature            | Props              | State                |
| ------------------ | ------------------- | ---------------------- |
| Owned by             | Parent component     | Current component      |
| Mutable?             | No                     | Yes                       |
| Purpose              | Pass data              | Store changing data       |
| Controlled by        | Parent                 | Component itself          |
| Causes re-render?    | Yes                    | Yes                         |

## Props

Props are data passed from a parent component to a child component — conceptually similar to function arguments.

```jsx
// Parent
function App() {
  return <User name="Amr" />;
}

// Child
function User(props) {
  return <h1>{props.name}</h1>;
}
// → Amr
```

Cleaner with destructuring:

```jsx
function User({ name }) {
  return <h1>{name}</h1>;
}
```

### Props Are Read-Only

```jsx
// Wrong — never mutate props
props.name = "Ali";
```

The parent owns the data; the child only receives it.

### Props Can Pass Functions

Passing a callback down as a prop lets a child communicate back up to its parent:

```jsx
// Parent
function App() {
  const handleDelete = () => {
    console.log('Deleted');
  };

  return <User onDelete={handleDelete} />;
}

// Child
function User({ onDelete }) {
  return (
    <button onClick={onDelete}>
      Delete
    </button>
  );
}
```

### One-Way Data Flow

React data flows one way: parent → child. Props move downward only; a child cannot pass props back up directly (it can only invoke a callback prop, as above).

## State

State is internal data managed by the component itself, and it changes over time. It's created with `useState`:

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

```javascript
const [count, setCount] = useState(0);
```

This creates a state variable (`count`) and an updater function (`setCount`). `useState(0)` sets the initial value of `count` to `0`.

### State Updates Cause Re-renders

```text
State changes
     ↓
React re-renders the component
     ↓
UI updates
```

Without state, the UI could never react to change — React's rendering model is built around reactive state updates.

### State Is Asynchronous

State updates don't apply synchronously, which trips up a lot of developers:

```jsx
setCount(count + 1);
console.log(count); // may still log the OLD value
```

This happens because React batches updates. The safe pattern when the next value depends on the previous one is a **functional update**:

```jsx
setCount(prev => prev + 1);
```

### Common Mistake

```jsx
// Wrong — mutating state directly does not trigger a re-render
count++;

// Correct
setCount(count + 1);
```

State should always be treated as immutable and replaced via its setter, never mutated in place — see [Mutation](../programming/fundamentals/mutation.md) for why mutating shared data directly is risky in JavaScript generally.

## Ownership

- **Props**: the parent controls props.
- **State**: the component controls its own state.

## Combining Props and State

```jsx
// Parent
function App() {
  return <Counter start={5} />;
}

// Child
function Counter({ start }) {
  const [count, setCount] = useState(start);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

Here, `start` is a prop and `count` is state.

### Common Examples

| Props                     | State                    |
| -------------------------- | -------------------------- |
| user data                    | counters                     |
| labels                        | form inputs                    |
| configuration                  | loading flags                    |
| callbacks                        | modal visibility                    |
| component customization            | fetched API data / auth state          |

## Controlled Components

Forms typically combine props and state: state controls the input's current value.

```jsx
const [name, setName] = useState('');

<input
  value={name}
  onChange={(e) => setName(e.target.value)}
/>
```

## Quick Reference

- **Difference between props and state?** Props are external, immutable data passed from parent components; state is internal, mutable data managed by the component itself.
- **Do props cause re-renders?** Yes — when props change, the component re-renders.
- **Can a child modify its props?** No, props are read-only.
- **Why use state?** To store dynamic UI data that changes over time.
- **What causes a component to re-render?** State updates, prop changes, or a parent re-render.

> Props provide immutable, external data flow between components, while state manages internal, mutable UI data. Together they enable React's reactive rendering model and unidirectional data architecture.

## Related

- [Components](components.md)
- [React Hooks](hooks.md)
- [Next.js Overview](nextjs-overview.md)
- [Mutation](../programming/fundamentals/mutation.md)
