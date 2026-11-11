import secrets

from fastapi import Header, HTTPException, status

from app.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Enforce API key when PULSEWATCH_API_KEY is set. Constant-time compare."""
    if settings.api_key is None:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
