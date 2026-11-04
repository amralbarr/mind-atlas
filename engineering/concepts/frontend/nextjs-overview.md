# Next.js Overview

Next.js is built on top of [React](https://react.dev/) — the [Components](components.md), [Props vs State](props-vs-state.md), and [Hooks](hooks.md) fundamentals all still apply inside a Next.js app. This page covers what Next.js adds on top: what it is, why teams reach for it, its key features, and how it talks to a backend.

## What Is Next.js?

Next.js is a React framework for building full-stack web applications. On top of plain React it adds:

- Server-Side Rendering (SSR)
- Static Site Generation (SSG)
- API routes
- File-based routing
- Image optimization
- [Middleware](../backend/middleware.md)
- SEO optimization
- App Router and Server Components

## Why Use Next.js? (React vs Next.js)

| React                  | Next.js                    |
| ------------------------ | ------------------------------ |
| UI library                 | Full framework                     |
| Client-side by default       | Supports SSR, SSG, and CSR             |
| Manual routing                  | File-based routing                        |
| No backend                         | API routes included                          |
| SEO is harder                         | Better SEO out of the box                      |
| Needs external setup                    | Built-in optimization                             |

Use SSR when data changes frequently and SEO matters; use SSG for mostly-static content like blogs and documentation.

## Key Features

### Rendering Strategies

See [Rendering Strategies](rendering-strategies.md) for the framework-agnostic concepts (SSR/SSG/ISR/CSR, hydration, when to use each) — below is how Next.js specifically implements each one.

**Server-Side Rendering (SSR)** — the page is rendered on the server for every request. Better SEO, always-fresh data, faster first contentful paint, but slower per-request than a static page.

```tsx
export async function getServerSideProps() {
  const res = await fetch('https://api.example.com/posts');
  const data = await res.json();

  return {
    props: { data }
  };
}
```

**Static Site Generation (SSG)** — pages are generated once, at build time. Very fast, [CDN](../networking/cdn.md)-friendly, but data is static until the next build.

```tsx
export async function getStaticProps() {
  const res = await fetch('https://api.example.com/posts');
  const data = await res.json();

  return {
    props: { data }
  };
}
```

| SSR                          | SSG                     |
| ------------------------------- | --------------------------- |
| Rendered on every request           | Rendered during build           |
| Dynamic data                           | Static data                        |
| Slower                                    | Faster                                |
| Good for dashboards                          | Good for blogs                           |

**Incremental Static Regeneration (ISR)** — lets statically generated pages update after deployment, without a full rebuild:

```tsx
export async function getStaticProps() {
  return {
    props: {},
    revalidate: 60
  };
}
```

**Client-Side Rendering (CSR)** — the browser renders the page using JavaScript, typically fetching data from an effect:

```tsx
useEffect(() => {
  fetchData();
}, []);
```

**Hydration** is the process where React attaches event listeners to the static HTML markup that was rendered on the server, turning it into an interactive page.

### Routing

Files inside the `app` (or legacy `pages`) directory automatically become routes:

```bash
app/about/page.tsx   →   /about
```

Dynamic routes use bracket segments:

```bash
app/product/[id]/page.tsx
```

```tsx
export default function Page({ params }) {
  return <h1>{params.id}</h1>;
}
```

The **App Router** is the modern routing system introduced in Next.js 13+, and it adds layouts, Server Components, streaming, nested routing, and per-route loading UI.

| Pages Router            | App Router                        |
| -------------------------- | -------------------------------------- |
| Old system                   | New system                                 |
| Uses the `pages` folder         | Uses the `app` folder                          |
| Limited layouts                    | Nested layouts                                    |
| No Server Components                  | Supports Server Components                           |

### Server Components vs Client Components

A **Server Component** runs only on the server: smaller client bundle size, can fetch data securely, generally better performance.

```tsx
async function Products() {
  const products = await getProducts();

  return <div>{products.length}</div>;
}
```

A **Client Component** runs in the browser and is required whenever you need `useState`, `useEffect`, browser APIs, or event handlers — mark it with the `'use client'` directive:

```tsx
'use client'

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

Best practice is to use Server Components by default and only opt into Client Components where interactivity is actually needed.

### Middleware

[Middleware](../backend/middleware.md) runs before a request completes, and is commonly used for [authentication](../security/auth/authentication.md), redirects, logging, and localization.

```tsx
import { NextResponse } from 'next/server';

export function middleware(request) {
  return NextResponse.next();
}
```

### Image Optimization

The built-in `Image` component handles resizing, lazy loading, and format optimization automatically:

```tsx
import Image from 'next/image';

<Image
  src="/test.png"
  width={300}
  height={300}
  alt="test"
/>
```

### SEO

Next.js improves SEO via SSR, metadata support, fast loading, optimized images, and better crawlability/indexing compared to a pure client-rendered SPA — see [Technical SEO](technical-seo.md) for the underlying mechanics (crawlability, structured data, Core Web Vitals) independent of any one framework.

## How Next.js Talks to a Backend

Next.js can act as its own backend and/or call an external one:

### API Routes / Route Handlers

Next.js can expose backend endpoints directly inside the app, effectively acting as a lightweight [REST](../backend/api/rest.md) API layer:

```tsx
export async function GET() {
  return Response.json({
    message: 'Hello'
  });
}
```

### Fetching From an External Backend

**On the server** (Server Components, `getServerSideProps`/`getStaticProps`, or Route Handlers) — data is fetched directly, keeping API keys and business logic off the client:

```tsx
const data = await fetch(url);
```

**On the client** — fetched from an effect, typically for data that depends on user interaction after the initial page load:

```tsx
useEffect(() => {
  fetchData();
}, []);
```

Whether the backend it talks to exposes [REST](../backend/api/rest.md) or [GraphQL](../backend/api/graphql.md), the same split applies: prefer fetching on the server when possible, and fall back to client-side fetching for interactive, user-driven data needs.

## Ecosystem and Practical Notes

### Common Packages

| Package                          | Usage                    |
| ------------------------------------ | ---------------------------- |
| axios                                   | [HTTP](../networking/http.md) requests                    |
| zustand                                    | State management                    |
| react-query / TanStack Query                  | Server state                           |
| next-auth                                        | [Authentication](../security/auth/authentication.md)                            |
| [zod](../programming/typescript/zod.md)                                                 | Validation                                    |
| prisma                                                 | [ORM](../backend/data/orm.md)                                                |

### Typical Folder Structure

```bash
app/
components/
lib/
hooks/
services/
public/
styles/
```

### Common Commands

```bash
npx create-next-app@latest   # scaffold a new app
npm run dev                  # local development
npm run build                # production build
npm run start                # run the production build
```

**Useful resource:** [Next-js-Boilerplate](https://github.com/ixartz/Next-js-Boilerplate) — a community starter template with TypeScript, Tailwind, testing, and CI preconfigured.

### Advanced Topics

Beyond the fundamentals above, production Next.js apps commonly touch: Server Actions, Edge Functions, streaming AI responses, [WebSockets](../networking/websockets.md), [caching strategies](../backend/architecture/caching-strategies.md), [Docker](../containers/docker.md) deployment, [CI/CD](../devops/ci-cd.md) pipelines, and integrating Redis or [PostgreSQL](../databases/relational/postgresql.md).

### Best Practices

- Default to Server Components; opt into Client Components only where needed.
- Keep secrets and business logic on the server.
- Use `next/image` for optimized images.
- Use TypeScript.
- Avoid unnecessary re-renders (see [Components](components.md)).
- Split components sensibly rather than building monoliths.
- Use `loading.tsx` and `error.tsx` for route-level loading and error UI.

## Quick Reference

- **Why use Next.js over plain React?** Built-in SSR/SSG/ISR, file-based routing, API routes, and better SEO without extra tooling.
- **What are Server Components?** Components that render only on the server, reducing client bundle size and allowing secure data fetching.
- **SSR vs CSR?** SSR renders on the server per request (better SEO, fresh data); CSR renders in the browser after JS loads (simpler, but worse first paint/SEO).
- **What is hydration?** React attaching event listeners/interactivity to server-rendered HTML on the client.

## Related

- [Components](components.md)
- [Props vs State](props-vs-state.md)
- [React Hooks](hooks.md)
- [REST](../backend/api/rest.md)
- [GraphQL](../backend/api/graphql.md)
- [Rendering Strategies](rendering-strategies.md)
- [Technical SEO](technical-seo.md)
