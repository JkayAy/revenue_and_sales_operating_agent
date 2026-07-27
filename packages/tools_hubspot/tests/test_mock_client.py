from tools_hubspot import MockHubSpotClient


def test_idempotent_note():
    client = MockHubSpotClient()
    r1 = client.create_note(contact_id="1", body="hi", idempotency_key="k1")
    r2 = client.create_note(contact_id="1", body="hi", idempotency_key="k1")
    assert r1.external_id == r2.external_id
    assert len(client.notes) == 1
