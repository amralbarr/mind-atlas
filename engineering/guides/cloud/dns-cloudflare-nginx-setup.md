# DNS Configuration & Image Optimization (Cloudflare + Nginx)

Steps to configure the [CDN](../../concepts/networking/cdn.md) using Cloudflare and follow up with image optimization for the upload pipeline.

## Goal Architecture

```
User → Cloudflare → Nginx → Disk (/uploads)
```

## CDN Configuration Steps

### 1. Add Domain to Cloudflare

- Log in to the Cloudflare Dashboard.
- Click **Add a Site**.
- Enter domain: `studio.example.com`.
- Select a plan (Free is sufficient for now).
- Follow the instructions to update nameservers.

### 2. Update DNS Records

- Go to **[DNS](../../concepts/networking/dns.md) → Records**.
- Add a record:
  - Type: **A**
  - Name: `studio`
  - IPv4 Address: `<YOUR_SERVER_IP>`
- Enable **Proxy (Orange Cloud)**.

### 3. Configure Nginx

Ensure [Nginx](../../concepts/backend/api-gateways/nginx.md) serves uploads directly:

```nginx
location /uploads/ {
    root /var/www/app;
    access_log off;
    expires 30d;
}
```

### 4. Add a Cloudflare Cache Rule

- Go to **Rules → Cache Rules**.
- Create a rule with the following condition and settings.

**Condition:**

```
URI Path starts with /uploads
```

**Settings:**
- Cache Level: Cache Everything
- Edge TTL: 1 month
- Browser TTL: Respect Existing Headers

## Image Optimization

### Enable Cloudflare Features

- Go to **Speed → Optimization**.
- Enable:
  - Auto Minify (HTML, CSS, JS)
  - Brotli Compression
  - Polish (Image Optimization)
  - WebP (if available)

### Optional: Advanced Optimization

Use responsive images:

```html
<img src="/uploads/image.jpg" width="800" loading="lazy" />
```

Compress images before upload (recommended tools):
- TinyPNG
- ImageOptim

## Best Practices

- Keep uploads publicly accessible (no auth via Nginx).
- Use hashed filenames for cache busting.
- Avoid frequent overwrites of the same file name.
- Monitor cache hit ratio in Cloudflare Analytics.

## Notes

- The system serves static files via [CDN](../../concepts/networking/cdn.md) efficiently.
- Backend load is reduced significantly.
- Performance improvement is expected globally.

For advanced tuning, consult the official Cloudflare and Nginx documentation.

## Related
- [../../concepts/cloud/azure.md](../../concepts/cloud/azure/azure.md)
- [../../concepts/networking/cdn.md](../../concepts/networking/cdn.md)
- [../../concepts/networking/dns.md](../../concepts/networking/dns.md)
- [../../concepts/networking/https.md](../../concepts/networking/https.md)
- [../../commands/cloudflare-tunnel.md](../../commands/cloudflare-tunnel.md) — an alternative that skips this [DNS](../../concepts/networking/dns.md)-to-a-public-IP setup entirely by never exposing the origin publicly
