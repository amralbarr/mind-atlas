# HMAC (Hash-based Message Authentication Code)

HMAC is a construction that combines a cryptographic hash function with a secret key to produce a value that proves two things at once: the message hasn't been tampered with (**integrity**), and it was actually created by someone who holds the secret key (**authenticity**). A plain hash alone only gives you the first guarantee — anyone can compute a plain hash of a message, including an attacker who altered it, so a bare hash can't prove who produced it. It's the mechanism behind request signing in [S3](../../protocols/s3-api.md) and [Azure Blob Storage](../../cloud/azure/azure-blob-storage.md)'s key-based auth.

## Why a plain hash isn't enough

```
Plain hash:  HMAC-less scenario
  Server stores: hash(message)
  Attacker intercepts message, changes it, recomputes hash(new_message)
  Server has no way to know the hash didn't come from the real sender
```

A plain hash proves a message matches *some* hash, but nothing ties that hash to a specific party holding a secret — anyone, including an attacker, can compute `hash(anything)`. HMAC fixes this by mixing a secret key into the hashing process itself, so only someone who knows the key could have produced a valid HMAC for a given message.

## How it works, conceptually

```
HMAC(key, message) = hash_function( (key XOR opad) + hash_function( (key XOR ipad) + message ) )
```

The exact construction (defined in RFC 2104) runs the message through the underlying hash function **twice**, each time mixed with a transformed version of the key — this nested structure is specifically designed to resist certain attacks that a naive `hash(key + message)` approach would be vulnerable to. The practical takeaway, without needing to reproduce the full proof: HMAC is a well-studied, standardized way to turn "I have a hash function" into "I have a way to prove a message came from someone holding this specific secret."

```python
import hmac
import hashlib

secret_key = b"my-secret-key"
message = b"the request being signed"

signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
```

## Verification is symmetric

Unlike a digital signature (asymmetric — sign with a private key, verify with a public key), HMAC is **symmetric**: both the sender and the verifier need the same secret key. The verifier recomputes the HMAC over the received message using their own copy of the shared key and checks it matches the one sent — if an attacker doesn't have the key, they can't produce a signature that will pass this check, even if they can see the message and its (correct) signature go by.

```python
expected = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
is_valid = hmac.compare_digest(expected, received_signature)  # constant-time comparison — see below
```

**Why `compare_digest` and not `==`:** a naive string comparison (`expected == received_signature`) exits early on the first mismatched character, which leaks timing information an attacker can exploit to guess the correct signature one byte at a time (a timing attack). `hmac.compare_digest` (or the equivalent in any serious crypto library) always takes the same amount of time regardless of where the strings first differ.

## Where it shows up in this handbook

- **[S3](../../protocols/s3-api.md)** signs every request with HMAC-SHA256 under [AWS](../../cloud/infrastructure/aws.md) Signature Version 4 — the access key identifies who's making the request, and the HMAC signature (computed with the secret key) proves they actually hold that key, without ever sending the secret key itself over the wire.
- **[Azure Blob Storage](../../cloud/azure/azure-blob-storage.md)**'s Account Key and SAS token [authentication](../auth/authentication.md) methods work the same way — the storage account key is used to compute an HMAC signature over the request, which the service verifies without the key ever needing to be transmitted per-request.

In both cases, the pattern is identical: the secret key never travels with the request — only a signature computed *from* it does, which is exactly the integrity-plus-authenticity guarantee HMAC exists to provide.

## Related

- [Hashing vs. Encryption](hashing-vs-encryption.md) — the broader comparison HMAC sits inside (it's keyed hashing, distinct from both plain hashing and encryption)
- [Amazon S3 API](../../protocols/s3-api.md) — uses HMAC-SHA256 for [AWS](../../cloud/infrastructure/aws.md) Signature Version 4 request signing
- [Azure Blob Storage](../../cloud/azure/azure-blob-storage.md) — uses HMAC-based signing for Account Key and SAS token auth
- [JWT](../auth/jwt.md) — can use an HMAC algorithm (`HS256`) for symmetric token signing, as an alternative to RSA-based asymmetric signing
