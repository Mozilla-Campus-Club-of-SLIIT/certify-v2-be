import httpx
from fastapi import Header, HTTPException, status

from config import AUTH_API

_client: httpx.AsyncClient | None = None


def get_auth_client() -> httpx.AsyncClient:
    """Return the shared AsyncClient, creating it lazily if lifespan hasn't."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=5.0)
    return _client


async def close_auth_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _bad_gateway(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


async def verify_admin(authorization: str = Header(None)) -> dict:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        resp = await get_auth_client().get(
            f"{AUTH_API}/users/me",
            headers={"Authorization": authorization},
        )
    except httpx.RequestError:
        raise _bad_gateway("Authentication service unavailable")

    if resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if resp.status_code != 200:
        raise _bad_gateway("Authentication service error")

    try:
        payload = resp.json()
    except ValueError:
        raise _bad_gateway("Authentication service returned an invalid response")

    user = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(user, dict):
        raise _bad_gateway("Authentication service returned an unexpected response")

    roles = user.get("roles", [])
    if not isinstance(roles, list):
        raise _bad_gateway("Authentication service returned an unexpected response")

    if "certify-admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    return user
