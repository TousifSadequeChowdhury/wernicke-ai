"""
Session ID handling for per-visitor document isolation.

The Streamlit frontend generates one random session ID per browser tab
and sends it on every request as the X-Session-ID header. Every document
a visitor uploads, and every question they ask, gets tagged with this ID —
so ChromaDB can filter results down to only that visitor's own data.

If a request arrives with no session header (e.g. someone hitting the API
directly with curl), we generate a one-off session ID instead of erroring
out — that request just gets its own small, isolated, throwaway space.
"""
import re
import uuid

from fastapi import Header

from . import config

_SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")


def new_session_id() -> str:
    """Generate a fresh, random session ID."""
    return uuid.uuid4().hex


def get_session_id(
    x_session_id: str | None = Header(default=None, alias=config.SESSION_HEADER_NAME)
) -> str:
    """
    FastAPI dependency: reads the session header, validates its shape,
    and falls back to a fresh one-off ID if it's missing or malformed.
    """
    if x_session_id and _SESSION_ID_PATTERN.match(x_session_id):
        return x_session_id
    return new_session_id()
