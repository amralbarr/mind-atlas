# Cloudflare Tunnel (`cloudflared`) Commands

Cloudflare Tunnel exposes a local or private service to the internet through an **outbound-only** connection from your server to Cloudflare's edge — no inbound firewall port needs to be opened, and no public IP is required at all. The `cloudflared` daemon runs next to your service and maintains that outbound connection; Cloudflare's edge routes public traffic through it. This is a different problem from the [DNS](../concepts/networking/dns.md)/[CDN](../concepts/networking/cdn.md) setup in [DNS Configuration & Image Optimization](../guides/cloud/dns-cloudflare-nginx-setup.md) — that guide covers pointing a domain's [DNS](../concepts/networking/dns.md) *at* a server you already expose publicly; a Tunnel avoids exposing the server publicly at all.

## Why This Matters

```text
Without a Tunnel:  Internet → your firewall (port opened) → your server
With a Tunnel:     your server → outbound connection → Cloudflare edge → Internet
```

No inbound port to scan, brute-force, or leave misconfigured — see [Fail2ban](../concepts/security/attacks/fail2ban.md) for the class of attack this sidesteps entirely rather than mitigates. This is also a common way to expose an internal admin panel or a [Node Agent](../concepts/ai/infrastructure/gpu-scheduling.md)-style private API without a VPN, while still authenticating access at Cloudflare's edge (Cloudflare Access) rather than relying on network obscurity.

## Install & Login

```bash
brew install cloudflared                        # macOS
# or: download the binary directly for Linux — see Cloudflare's docs for the current URL

cloudflared tunnel login                        # opens a browser to authorize this machine against your Cloudflare account
```

## Quick Tunnels (No Account Config, Throwaway URL)

```bash
cloudflared tunnel --url http://localhost:3000
```

Prints a random `*.trycloudflare.com` URL that proxies to your local port immediately — no [DNS](../concepts/networking/dns.md) setup, no named tunnel. Good for a quick demo or webhook testing; the URL isn't stable across restarts, so it's not meant for anything production.

## Named Tunnels (Persistent, Production Setup)

```bash
cloudflared tunnel create my-app                # creates a tunnel + a credentials file
cloudflared tunnel list                         # list tunnels in your account
cloudflared tunnel info my-app                  # details for one tunnel
cloudflared tunnel delete my-app
```

### Routing DNS to the Tunnel

```bash
cloudflared tunnel route dns my-app app.example.com         # by tunnel name
cloudflared tunnel route dns 4a1b2c3d-... app.example.com   # by tunnel UUID — works identically, `cloudflared tunnel list` shows both
```

`route dns` accepts either the tunnel's name or its ID (the [UUID](../concepts/databases/relational/uuid.md) `cloudflared tunnel create` prints, and what `list`/`info` show) — useful when scripting this step, since the ID is stable even if the tunnel is later renamed.

```bash
dig app.example.com CNAME +short                # confirm the route actually took effect
```

An empty result means the CNAME hasn't propagated yet (or the command above didn't succeed) — see [dig Commands](dig.md) for reading this output alongside `@1.1.1.1`/`@8.8.8.8` lookups.

### Config File

```yaml
# ~/.cloudflared/config.yml
tunnel: my-app
credentials-file: /home/user/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: app.example.com
    service: http://localhost:3000
  - hostname: api.example.com
    service: http://localhost:8080
  - service: http_status:404          # catch-all — required as the last rule
```

Multiple `hostname` entries let one tunnel/one `cloudflared` process expose several local services under different subdomains — the catch-all `http_status:404` rule at the end is mandatory; without it, unmatched hostnames fail to route.

**Document what backs each port right in the comment**, once you've identified it (see the debugging section below) — a config file with several `hostname`/`service` pairs is otherwise impossible to make sense of months later without re-running `lsof`/`systemctl status` from scratch every time:

```yaml
ingress:
  - hostname: models.example.com
    service: http://localhost:8090   # nginx (nginx.service) → proxies to the model backend
  - hostname: api.example.com
    service: http://localhost:8080   # node app, managed by pm2 as "my-api"
```

[YAML](../concepts/devops/yaml.md) comments (`#`) are ignored by `cloudflared`'s parser entirely — this costs nothing and turns the config into its own documentation.

### Running the Tunnel

```bash
cloudflared tunnel run my-app                   # foreground, uses ~/.cloudflared/config.yml by default
cloudflared tunnel run --config /path/to/config.yml my-app
```

## Running as a Background Service

```bash
sudo cloudflared service install                # installs and starts a systemd (or launchd on macOS) service
sudo systemctl status cloudflared                # then manage it like any other systemd service
```

`service install` also **relocates the config it expects** — this is the single most common point of confusion with a Tunnel that works when run manually but not as a service:

| Running via | Config file it reads |
|---|---|
| `cloudflared tunnel run` (manual, your own user) | `~/.cloudflared/config.yml` |
| `cloudflared service install` (systemd/launchd) | `/etc/cloudflared/config.yml` |

