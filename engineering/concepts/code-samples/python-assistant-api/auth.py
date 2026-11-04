"""Authentication and authorization dependency.

Deliberately simplified for illustration: a real deployment would validate
a signed token (e.g. a Microsoft Entra ID JWT) and derive group membership
from its claims, rather than trusting a plain header value.

See:
- ../../concepts/security/auth/authentication.md
- ../../concepts/security/authorization/authorization.md
- ../../concepts/security/auth/jwt.md
"""
import uuid
from dataclasses import dataclass, field

from fastapi import Header, HTTPException


@dataclass
class User:
    request_id: str
    groups: list[str] = field(default_factory=list)


async def get_current_user(
    authorization: str | None = Header(default=None),
    x_user_groups: str | None = Header(default=None),
) -> User:
    if authorization is None:
        raise HTTPException(status_code=401, detail="missing Authorization header")

    # Illustrative only: a real implementation verifies the token's
    # signature and expiry (see jwt.md) instead of trusting it as-is.
    groups = x_user_groups.split(",") if x_user_groups else []
    return User(request_id=str(uuid.uuid4()), groups=groups)
