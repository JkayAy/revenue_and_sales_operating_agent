from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HubSpotWriteResult:
    ok: bool
    external_id: str | None = None
    detail: str = ""
    dry_run: bool = False


class MockHubSpotClient:
    """In-memory HubSpot stand-in for pilot and eval."""

    def __init__(self) -> None:
        self.notes: list[dict[str, Any]] = []
        self.stage_updates: list[dict[str, Any]] = []
        self._idempotency: dict[str, HubSpotWriteResult] = {}

    def create_note(
        self,
        *,
        contact_id: str,
        body: str,
        idempotency_key: str | None = None,
        dry_run: bool = False,
    ) -> HubSpotWriteResult:
        if idempotency_key and idempotency_key in self._idempotency:
            return self._idempotency[idempotency_key]
        if dry_run:
            result = HubSpotWriteResult(
                ok=True,
                external_id="dry-run-note",
                detail="Shadow mode — note not persisted",
                dry_run=True,
            )
        else:
            note_id = f"note_{len(self.notes) + 1}"
            self.notes.append({"id": note_id, "contact_id": contact_id, "body": body})
            result = HubSpotWriteResult(ok=True, external_id=note_id, detail="created")
        if idempotency_key:
            self._idempotency[idempotency_key] = result
        return result

    def update_deal_stage(
        self,
        *,
        deal_id: str,
        stage_id: str,
        idempotency_key: str | None = None,
        dry_run: bool = False,
    ) -> HubSpotWriteResult:
        if idempotency_key and idempotency_key in self._idempotency:
            return self._idempotency[idempotency_key]
        if dry_run:
            result = HubSpotWriteResult(
                ok=True,
                external_id="dry-run-stage",
                detail=f"Would move deal {deal_id} to {stage_id}",
                dry_run=True,
            )
        else:
            self.stage_updates.append({"deal_id": deal_id, "stage_id": stage_id})
            result = HubSpotWriteResult(ok=True, external_id=deal_id, detail="stage_updated")
        if idempotency_key:
            self._idempotency[idempotency_key] = result
        return result