```bash
sudo nano /etc/cloudflared/config.yml           # edit the SYSTEM service's config, not your user one
sudo systemctl restart cloudflared              # re-read it — see systemctl Commands for the general pattern
```

Editing `~/.cloudflared/config.yml` after installing the service has no effect on the running daemon — it's reading the `/etc/` copy instead. Note this is an *application* config file, not the systemd *unit* file itself, so `systemctl restart` (which respawns the `cloudflared` process, making it re-read its own config on startup) is what's needed here — not `daemon-reload`, which only matters after editing the unit file (`/etc/systemd/system/cloudflared.service`) itself. See [systemctl Commands § Viewing a Unit File's Content & Path](systemctl.md#viewing-a-unit-files-content--path) for the equivalent "where did my config actually go" confusion with any systemd-managed service.

See [systemctl Commands](systemctl.md) for the general service-management commands this then falls under.

## Debugging: "Ingress Rule Exists, But It Doesn't Work"

An `ingress` entry only tells Cloudflare where to *forward* traffic — it doesn't guarantee anything is actually listening there. Before suspecting the tunnel itself, confirm the local service side first:

```bash
lsof -i :8090                # is anything actually listening on the port the ingress rule points at?
sudo ss -tlnp | grep 8090    # equivalent, if lsof isn't installed
curl http://localhost:8090   # can the machine itself reach the service, independent of Cloudflare entirely?
```

An empty `lsof`/`ss` result means nothing is bound to that port at all — the [ingress](../concepts/distributed-systems/kubernetes/ingress.md) rule's `service: http://localhost:8090` has nowhere to actually forward to, which surfaces to the public client as a `502`/connection error from Cloudflare's edge, not an error from your own service (it never got called). See [Bash & Shell Commands](bash.md) for `lsof` in the general port/process-inspection context, and [curl Commands](curl.md) for verifying the local response independent of the tunnel.

### A Clean `404` With No Body Is Usually `cloudflared` Itself, Not Your Origin

If the local service check above passes (something IS listening, and a local `curl` to it works) but the public hostname still returns a bare `404` — no `content-type`, no `content-length`, nothing that looks like an actual page — that response is very likely coming from `cloudflared`'s own **catch-all** [ingress](../concepts/distributed-systems/kubernetes/ingress.md) rule (`service: http_status:404`, the mandatory last entry), not from your origin server. This means the request never matched any `hostname:` entry at all.

```bash
sudo journalctl -u cloudflared -f              # watch cloudflared's own routing decision live
curl -I https://models.example.com             # (from another terminal) trigger the request
```

The most common causes of a hostname simply not matching:

- A typo or trailing-slash mismatch in the `hostname:` value inside `config.yml` vs. the URL actually being requested.
- [DNS](../concepts/networking/dns.md) was routed for a *different* hostname than the one being tested — `cloudflared tunnel route dns <tunnel> <hostname>` has to be run once per exact hostname; routing `service.example.com` doesn't also cover `models.example.com`.
- `cloudflared` is still running its **old** config — restarting the service (`systemctl restart cloudflared`) is required after any config edit; `systemctl status cloudflared` and `journalctl -u cloudflared -n 50` confirm it actually picked up the change rather than failing silently on a [YAML](../concepts/devops/yaml.md) syntax error.

A real 404 coming from your origin app, by contrast, normally carries a `content-type`/`content-length` and whatever body your framework generates for an unmatched route — the presence or absence of those headers is the fastest way to tell which side actually generated the error.

## Common Questions

**Does a Cloudflare Tunnel replace the need for [HTTPS](../concepts/networking/https.md)/[TLS](../concepts/networking/tls.md) configuration on my own server?**
> Yes for the public-facing side — Cloudflare terminates [TLS](../concepts/networking/tls.md) at its edge, so your origin server can run plain [HTTP](../concepts/networking/http.md) on `localhost` with no certificate to manage there. See [HTTPS](../concepts/networking/https.md) for what's happening at that termination point, and note that traffic between Cloudflare's edge and your `cloudflared` daemon is itself already encrypted as part of the tunnel protocol.

**How is this different from just using ngrok?**
> Conceptually similar (both create an outbound tunnel exposing a local service publicly), but a Cloudflare named Tunnel is meant to be a persistent, production-grade setup tied to a domain you control on Cloudflare, with Cloudflare Access available for edge-level [authentication](../concepts/security/auth/authentication.md) — ngrok's free tier is oriented more toward quick, temporary exposure, closer to `cloudflared tunnel --url` above than to a named tunnel.

## Related

- [dig Commands](dig.md)
- [DNS Configuration & Image Optimization (Cloudflare + Nginx)](../guides/cloud/dns-cloudflare-nginx-setup.md)
- [systemctl Commands](systemctl.md)
- [HTTPS](../concepts/networking/https.md)
- [Fail2ban](../concepts/security/attacks/fail2ban.md)
- [CDN](../concepts/networking/cdn.md)
