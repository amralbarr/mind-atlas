# Technical SEO

Technical SEO is the engineering side of search visibility — making sure a page *can* be found, crawled, rendered, and understood correctly by search engines — as distinct from content/keyword strategy (see [SEO Fundamentals](../../../marketing/concepts/digital-marketing/seo-fundamentals.md) for that side). A page with perfect content and zero technical SEO can still fail to rank simply because it was never properly indexed.

## Crawlability & Indexing

| Mechanism | Purpose |
|---|---|
| `robots.txt` | Tells crawlers which paths they may or may not crawl |
| `sitemap.xml` | Lists every URL that should be indexed, helping crawlers discover pages that aren't well-linked internally |
| `<link rel="canonical">` | Declares the "master" URL when the same content is reachable at multiple URLs (with/without trailing slash, query params, etc.), preventing duplicate-content penalties |
| [HTTP](../networking/http.md) status codes | A `404`/`410` correctly signals "gone" (see [HTTP Status Codes](../backend/api/http-status-codes.md)); a soft-404 (a "not found" page that returns `200`) confuses crawlers into indexing it as real content |

## Rendering Strategy's Effect on SEO

How a page renders directly affects whether a crawler sees its content at all — see [Rendering Strategies](rendering-strategies.md) for the underlying mechanics. In short: SSR and SSG deliver complete HTML immediately, which crawlers parse reliably; pure CSR requires the crawler to execute JavaScript to see any content, which is slower and less reliable even for crawlers that support it. A content-heavy, SEO-dependent page (a blog post, a product page) is a strong candidate for SSR/SSG/ISR specifically *because of* this; a logged-in dashboard that will never be indexed has no such constraint.

## Metadata & Structured Data

- **Title tag & meta description** — don't directly boost ranking, but strongly affect click-through rate from the search results page (this is the shared boundary with [SEO Fundamentals](../../../marketing/concepts/digital-marketing/seo-fundamentals.md) — the copy is a content decision, but *rendering it correctly per-page* is an engineering one).
- **Open Graph / Twitter Card tags** — control how a link looks when shared on social platforms (image, title, description preview).
- **Structured data ([JSON](../programming/fundamentals/json.md)-LD / schema.org)** — a machine-readable block describing what a page *is* (an article, a product, a recipe, an FAQ) — enables rich search results (star ratings, price, FAQ dropdowns directly in search listings) that plain HTML can't produce alone.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example Product",
  "offers": { "@type": "Offer", "price": "29.99", "priceCurrency": "USD" }
}
</script>
```

## Core Web Vitals

A set of performance metrics Google uses as a ranking signal, measuring real user-experienced load performance:

| Metric | Measures |
|---|---|
| **LCP** (Largest Contentful Paint) | How long until the largest visible element renders |
| **INP** (Interaction to Next Paint) | How responsive the page is to user interaction |
| **CLS** (Cumulative Layout Shift) | How much visible content unexpectedly shifts position during load |

These are directly influenced by rendering strategy and implementation choices (image optimization, font-loading strategy, avoiding render-blocking scripts) — poor Core Web Vitals scores can suppress ranking even when content and metadata are otherwise correct.

## Common Questions

**If SSR/SSG are better for SEO, is CSR ever acceptable for a public, indexable page?**
> Generally avoid pure CSR for pages that need to rank — even with a crawler that executes JavaScript, indexing is slower and less reliable, and Core Web Vitals (first paint especially) tend to suffer. A common middle ground is server-rendering the initial HTML and hydrating into a fully client-rendered app from there (see [Hydration](rendering-strategies.md#hydration--where-csr-and-ssrssg-meet)) rather than choosing pure CSR outright.

**Does technical SEO guarantee good rankings on its own?**
> No — it removes *obstacles* to being found and indexed correctly; it doesn't substitute for the content and keyword-relevance work covered in [SEO Fundamentals](../../../marketing/concepts/digital-marketing/seo-fundamentals.md). A perfectly crawlable page with no relevant content still won't rank for anything useful.

## Related

- [Rendering Strategies](rendering-strategies.md)
- [SEO Fundamentals](../../../marketing/concepts/digital-marketing/seo-fundamentals.md) *(marketing/content side)*
- [HTTP Status Codes](../backend/api/http-status-codes.md)
- [CDN](../networking/cdn.md)
