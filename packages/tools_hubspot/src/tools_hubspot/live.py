from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

from tools_hubspot.client import HubSpotWriteResult

HUBSPOT_API = "https://api.hubapi.com"
# HubSpot-defined association: note → contact
NOTE_TO_CONTACT_ASSOC = 202


class LiveHubSpotClient:
    """HubSpot CRM v3 client (private app token or OAuth access token)."""

    def __init__(self, access_token: str, *, timeout: float = 30.0) -> None:
        self.access_token = access_token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_contact(self, contact_id: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(
                f"{HUBSPOT_API}/crm/v3/objects/contacts/{contact_id}",
                headers=self._headers(),
                params={
                    "properties": "email,firstname,lastname,company,country,industry,numemployees",
                },
            )
            r.raise_for_status()
            data = r.json()
            props = data.get("properties") or {}
            return {
                "id": str(data.get("id", contact_id)),
                "email": props.get("email"),
                "first_name": props.get("firstname"),
                "company": props.get("company"),
                "country": props.get("country"),
                "industry": props.get("industry"),
                "employee_count": _parse_int(props.get("numemployees")),
            }

    def create_note(
        self,
        *,
        contact_id: str,
        body: str,
        idempotency_key: str | None = None,
        dry_run: bool = False,
    ) -> HubSpotWriteResult:
        if dry_run:
            return HubSpotWriteResult(
                ok=True,
                external_id="dry-run-note",
                detail="Shadow mode — note not persisted",
                dry_run=True,
            )
        payload = {
            "properties": {"hs_note_body": body},
            "associations": [
                {
                    "to": {"id": str(contact_id)},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": NOTE_TO_CONTACT_ASSOC,
                        }
                    ],
                }
            ],
        }
        headers = self._headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(
                f"{HUBSPOT_API}/crm/v3/objects/notes",
                headers=headers,
                json=payload,
            )
            if r.status_code >= 400:
                return HubSpotWriteResult(ok=False, detail=r.text[:500])
            note_id = str(r.json().get("id", ""))
            return HubSpotWriteResult(ok=True, external_id=note_id, detail="created")

    def update_deal_stage(
        self,
        *,
        deal_id: str,
        stage_id: str,
        idempotency_key: str | None = None,
        dry_run: bool = False,
    ) -> HubSpotWriteResult:
        if dry_run:
            return HubSpotWriteResult(
                ok=True,
                external_id="dry-run-stage",
                detail=f"Would move deal {deal_id} to {stage_id}",
                dry_run=True,
            )
        headers = self._headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        with httpx.Client(timeout=self.timeout) as client:
            r = client.patch(
                f"{HUBSPOT_API}/crm/v3/objects/deals/{deal_id}",
                headers=headers,
                json={"properties": {"dealstage": stage_id}},
            )
            if r.status_code >= 400:
                return HubSpotWriteResult(ok=False, detail=r.text[:500])
            return HubSpotWriteResult(ok=True, external_id=deal_id, detail="stage_updated")


def verify_webhook_signature(
    client_secret: str,
    body: bytes,
    signature_header: str | None,
) -> bool:
    """HubSpot v1 request signature: SHA-256(secret + raw body)."""
    if not client_secret:
        return True
    if not signature_header:
        return False
    source = client_secret.encode("utf-8") + body
    expected = hashlib.sha256(source).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())


def _parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None
