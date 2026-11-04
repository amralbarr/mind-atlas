# Fail2ban

Fail2ban is an intrusion prevention daemon that monitors log files for repeated failed [authentication](../auth/authentication.md) attempts and temporarily bans the offending IP addresses by inserting firewall rules (iptables/nftables/firewalld). It is the standard tool for protecting Linux servers against [brute-force attacks](brute-force.md) on [SSH](../../protocols/ssh.md), web apps, and any service that writes failure events to a log.

## How It Works

```
Log file (e.g. /var/log/auth.log)
       ↓
   Filter  (regex matches failure patterns)
       ↓
   Jail    (counts matches per IP within a time window)
       ↓
   Action  (ban IP via iptables / send email / run script)
```

1. **Filter** — a regex that extracts the offending IP from a log line
2. **Jail** — combines a filter with thresholds (`maxretry`, `findtime`, `bantime`) and one or more actions
3. **Action** — what to do when the threshold is reached (usually add an iptables DROP rule)

## Installation

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install fail2ban -y

# RHEL / CentOS / Rocky
sudo dnf install fail2ban -y

# Enable and start
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

## Configuration Files

| Path | Purpose |
|---|---|
| `/etc/fail2ban/fail2ban.conf` | Global daemon config (log level, socket) |
| `/etc/fail2ban/jail.conf` | Built-in jail defaults (do not edit) |
| `/etc/fail2ban/jail.local` | Your overrides — create this file |
| `/etc/fail2ban/filter.d/*.conf` | Filter (regex) definitions |
| `/etc/fail2ban/action.d/*.conf` | Action definitions |

**Always edit `jail.local`, never `jail.conf`** — `jail.conf` is overwritten on package upgrades.

## jail.local — Basic Setup

```ini
# /etc/fail2ban/jail.local

[DEFAULT]
# Ban duration in seconds (or use time suffixes: 10m, 1h, 1d)
bantime  = 1h
# Time window to count failures
findtime = 10m
# Number of failures before ban
maxretry = 5
# Your own IPs — never ban these
ignoreip = 127.0.0.1/8 ::1 10.0.0.0/8 192.168.0.0/16

# Backend for reading logs (auto detects systemd/inotify)
backend = auto

# Default action: ban + send no email
action = %(action_)s

# ── Jails ──────────────────────────────────────────────

[sshd]
enabled  = true
port     = ssh          # or a custom port number
filter   = sshd
logpath  = %(sshd_log)s
maxretry = 3
bantime  = 1d

[nginx-http-auth]
enabled  = true
port     = http,https
filter   = nginx-http-auth
logpath  = /var/log/nginx/error.log
maxretry = 5

[nginx-limit-req]
enabled  = true
port     = http,https
filter   = nginx-limit-req
logpath  = /var/log/nginx/error.log
maxretry = 10
findtime = 1m

[nextcloud]
enabled  = true
port     = http,https
filter   = nextcloud
logpath  = /var/www/html/nextcloud/data/nextcloud.log
maxretry = 5
bantime  = 12h
```

## Custom Filter (for any application)

```ini
# /etc/fail2ban/filter.d/myapp.conf
[Definition]
failregex = ^.* Login failed for user .* from <HOST>.*$
            ^.* Authentication error from <HOST>.*$
ignoreregex =
```

`<HOST>` is a built-in placeholder that matches IPv4 and IPv6 addresses.

Test your filter against a real log file before enabling:

```bash
fail2ban-regex /var/log/myapp.log /etc/fail2ban/filter.d/myapp.conf
```

## Custom Jail for a FastAPI / Python App

```ini
# /etc/fail2ban/jail.local (append)
[fastapi-auth]
enabled  = true
port     = 8000
filter   = fastapi-auth
logpath  = /var/log/myapp/app.log
maxretry = 5
findtime = 5m
bantime  = 30m
```

```ini
# /etc/fail2ban/filter.d/fastapi-auth.conf
[Definition]
failregex = .*"POST /auth/login.*" 401 .* "<HOST>"
ignoreregex =
```

Your [FastAPI](../../programming/python/fastapi.md) app should log in a format that includes the client IP. With `uvicorn` access logs:

```
INFO: 203.0.113.5:54321 - "POST /auth/login HTTP/1.1" 401
```

## Nextcloud Filter

```ini
# /etc/fail2ban/filter.d/nextcloud.conf
[Definition]
_groupsre = (?:(?:,?\s*"\w+":(?:"[^"]*"|\w+))*)
failregex  = ^\{%(_groupsre)s,?\s*"remoteAddr":"<HOST>"%(_groupsre)s,?\s*"message":"Login failed
ignoreregex =
```

