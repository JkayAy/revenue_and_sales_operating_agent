from __future__ import annotations

import json
from typing import Any

import httpx

from sales_api.config import settings
from sales_api.models import OutreachDraft
from sales_api.store import get_flags


def generate_draft(
    *,
    first_name: str | None,
    company: str | None,
    research: dict[str, Any],
    tone: str,
    template_draft: OutreachDraft,
) -> OutreachDraft:
    flags = get_flags()
    if not (settings.llm_draft_enabled and flags.get("llm_draft_enabled")):
        return template_draft
    if not settings.openai_api_key.strip():
        return template_draft
    try:
        return _openai_draft(
            first_name=first_name,
            company=company,
            research=research,
            tone=tone,
        )
    except Exception:
        return template_draft


def _openai_draft(
    *,
    first_name: str | None,
    company: str | None,
    research: dict[str, Any],
    tone: str,
) -> OutreachDraft:
    sources = research.get("sources", [])
    points = research.get("talking_points", [])
    system = (
        "You write short B2B sales first-touch emails. Output JSON only with keys "
        '"subject" and "body". No markdown. Under 150 words body. '
        f"Tone: {tone}. Do not invent facts not in the brief."
    )
    user = json.dumps(
        {
            "first_name": first_name,
            "company": company,
            "talking_points": points,
            "sources": sources,
        }
    )
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=45.0) as client:
        r = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    data = json.loads(content)
    subject = str(data.get("subject", "")).strip()
    body = str(data.get("body", "")).strip()
    if not subject or not body:
        raise ValueError("empty llm draft")
    return OutreachDraft(subject=subject, body=body, version=1)
