# Load Balancing

Load balancing is the practice of distributing incoming traffic across multiple backend servers instead of sending it all to one — so no single server becomes a bottleneck or a single point of failure, and capacity can be added by adding more servers ([horizontal scaling](../backend/architecture/horizontal-scaling.md)) rather than making one server bigger.

```text
                  ┌──> Server 1
Client → Load Balancer ──> Server 2
                  └──> Server 3
```

## L4 vs. L7 Load Balancing

The most fundamental distinction is *which layer of the network stack* the load balancer makes routing decisions at.

| | L4 (Transport layer) | L7 (Application layer) |
|---|---|---|
| Operates on | IP address + [TCP](tcp.md)/UDP port — doesn't inspect the payload | Full [HTTP](http.md) request — method, path, headers, cookies, body |
| Decision basis | Which backend gets this *connection* | Which backend gets this *specific request* |
| Can route by URL path (`/api` vs `/static`)? | No | Yes |
| Can terminate [TLS](tls.md)? | Typically passes encrypted traffic through untouched | Commonly terminates [TLS](tls.md) itself, then talks plain [HTTP](http.md) internally |
| Performance | Faster — less to inspect per packet | Slower per-request, but negligible for most workloads given the flexibility gained |
| Examples | [AWS](../cloud/infrastructure/aws.md) Network Load Balancer (NLB), raw [TCP](tcp.md)/UDP load balancers, IPVS | [NGINX](../backend/api-gateways/nginx.md), [Kong](../backend/api-gateways/kong.md), [Traefik](../backend/api-gateways/traefik.md), [AWS](../cloud/infrastructure/aws.md) Application Load Balancer (ALB) |

A simple way to remember it: **L4 load balances connections; L7 load balances requests.** An L4 balancer can't tell that `GET /orders` and `GET /images/logo.png` are different things — it only sees a stream of [TCP](tcp.md) packets to route. An L7 balancer reads the actual [HTTP](http.md) request and can route `/orders` to the orders service and `/images` to a static-file server, all behind the same public IP.

## Load Balancing Algorithms

| Algorithm                                    | How it picks a backend                                                                                                                                               |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Round robin**                              | Cycles through backends in order — simple, assumes all backends and requests are roughly equal                                                                       |
| **Least connections**                        | Sends the next request to whichever backend currently has the fewest active connections — better than round robin when requests vary a lot in duration               |
| **Weighted round robin / least connections** | Same as above, but backends are given weights (e.g. a bigger server gets 2x the traffic of a smaller one)                                                            |
| **IP hash**                                  | Routes based on a hash of the client's IP, so the same client consistently lands on the same backend — a simple way to get "sticky" behavior without a session store |
| **Random**                                   | Picks a backend at random — surprisingly competitive at scale, cheap to compute                                                                                      |
| **Least response time**                      | Combines active connection count with observed latency — favors backends that are both underloaded *and* currently fast                                              |

## Health Checks

A load balancer is only useful if it stops sending traffic to a backend that's actually broken. It periodically probes each backend (an [HTTP](http.md) request to a `/health` endpoint, or a raw [TCP](tcp.md) connection attempt) and removes any that fail from the rotation until they recover — see [Health, Liveness & Readiness](../backend/architecture/health-liveness-readiness.md) for how this connects to what a backend should actually report.

```nginx
upstream orders_backend {
    server orders-1:3000;
    server orders-2:3000;
}
# NGINX Plus / external health-check modules handle active probing;
# open-source NGINX detects failures passively via failed proxy attempts
```

## Sticky Sessions

Some applications store session state in server memory rather than a shared store, which means a given client must keep landing on the *same* backend or their session appears to vanish. A load balancer can enforce this via a cookie it sets (`Set-Cookie: SERVERID=backend-2`) or via IP hashing — but sticky sessions undermine even distribution and are considered a workaround, not a best practice. The more scalable fix is making backends stateless and storing session/connection state in a shared store (e.g. Redis) instead of relying on stickiness at all — this matters even more for [WebSockets](websockets.md), where the "session" is a live open connection that genuinely can't be moved between backends mid-flight.

## DNS Load Balancing vs. a Dedicated Load Balancer

[DNS](dns.md) can return multiple IPs for one hostname and let clients pick, which spreads load crudely across servers — but [DNS](dns.md) has no awareness of backend health or load, and clients/resolvers cache results for varying, hard-to-control lengths of time. A dedicated load balancer (hardware or software) sits in the actual traffic path, can react to health checks within seconds, and makes a fresh decision per connection/request — [DNS](dns.md)-based "load balancing" is a coarse, low-control first layer often combined *with*, not instead of, a real load balancer (e.g. [DNS](dns.md) spreads traffic across regions, and a regional load balancer handles distribution within that region).

## Where Load Balancing Fits in a Real Stack

```text
Internet
   ↓
DNS (coarse, regional distribution)
   ↓
L4/L7 Load Balancer (or reverse proxy acting as one — see Reverse Proxy)
   ↓
Backend service instances
   ↓
Database (often with its own load-balancing concern — see Read Replicas)
```

A single tool often plays both the load-balancer and [reverse-proxy](reverse-proxy.md) role at once — [NGINX](../backend/api-gateways/nginx.md), for example, terminates [TLS](tls.md), proxies the request to an internal backend, *and* chooses which of several backend instances handles it, all in one config.

## Common Questions

**Is a load balancer the same thing as a [reverse proxy](reverse-proxy.md)?**
> Related but distinct concepts — a [reverse proxy](reverse-proxy.md) forwards requests to *a* backend on the backend's behalf; load balancing specifically means choosing *which* backend among several. Many real tools ([NGINX](../backend/api-gateways/nginx.md), [Traefik](../backend/api-gateways/traefik.md), [Kong](../backend/api-gateways/kong.md)) do both at once, which is why the terms get used almost interchangeably in practice. See [Reverse Proxy](reverse-proxy.md) for the distinction in full.

**When would you choose L4 over L7 given L7 is more flexible?**
> When the traffic isn't [HTTP](http.md) at all (raw [TCP](tcp.md)/UDP, database connections, arbitrary protocols) — L7 balancers are [HTTP](http.md)-aware and can't help there — or when raw throughput/latency at very high connection volumes matters more than content-aware routing.

**How does load balancing interact with autoscaling?**
> They're complementary: autoscaling changes *how many* backend instances exist based on load; the load balancer continuously redistributes traffic across whatever instances currently exist, including newly launched or terminated ones (which is why new instances must pass health checks before receiving real traffic).

## Related

- [TLS](tls.md) — termination is commonly handled by the same tool that load-balances
- [Reverse Proxy](reverse-proxy.md)
- [NGINX](../backend/api-gateways/nginx.md)
- [Kong](../backend/api-gateways/kong.md)
- [Traefik](../backend/api-gateways/traefik.md)
- [Health, Liveness & Readiness](../backend/architecture/health-liveness-readiness.md)
- [Mesh Architecture](../distributed-systems/patterns/mesh-architecture.md)
- [Exponential Backoff and Jitter](../backend/resilience/exponential-backoff-and-jitter.md) — a load balancer's own upstream timeout is a hard ceiling an application-level request deadline must stay under, or it returns a [504](../backend/api/http-status-codes.md) before the application even finishes retrying
