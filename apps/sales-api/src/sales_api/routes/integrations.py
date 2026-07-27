from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from sales_api.config import settings
from sales_api.hubspot_auth import (
    build_authorize_url,
    connection_status,
    exchange_code_for_tokens,
    persist_oauth_tokens,
)

router = APIRouter(prefix="/integrations/hubspot", tags=["integrations"])


@router.get("/status")
def hubspot_status() -> dict[str, Any]:
    return connection_status()


@router.get("/authorize")
def hubspot_authorize() -> RedirectResponse:
    if not settings.hubspot_oauth_configured:
        raise HTTPException(
            status_code=501,
            detail="Set HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI",
        )
    return RedirectResponse(build_authorize_url(), status_code=302)


@router.get("/callback")
def hubspot_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> dict[str, Any]:
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not code:
        raise HTTPException(status_code=400, detail="missing_code")
    tokens = exchange_code_for_tokens(code)
    persist_oauth_tokens(tokens)
    return {"status": "connected", **connection_status()}
