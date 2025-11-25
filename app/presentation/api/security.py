"""Unified security dependencies: API Key and optional JWT.

Behavior:
  - If API_KEY env var set, accept matching `X-API-Key` header.
  - If JWT_SECRET env var set, also accept valid `Authorization: Bearer <jwt>`.
  - If neither env var is set, all requests are permitted.
  - A request is authorized if ANY configured mechanism validates (logical OR).

This keeps deployment flexible: start with API key; layer JWT later without
breaking existing clients.
"""
from fastapi import Header, HTTPException
from jose import jwt, JWTError
import os


def require_api_key(x_api_key: str = Header(None)) -> bool:  # retained for backward compatibility
    expected = os.getenv("API_KEY")
    if not expected:
        return True
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


def require_auth(
    x_api_key: str = Header(None, alias="X-API-Key"),
    authorization: str = Header(None, alias="Authorization")
) -> bool:
    api_key = os.getenv("API_KEY")
    jwt_secret = os.getenv("JWT_SECRET")

    api_key_valid = False
    jwt_valid = False

    if api_key:
        api_key_valid = (x_api_key == api_key)

    if jwt_secret and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            jwt.decode(token, jwt_secret, algorithms=["HS256"])
            jwt_valid = True
        except JWTError:
            jwt_valid = False

    if not api_key and not jwt_secret:
        return True  # no security configured

    if api_key_valid or jwt_valid:
        return True

    raise HTTPException(status_code=401, detail="Unauthorized")
