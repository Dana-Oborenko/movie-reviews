# Supabase JWT verification and role extraction
import time
import httpx
from jose import jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, status
from app.core.config import settings

_JWKS_CACHE = {"keys": None, "expires_at": 0}


def _get_jwks_url() -> str:
    # Supabase JWKS endpoint
    return f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"


def _get_issuer() -> str:
    # Supabase token issuer
    return f"{settings.SUPABASE_URL}/auth/v1"

async def get_jwks() -> dict:
    """
    Fetch JWKS from Supabase and cache it for a short time.
    """
    now = int(time.time())
    if _JWKS_CACHE["keys"] and now < _JWKS_CACHE["expires_at"]:
        return _JWKS_CACHE["keys"]

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(_get_jwks_url())
        r.raise_for_status()
        jwks = r.json()

    _JWKS_CACHE["keys"] = jwks
    _JWKS_CACHE["expires_at"] = now + 3600  # cache 1 hour
    return jwks


async def verify_supabase_jwt(token: str) -> dict:
    """
    Verify Supabase JWT using JWKS. Works with ES256 and returns clear debug errors.
    """
    try:
        from jose import jwk

        jwks = await get_jwks()

        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg", "ES256")

        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header (no kid)")

        key_dict = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key_dict:
            raise HTTPException(status_code=401, detail="Unknown token key (kid not found)")

        # Build a key object from JWK (more reliable than passing dict directly)
        public_key = jwk.construct(key_dict, alg)

        # Decode with issuer/audience checks
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            audience=settings.SUPABASE_JWT_AUD,
            issuer=f"{settings.SUPABASE_URL}/auth/v1",
            options={"verify_exp": True},
        )
        return payload

    except HTTPException:
        raise
    except Exception as e:
        # TEMP debug detail (ok for development; remove later if you want)
        raise HTTPException(status_code=401, detail=f"JWT verify failed: {e}")
