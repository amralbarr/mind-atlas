# Brute-Force Attacks

A **brute-force attack** is an attempt to gain unauthorized access by systematically trying every possible credential combination until one succeeds. It requires no knowledge of the target's logic — only time and computational power.

## Attack Types

| Type | Description | Example |
|---|---|---|
| **Pure brute-force** | Try every possible character combination | `aaaa`, `aaab`, `aaac`... |
| **Dictionary attack** | Try words from a wordlist | `rockyou.txt` passwords |
| **Credential stuffing** | Try username/password pairs from leaked databases | Combolists from data breaches |
| **Password spraying** | Try one common password against many accounts | `Password123!` against all users |
| **Reverse brute-force** | Fix the password, enumerate usernames | Try `admin123` against all users |
| **Rainbow table** | Precomputed hash→password lookup | Crack unsalted MD5 hashes |

## Why It Works

- Weak or default passwords
- No account lockout policy
- No [rate limiting](../../backend/architecture/rate-limiting.md) on auth endpoints
- Leaked password databases (credential stuffing)
- Short or predictable token/[OTP](../auth/otp.md) values

## Common Targets

- [SSH](../../protocols/ssh.md) / RDP login endpoints
- Web app login forms
- Admin panels (`/admin`, `/wp-login.php`)
- API [authentication](../auth/authentication.md) endpoints
- Database ports exposed to the internet (3306, 5432)
- ZIP / encrypted file passwords

## Defenses

### 1. Rate Limiting & Lockout

Block or slow down repeated failures from the same IP or account.

```python
# FastAPI example with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginCredentials):
    ...
```

Account-level lockout (after N failures, lock the account for T minutes) prevents per-account brute-force even from distributed IPs.

### 2. Fail2ban (IP Banning)

Automatically ban IPs that exceed a failure threshold by parsing log files.

→ See [Fail2ban](./fail2ban.md) for full configuration.

### 3. Strong Password Policy

- Minimum 12 characters
- Require complexity (uppercase, lowercase, digit, symbol)
- Check against breach databases (HaveIBeenPwned API)
- Do NOT force frequent rotation — it encourages weak incremental changes

### 4. Multi-Factor Authentication (MFA)

Even with a correct password, brute-force is useless without the second factor (TOTP, hardware key, push notification). MFA is the single most effective defense against credential-based attacks.

### 5. CAPTCHA

Add a CAPTCHA challenge after N failed attempts. Effective against automated tools, not sophisticated attackers who can solve them.

### 6. Disable Password Auth for SSH

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

Force key-based [authentication](../auth/authentication.md) — brute-forcing a 4096-bit RSA key is computationally infeasible.

### 7. Secure Password Hashing

Store passwords with a slow, salted hashing algorithm so leaked hashes are not cheaply cracked:

```python
# Python — use bcrypt or argon2
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("user_password")
valid  = pwd_context.verify("user_password", hashed)
```

| Algorithm | Status |
|---|---|
| `bcrypt` | Recommended — widely supported |
| `argon2id` | Best — winner of the Password Hashing Competition |
| `scrypt` | Good — memory-hard |
| `PBKDF2` | Acceptable — used by [Django](../../programming/python/django.md) |
| `MD5 / SHA1 / SHA256` (unsalted) | **Never use** for passwords |

### 8. Monitor & Alert

Log all failed auth attempts and alert when:
- Same IP fails > N times across any accounts
- Same account fails > N times from any IPs (distributed spray)
- Login from a new country / unusual time

### 9. Network-Level Controls

- Never expose 3306 ([MySQL](../../databases/relational/mysql.md)), 5432 ([PostgreSQL](../../databases/relational/postgresql.md)), 27017 ([MongoDB](../../databases/nosql/mongodb.md)) to the internet
- Restrict [SSH](../../protocols/ssh.md) (22) to known IPs via [NSG](../../cloud/azure/azure-nsg.md) / firewall rules
- Use a VPN or Bastion host for admin access
- Use [Azure Bastion](../../cloud/remote-access/azure-bastion.md) / [AWS](../../cloud/infrastructure/aws.md) Session Manager instead of Public IPs for RDP/[SSH](../../protocols/ssh.md)

## Detection Signals

| Signal | Indicates |
|---|---|
| Many 401/403 responses from one IP | IP-based brute-force |
| Many failures across many IPs on one account | Password spray |
| Many failures across many accounts and IPs | Credential stuffing |
| Failures spiking at off-hours | Automated attack |

## Defense-in-Depth Summary

```
Layer 1 — Network:    Firewall / NSG rules, VPN, no exposed ports
Layer 2 — Rate limit: Fail2ban, API rate limiting, account lockout
Layer 3 — Auth:       MFA, SSH keys only, CAPTCHA after failures
Layer 4 — Storage:    bcrypt/argon2 hashing, salted
Layer 5 — Monitoring: Alert on anomalous failure patterns
```

No single defense is sufficient — apply all layers.

## Related Concepts

- [Fail2ban](./fail2ban.md) — automated IP banning based on log patterns
- [Access Control & IAM](../authorization/access-control-iam.md) — MFA, [RBAC](../authorization/rbac.md), least privilege
- [NSG](../../cloud/azure/azure-nsg.md) — block ports at the network level