## Management Commands

```bash
# Check fail2ban status
sudo fail2ban-client status

# Check a specific jail
sudo fail2ban-client status sshd

# Unban an IP
sudo fail2ban-client set sshd unbanip 203.0.113.5

# Ban an IP manually
sudo fail2ban-client set sshd banip 203.0.113.5

# Reload config after changes
sudo fail2ban-client reload

# Test a filter against a log file
fail2ban-regex /var/log/auth.log /etc/fail2ban/filter.d/sshd.conf

# Show current iptables ban rules
sudo iptables -L f2b-sshd -n -v
```

## Viewing Bans & Logs

```bash
# Fail2ban log
sudo tail -f /var/log/fail2ban.log

# Show all currently banned IPs across all jails
sudo fail2ban-client status | grep "Jail list" | sed 's/.*://;s/,/\n/g' | \
  xargs -I{} sudo fail2ban-client status {} | grep "Banned IP"
```

## Email Notifications

```ini
# /etc/fail2ban/jail.local [DEFAULT]
destemail = admin@example.com
sender    = fail2ban@example.com
mta       = sendmail

# Actions with email:
# action_mw  = ban + email with whois
# action_mwl = ban + email with whois + log lines
action = %(action_mwl)s
```

## Persistent Bans (survive restarts)

By default, bans are cleared on restart. To persist them:

```ini
# /etc/fail2ban/jail.local [DEFAULT]
dbfile   = /var/lib/fail2ban/fail2ban.sqlite3
dbpurgeage = 7d   # keep ban history for 7 days
```

With `dbfile` set, fail2ban reloads active bans from the database on startup.

## Integration with UFW (Ubuntu)

```ini
# /etc/fail2ban/jail.local [DEFAULT]
banaction = ufw
```

```ini
# /etc/fail2ban/action.d/ufw.conf (create if missing)
[Definition]
actionban   = ufw insert 1 deny from <ip> to any
actionunban = ufw delete deny from <ip> to any
```

## Docker Considerations

Fail2ban runs on the **host** and reads host log files. For Dockerized services:

- Configure your container to write logs to a file on the host (volume mount or log driver)
- Or use the `docker-action` approach: have fail2ban call `docker exec` to block IPs inside the container
- For `nginx` in [Docker](../../containers/docker.md), mount `/var/log/nginx` to the host and point `logpath` there

```yaml
# docker-compose.yml
services:
  nginx:
    volumes:
      - /var/log/nginx:/var/log/nginx
```

## fail2ban vs Alternatives

| | fail2ban | UFW rate-limit | iptables hashlimit | Cloudflare [WAF](waf.md) |
|---|---|---|---|---|
| Based on | Log analysis | Kernel packet rate | Kernel packet rate | Edge network |
| Config | Regex + jails | Simple rules | Complex iptables | Web dashboard |
| App-aware | Yes (log patterns) | No | No | Yes (L7) |
| Best for | Brute-force [SSH](../../protocols/ssh.md)/web | Simple [rate limiting](../../backend/architecture/rate-limiting.md) | High-performance limits | Public-facing web apps |

## Security Best Practices

- Set `bantime` to at least `1h` for [SSH](../../protocols/ssh.md); `1d` or more for repeat offenders (use `bantime.increment = true`)
- Add your own IP to `ignoreip` to avoid locking yourself out
- Never rely on fail2ban alone — also disable password auth for [SSH](../../protocols/ssh.md) (`PasswordAuthentication no`) and use key pairs
- Monitor `/var/log/fail2ban.log` regularly or ship it to a log aggregator
- Test filters with `fail2ban-regex` before enabling jails in production

```ini
# Exponential ban time for repeat offenders
[DEFAULT]
bantime.increment   = true
bantime.factor      = 2
bantime.maxtime     = 1w
bantime.overalljails = true
```

## Related Concepts

- [systemctl (systemd) Commands](../../../commands/systemctl.md) — managing the `fail2ban` daemon itself (enable/start/status/logs)
- [NSG](../../cloud/azure/azure-nsg.md) — cloud-layer firewall (complements fail2ban on [Azure](../../cloud/azure/azure.md) VMs)
- [Access Control & IAM](../authorization/access-control-iam.md) — identity-based access control
- [WebDAV](../../protocols/webdav.md) — common target for brute-force; protect with fail2ban
- [Cloudflare Tunnel (`cloudflared`) Commands](../../../commands/cloudflare-tunnel.md) — an alternative that sidesteps this class of attack entirely by never opening an inbound port for fail2ban to defend in the first place
