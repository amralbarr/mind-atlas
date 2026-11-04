# One-Time Passwords (OTP)

## What is an OTP System?

An OTP (One-Time Password) system is a mechanism used to verify a user's identity by generating a temporary, unique code that is valid for a short period of time. It is one of the most common ways to implement a second [authentication](authentication.md) factor (see [Access Control & IAM](../authorization/access-control-iam.md)).

## Basic Flow

1. User enters phone/email
2. Server generates OTP
3. OTP is sent via SMS or email
4. User submits OTP
5. Server verifies OTP
6. If valid, the user is authenticated

## OTP Generation (Node.js Example)

```javascript
import crypto from "crypto";

function generateOTP() {
  return crypto.randomInt(100000, 999999).toString(); // 6-digit OTP
}
```

Use a cryptographically secure random source (`crypto`, not `Math.random`) — `Math.random()` is not safe for security-sensitive values because it is not guaranteed to be unpredictable, while `crypto.randomInt`/`crypto.randomBytes` are designed for exactly this purpose.

## Storing OTPs Securely

- Do **not** store the OTP in plain text
- Store a **hashed** version instead, alongside an expiry timestamp

```javascript
import bcrypt from "bcrypt";

const otp = generateOTP();
const hashedOtp = await bcrypt.hash(otp, 10);

// Save hashedOtp in DB with expiry
```

`bcrypt` is used here rather than a general-purpose hash function (like SHA-256 via `crypto`) because it is a slow, salted, purpose-built password-hashing algorithm — it resists brute-force guessing of a short numeric code far better than a fast general-purpose hash would.

### Example DB Fields

- `user_id` / `email` / `phone`
- `otp_hash`
- `expires_at`
- `attempts_count`

## Expiration

Recommended validity window: **2–5 minutes**.

```javascript
const expires_at = Date.now() + 5 * 60 * 1000;
```

## Sending the OTP

- SMS APIs (e.g., Twilio)
- Email services (e.g., SendGrid)

## Verifying the OTP

```javascript
const isMatch = await bcrypt.compare(inputOtp, storedHash);

if (!isMatch) {
  throw new Error("Invalid OTP");
}

if (Date.now() > expires_at) {
  throw new Error("OTP expired");
}
```

## Security Best Practices

- Limit verification attempts (e.g., max 3 tries)
- Rate-limit OTP requests to prevent abuse
- Make each OTP single-use — invalidate it after a successful verification
- Add a resend cooldown (e.g., 30 seconds)
- Always use [HTTPS](../../networking/https.md)
- Log suspicious activity (repeated failures, unusual request rates)

## Advanced Improvements

- Use Redis for storage, taking advantage of built-in key expiry (TTL)
- Implement TOTP (Time-based One-Time Password), as used by authenticator apps
- Add CAPTCHA to slow down automated abuse
- Bind the OTP to a specific session or device to prevent replay from another context

## Architecture

```
Client → API → Generate OTP → Store (DB/Redis)
                    │
                    ▼
               Send SMS/Email

Client → API → Verify OTP → Validate → Login Success
```

## Short Answer

An OTP system generates a secure random code, stores a hashed version with an expiration time, sends it to the user through an out-of-band channel (SMS/email), and verifies it securely with [rate limiting](../../backend/architecture/rate-limiting.md) and attempt controls.

## Related

- [Access Control & IAM](../authorization/access-control-iam.md)
- [Nextcloud](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Hashing vs. Encryption](../secrets/hashing-vs-encryption.md)
