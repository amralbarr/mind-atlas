# Components

Components are the most important concept in [React](https://react.dev/). Everything in a React app is built by composing components.

## What Is a Component?

A component is a reusable piece of UI with its own logic and structure. Think of components like LEGO blocks: you combine small blocks to build large applications.

For example, a typical page breaks down like this:

```text
Page
 ├── Navbar
 ├── Sidebar
 ├── Product Card
 └── Footer
```

Each part is its own component.

### Basic Example

```jsx
function Welcome() {
  return <h1>Hello Amr</h1>;
}
```

Usage:

```jsx
<Welcome />
```

Internally, React calls `Welcome()` and renders the returned JSX:

```html
<h1>Hello Amr</h1>
```

### Naming Rule

Components must start with a capital letter, or React treats them as a plain HTML tag.

```jsx
// Correct
function Navbar() {}

// Wrong — lowercase is treated as an HTML tag
function navbar() {}
```

## Types of Components

### Functional Components (Modern)

The most common style today.

```jsx
function Button() {
  return <button>Click</button>;
}

// Arrow function version
const Button = () => {
  return <button>Click</button>;
};
```

### Class Components (Legacy)

The older React style, built around lifecycle methods instead of [hooks](hooks.md). Rare in new code but still appears in legacy codebases.

```jsx
class Button extends React.Component {
  render() {
    return <button>Click</button>;
  }
}
```

### Functional vs Class Components

| Functional | Class             |
| ---------- | ----------------- |
| Modern     | Legacy             |
| [Hooks](hooks.md)      | Lifecycle methods  |
| Simpler    | More verbose       |
| Preferred  | Rare today         |

## Reusable Components

Any component can be reused as many times as needed:

```jsx
function UserCard() {
  return <div>User</div>;
}
```

```jsx
<UserCard />
<UserCard />
<UserCard />
```

## Components with Props

Props are data passed into a component from its parent.

```jsx
function Welcome(props) {
  return <h1>Hello {props.name}</h1>;
}
```

```jsx
<Welcome name="Amr" />
// → Hello Amr
```

Cleaner with destructuring:

```jsx
function Welcome({ name }) {
  return <h1>Hello {name}</h1>;
}
```

Props are **read-only** — a component must never mutate its own props:

```jsx
// Wrong
props.name = "Ali";
```

See [Props vs State](props-vs-state.md) for the full comparison.

## Component State

State is internal data owned and managed by the component itself, and it can change over time.

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

| Props              | State                     |
| ------------------ | ------------------------- |
| External data       | Internal data              |
| Read-only            | Mutable                     |
| Passed from parent   | Managed inside component   |

## Parent and Child Components

```jsx
// Parent
function App() {
  return <User name="Amr" />;
}

// Child
function User({ name }) {
  return <h1>{name}</h1>;
}
```

## Component Composition

React apps are built by nesting components inside one another:

```jsx
function App() {
  return (
    <>
      <Navbar />
      <Sidebar />
      <Dashboard />
    </>
  );
}
```

### Fragments

Fragments (`<>...</>`) let you group elements without adding an extra wrapper `<div>`:

```jsx
<>
  <h1>Hello</h1>
  <p>World</p>
</>
```

This is equivalent to `<React.Fragment>...</React.Fragment>`.

## Conditional Rendering

```jsx
function App({ loggedIn }) {
  return (
    <>
      {loggedIn ? <Dashboard /> : <Login />}
    </>
  );
}
```

## Rendering Lists

```jsx
const users = ['Amr', 'Ali'];

return (
  <>
    {users.map(user => (
      <p key={user}>{user}</p>
    ))}
  </>
);
```

Always provide a stable `key` when rendering lists — keys help React efficiently identify which elements changed during reconciliation.

## Event Handling

```jsx
function handleClick() {
  console.log('Clicked');
}
```

```jsx
<button onClick={handleClick}>Click</button>
```

## Controlled Components

Common in forms — React (state) controls the input's value rather than the DOM:

```jsx
const [name, setName] = useState('');

<input
  value={name}
  onChange={(e) => setName(e.target.value)}
/>
```

## Component Lifecycle

Functional components model their lifecycle with [hooks](hooks.md) (see [React Hooks](hooks.md)):

- **Mount** — the component appears.
- **Update** — state or props change.
- **Unmount** — the component is removed.

```jsx
useEffect(() => {
  console.log('Mounted');

  return () => {
    console.log('Unmounted');
  };
}, []);
```

## Re-renders

React re-renders a component when:

- its state changes
- its props change
- its parent re-renders

> Re-rendering is the process where React re-executes a component function to update the virtual DOM after state or props change.

### Pure Components and Avoiding Unnecessary Re-renders

Tools for avoiding unnecessary re-renders: `React.memo`, `useMemo`, `useCallback`. This is a common performance topic — see also [Debounce vs Throttle](../programming/javascript/debounce-vs-throttle.md) for a related frontend performance technique used to limit how often expensive handlers (scroll, resize, input) run.

## JSX

Components return JSX:

```jsx
return <h1>Hello</h1>;
```

JSX is syntax that compiles down to:

```javascript
React.createElement(...)
```

## Quick Reference

- **What is a component?** A reusable, isolated piece of UI logic in React that returns JSX and can manage state and props.
- **Functional vs class components?** Functional components are simpler, support [hooks](hooks.md), and are the preferred modern approach.
- **Why do keys matter in lists?** Keys help React efficiently identify changed elements during reconciliation.
- **What causes re-renders?** State updates, prop changes, or a parent re-rendering.

> React components are reusable UI units that encapsulate rendering logic, state, and behavior. They enable modular architecture, composability, and efficient UI updates through React's virtual DOM reconciliation process.

## Related

- [Props vs State](props-vs-state.md)
- [React Hooks](hooks.md)
- [Next.js Overview](nextjs-overview.md)
- [Debounce vs Throttle](../programming/javascript/debounce-vs-throttle.md)
