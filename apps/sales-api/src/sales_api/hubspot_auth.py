from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from sales_api.config import settings
from sales_api.database import db_enabled, pg_dsn

HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
DEFAULT_SCOPES = (
    "crm.objects.contacts.read crm.objects.contacts.write "
    "crm.objects.deals.read crm.objects.deals.write"
)


def get_effective_access_token() -> str | None:
    if settings.hubspot_access_token.strip():
        return settings.hubspot_access_token.strip()
    if db_enabled():
        row = _load_connection_from_db()
        if not row:
            return None
        token, refresh, expires_at = row
        if expires_at and expires_at < datetime.now(UTC):
            if refresh:
                refreshed = _refresh_access_token(refresh)
                if refreshed:
                    return refreshed.get("access_token")
            return None
        return token
    return None


def _refresh_access_token(refresh_token: str) -> dict[str, Any] | None:
    if not settings.hubspot_oauth_configured:
        return None
    data = {
        "grant_type": "refresh_token",
        "client_id": settings.hubspot_client_id,
        "client_secret": settings.hubspot_client_secret,
        "refresh_token": refresh_token,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                HUBSPOT_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            r.raise_for_status()
            payload = r.json()
    except Exception:
        return None
    persist_oauth_tokens(payload)
    return payload


def build_authorize_url(state: str = "pipelinepilot") -> str:
    params = {
        "client_id": settings.hubspot_client_id,
        "redirect_uri": settings.hubspot_redirect_uri,
        "scope": DEFAULT_SCOPES,
        "state": state,
    }
    q = urlencode(params)
    return f"{HUBSPOT_AUTH_URL}?{q}"


def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.hubspot_client_id,
        "client_secret": settings.hubspot_client_secret,
        "redirect_uri": settings.hubspot_redirect_uri,
        "code": code,
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            HUBSPOT_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        return r.json()


def persist_oauth_tokens(token_response: dict[str, Any], portal_id: str | None = None) -> None:
    access = token_response.get("access_token", "")
    refresh = token_response.get("refresh_token", "")
    expires_in = int(token_response.get("expires_in", 3600))
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
    if not db_enabled():
        settings.hubspot_access_token = access
        return
    import psycopg

    dsn = pg_dsn()
    assert dsn
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        conn.execute(
            """
            INSERT INTO hubspot_connections (
              org_id, portal_id, access_token_enc, refresh_token_enc, expires_at
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (org_id) DO UPDATE SET
              portal_id = EXCLUDED.portal_id,
              access_token_enc = EXCLUDED.access_token_enc,
              refresh_token_enc = EXCLUDED.refresh_token_enc,
              expires_at = EXCLUDED.expires_at
            """,
            (
                settings.default_org_id,
                portal_id,
                access,
                refresh,
                expires_at,
            ),
        )
        conn.commit()


def connection_status() -> dict[str, Any]:
    token = get_effective_access_token()
    return {
        "connected": bool(token),
        "oauth_configured": settings.hubspot_oauth_configured,
        "mock_tools": settings.mock_tools,
        "source": (
            "env_token"
            if settings.hubspot_access_token.strip()
            else ("database" if token else "none")
        ),
    }


def _load_connection_from_db() -> tuple[str, str | None, datetime | None] | None:
    import psycopg

    dsn = pg_dsn()
    assert dsn
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        row = conn.execute(
            """
            SELECT access_token_enc, refresh_token_enc, expires_at FROM hubspot_connections
            WHERE org_id = %s
            """,
            (settings.default_org_id,),
        ).fetchone()
        if not row or not row[0]:
            return None
        return str(row[0]), (str(row[1]) if row[1] else None), row[2]
