import hashlib
import json

from fastapi.testclient import TestClient

from sales_api.config import settings
from sales_api.main import create_app


def test_webhook_rejects_bad_signature(monkeypatch):
    monkeypatch.setattr(settings, "hubspot_webhook_secret", "top-secret")
    monkeypatch.setattr(settings, "hubspot_client_secret", "")
    client = TestClient(create_app())
    body = json.dumps([{"objectId": 1, "propertyName": "email", "propertyValue": "a@b.io"}])
    r = client.post(
        "/v1/webhooks/hubspot",
        content=body,
        headers={"Content-Type": "application/json", "X-HubSpot-Signature": "invalid"},
    )
    assert r.status_code == 401


def test_webhook_accepts_valid_signature(monkeypatch):
    secret = "top-secret"
    monkeypatch.setattr(settings, "hubspot_webhook_secret", secret)
    body = json.dumps(
        [
            {
                "objectId": 99,
                "propertyName": "email",
                "propertyValue": "webhook@test.io",
                "company": "Acme",
                "numemployees": "120",
                "country": "US",
                "industry": "software",
            }
        ]
    ).encode("utf-8")
    sig = hashlib.sha256(secret.encode("utf-8") + body).hexdigest()
    client = TestClient(create_app())
    r = client.post(
        "/v1/webhooks/hubspot",
        content=body,
        headers={"Content-Type": "application/json", "X-HubSpot-Signature": sig},
    )
    assert r.status_code == 200
    assert r.json()["processed"] == 1
