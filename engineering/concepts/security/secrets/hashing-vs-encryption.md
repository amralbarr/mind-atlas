# Hashing vs. Encryption

These two are constantly confused because both turn readable data into unreadable-looking output — but they solve opposite problems: encryption is meant to be **reversed**, hashing is meant to be **irreversible**.

## Core Distinction

| | Hashing | Encryption |
|---|---|---|
| **Reversible?** | No — one-way by design | Yes — decryptable with the right key |
| **Purpose** | Verify integrity/identity without storing the original | Protect confidentiality of data that must be recovered later |
| **Key required?** | No key (plain hash) — or a secret key for [HMAC](hmac.md) | Yes — a key (symmetric) or key pair (asymmetric) is required for both directions |
| **Output length** | Fixed length regardless of input size (e.g. SHA-256 always outputs 256 bits) | Output length scales with input length |
| **Typical use** | Password storage, integrity checks, checksums, digital signatures, data structures (hash tables) | Data at rest, data in transit ([TLS](../../networking/https.md)), secrets that must be read back later |

## Hashing

A hash function takes an input of any size and deterministically produces a fixed-size output (a "digest"). The same input always produces the same output, but there's no operation that turns the output back into the input.

```javascript
const crypto = require('crypto');
crypto.createHash('sha256').update('hello').digest('hex');
// → 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
```

**Properties a cryptographic hash function must have:**

- **Deterministic** — same input always produces the same output.
- **One-way** — computationally infeasible to recover the input from the output.
- **Avalanche effect** — a tiny input change produces a completely different output.
- **Collision-resistant** — infeasible to find two different inputs producing the same output.

### Why Passwords Are Hashed, Never Encrypted

A password should never need to be *recovered* — the system only ever needs to verify "does this input match what was stored," which hashing does perfectly without ever holding a reversible copy of the real password. If a password database is stolen, hashed passwords can't be turned back into plaintext (assuming a strong algorithm and no successful brute-force/rainbow-table attack); encrypted passwords, by contrast, *could* be decrypted if the attacker also gets the key — an unnecessary extra risk for data that never needs to come back out.

### Fast Hashes vs. Password Hashes

General-purpose hashes (SHA-256, MD5) are built to be **fast** — great for checksums, bad for passwords, because fast means an attacker can brute-force billions of guesses per second on modern hardware. Password hashing uses deliberately **slow**, memory-hard algorithms instead:

| Algorithm | Why it's used for passwords |
|---|---|
| **bcrypt** | Configurable work factor (cost); intentionally slow; widely supported |
| **scrypt** | Memory-hard — expensive to parallelize on GPUs/ASICs |
| **Argon2** | Winner of the Password Hashing Competition; the current recommended default |

```javascript
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash('userPassword123', 10); // cost factor 10
const isMatch = await bcrypt.compare('userPassword123', hash);
```

### Salting

A **salt** is random data added to the input before hashing, unique per record, stored alongside the hash. It defeats precomputed rainbow-table attacks and ensures two users with the same password get different hashes. Modern password-hashing libraries (bcrypt, Argon2) generate and embed the salt automatically — you don't manage it separately.

## Encryption

Encryption transforms data using an algorithm and a **key**, and the same (or a paired) key can transform it back to the original — this reversibility is the entire point.

### Symmetric Encryption

The same key encrypts and decrypts:

```text
Plaintext --[key]--> Ciphertext --[same key]--> Plaintext
```

Fast, used for bulk data (e.g. AES). The hard problem is securely distributing/storing the shared key — anyone with it can decrypt everything.

### Asymmetric Encryption

A key pair — a public key (safe to share) encrypts, and only the paired private key can decrypt:

```text
Plaintext --[public key]--> Ciphertext --[private key]--> Plaintext
```

Slower than symmetric encryption, so it's typically used to securely exchange a symmetric session key rather than to encrypt bulk data directly — exactly what happens in a [TLS handshake](../../networking/https.md).

## HMAC: Where Hashing and a Secret Key Meet

An [HMAC](hmac.md) (Hash-based Message Authentication Code) combines a hash function with a secret key to verify both integrity *and* authenticity — proving a message wasn't tampered with *and* that it came from someone who holds the secret key. This is how [JWT](../auth/jwt.md) signatures (`HS256`) work: the token's payload is hashed together with a server-held secret, and only someone with that secret could have produced a matching signature.

## Common Questions

**If someone steals a database of bcrypt password hashes, can they get the passwords back?**
> Not directly — bcrypt is one-way. Their only option is guessing: hashing candidate passwords and comparing to the stolen hash. bcrypt's deliberate slowness makes large-scale guessing (dictionary/[brute-force attacks](../attacks/brute-force.md)) far more expensive than it would be against a fast hash like plain SHA-256.

**Why not just encrypt passwords instead of hashing them?**
> Because encryption requires a key that decrypts them back to plaintext — if that key is ever compromised (or the encryption is reversible by design), every password is exposed at once. Hashing removes that entire risk category since there's no key that reverses it.

**Is Base64 encryption?**
> No — Base64 is encoding, not encryption or hashing. It's fully and trivially reversible with no key at all; it exists to represent binary data as text-safe characters, not to provide any security property. Seeing Base64 and assuming something is "encrypted" is a common and dangerous mistake.

**Senior-level summary:**
> Hashing produces a one-way, fixed-size fingerprint used to verify data without storing or recovering the original — the right tool for passwords and integrity checks. Encryption is a reversible transformation protected by a key, used when the original data must be recoverable — the right tool for data at rest and in transit.

## Related

- [JWT](../auth/jwt.md)
- [OTP](../auth/otp.md)
- [Secrets Management](secrets-management.md)
- [HTTPS](../../networking/https.md)
- [Brute Force](../attacks/brute-force.md)
