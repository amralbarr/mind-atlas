# Rendering Strategies (CSR, SSR, SSG, ISR)

The **rendering strategy** is *when and where* HTML for a page gets generated — at build time, on each request, or in the browser after JavaScript loads. This is a framework-agnostic architectural choice; Next.js (see [Next.js Overview](nextjs-overview.md)) is one popular framework that exposes all four as first-class options, but the concepts themselves predate it and apply to any web stack.

## The Four Core Strategies

| Strategy | HTML generated | When | Data freshness |
|---|---|---|---|
| **CSR** (Client-Side Rendering) | In the browser, via JS | After the JS bundle loads and runs | Always fresh (fetched live) |
| **SSR** (Server-Side Rendering) | On the server | On every request | Always fresh |
| **SSG** (Static Site Generation) | On the server | Once, at build time | Stale until the next build/deploy |
| **ISR** (Incremental Static Regeneration) | On the server | At build time, then re-generated on a timer/trigger | Stale until the next revalidation window |

## CSR — Client-Side Rendering

The server sends a near-empty HTML shell plus a JS bundle; the browser downloads, parses, and executes the bundle, which then fetches data and renders the page.

- **Pros**: simple mental model, fast subsequent navigations once the app is loaded (a classic single-page app).
- **Cons**: slow first paint (blank page until JS loads and runs), poor SEO by default (a crawler that doesn't execute JS sees an empty shell), a larger initial JS payload.

## SSR — Server-Side Rendering

The server executes the rendering logic (in whatever framework/language) fresh for every incoming request, producing complete HTML before it reaches the browser.

- **Pros**: fast first paint (HTML arrives ready to display), good SEO (crawlers see full content immediately), always reflects current data.
- **Cons**: slower time-to-first-byte than a pre-built static page (rendering work happens per request), higher server load under traffic.

## SSG — Static Site Generation

HTML is generated once, ahead of time (at build/deploy), and served as a plain static file from then on — often via a [CDN](../networking/cdn.md), making it extremely fast and cheap to serve at scale.

- **Pros**: fastest possible serving (no per-request server work at all), trivially cacheable/[CDN](../networking/cdn.md)-friendly, minimal server cost.
- **Cons**: content goes stale the moment underlying data changes, until the next full rebuild — unsuitable for frequently-changing or per-user content.

## ISR — Incremental Static Regeneration

A hybrid: pages are pre-built like SSG, but the framework can regenerate an individual page in the background after a configured time window (or an explicit trigger) — without rebuilding the entire site.

- **Pros**: near-SSG serving speed most of the time, without SSG's "stale until the next full deploy" limitation.
- **Cons**: more moving parts (a regeneration trigger, a background rendering process); the very first visitor after content changes may briefly see stale content while regeneration completes.

## Hydration — Where CSR and SSR/SSG Meet

**Hydration** is the process where client-side JavaScript "attaches" to server-rendered (or statically-generated) HTML that's already on the page — wiring up event listeners and component state so the already-visible markup becomes interactive, without re-rendering it from scratch. This is what lets SSR/SSG/ISR deliver fast, crawlable initial HTML *and* still become a fully interactive app once JS loads — the HTML isn't thrown away and re-rendered client-side, it's reused.

## Choosing a Strategy

| Use case | Good fit |
|---|---|
| Marketing pages, blogs, documentation | SSG (rarely changes, benefits from [CDN](../networking/cdn.md) caching) |
| Blog/catalog with frequent but not per-second updates | ISR |
| Dashboards, personalized/logged-in content, real-time data | SSR (or CSR behind an SSR'd shell) |
| Highly interactive apps where SEO doesn't matter (internal tools) | CSR |

Most modern frameworks (Next.js, Nuxt, SvelteKit, Remix) let this be decided *per route* rather than once for the whole app — a marketing site's landing pages can be SSG while its logged-in dashboard is SSR, in the same codebase.

## Common Questions

**Why does SSR/SSG matter for SEO specifically?**
> Search engine crawlers historically didn't execute JavaScript at all, and even modern crawlers that can execute it do so more slowly and unreliably than parsing plain HTML — a page whose content only exists after a client-side fetch risks being indexed incompletely or not at all. See [Technical SEO](technical-seo.md) for the fuller picture of what affects crawlability and ranking beyond rendering strategy alone.

**Is ISR strictly better than plain SSG, since it does everything SSG does plus more?**
> Not strictly — ISR adds complexity (a regeneration mechanism, cache-invalidation reasoning) that a purely static site with genuinely infrequent updates doesn't need. If content changes only on deploy anyway, plain SSG is simpler with no real downside.

## Related

- [Next.js Overview](nextjs-overview.md)
- [Technical SEO](technical-seo.md)
- [CDN](../networking/cdn.md)
