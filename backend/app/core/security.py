"""Verify Supabase-issued JWTs.

Supabase projects sign tokens either with a shared secret (HS256, the legacy
default) or with asymmetric keys published at a JWKS URL (RS256/ES256). Both
are supported; check which one your project uses under Project Settings > API.
"""
from functools import lru_cache

import jwt
from jwt import PyJWKClient, PyJWTError

from app.core.config import get_settings


class AuthError(Exception):
    pass


@lru_cache
def _jwks_client(supabase_url: str) -> PyJWKClient:
    return PyJWKClient(f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json")


def decode_supabase_token(token: str) -> dict:
    s = get_settings()
    try:
        alg = jwt.get_unverified_header(token).get("alg")
        if alg == "HS256":
            if not s.supabase_jwt_secret:
                raise AuthError("SUPABASE_JWT_SECRET is not configured")
            return jwt.decode(
                token, s.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated"
            )
        if alg in ("RS256", "ES256") and s.supabase_url:
            key = _jwks_client(s.supabase_url).get_signing_key_from_jwt(token).key
            return jwt.decode(token, key, algorithms=[alg], audience="authenticated")
        raise AuthError("Unsupported token algorithm or Supabase not configured")
    except PyJWTError as exc:
        raise AuthError(str(exc)) from exc