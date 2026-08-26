from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from tools_hubspot import verify_webhook_signature

from sales_api.config import settings
from sales_api.hubspot_auth import get_effective_access_token
from sales_api.lead_service import process_ingest
from sales_api.store import get_hubspot_client

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/hubspot")
async def hubspot_webhook(request: Request) -> dict[str, Any]:
    body = await request.body()
    signature = request.headers.get("X-HubSpot-Signature")
    secret = settings.hubspot_webhook_secret or settings.hubspot_client_secret
    if secret and not verify_webhook_signature(secret, body, signature):
        raise HTTPException(status_code=401, detail="invalid_signature")

    try:
        payload = json.loads(body.decode("utf-8") or "[]")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid_json") from exc

    events = payload if isinstance(payload, list) else [payload]
    results: list[dict[str, Any]] = []
    hubspot = get_hubspot_client()

    for event in events:
        ingest_body = _event_to_ingest(event, hubspot)
        if not ingest_body:
            continue
        lead, run = process_ingest(
            request.app.state.playbook_engine,
            request.app.state.orchestrator,
            ingest_body,
        )
        results.append({"lead_id": lead.id, "run_id": run.id, "status": lead.status})

    if not results:
        raise HTTPException(status_code=400, detail="no_ingestible_events")
    return {"processed": len(results), "results": results}


def _event_to_ingest(event: dict[str, Any], hubspot: Any) -> dict[str, Any] | None:
    props = event.get("properties") if isinstance(event.get("properties"), dict) else {}
    email = (
        props.get("email") or event.get("propertyValue")
        if event.get("propertyName") == "email"
        else None
    )
    if not email and event.get("propertyName") == "email":
        email = event.get("propertyValue")

    contact_id = str(event.get("objectId") or props.get("hs_object_id") or "")

    first_name = props.get("firstname") or props.get("first_name") or event.get("firstname")
    company = props.get("company") or event.get("company")
    employee_count = _parse_int(
        props.get("employee_count")
        or props.get("numemployees")
        or event.get("numemployees")
    )
    country = props.get("country") or event.get("country")
    industry = props.get("industry") or event.get("industry")

    if (
        not email
        and contact_id
        and get_effective_access_token()
        and hasattr(hubspot, "get_contact")
    ):
        try:
            contact = hubspot.get_contact(contact_id)
            email = contact.get("email")
            first_name = first_name or contact.get("first_name")
            company = company or contact.get("company")
            employee_count = employee_count or contact.get("employee_count")
            country = country or contact.get("country")
            industry = industry or contact.get("industry")
        except Exception:
            pass

    if not email:
        return None

    return {
        "email": email,
        "first_name": first_name,
        "company": company,
        "employee_count": employee_count,
        "country": country,
        "industry": industry,
        "hubspot_contact_id": contact_id or None,
    }


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
