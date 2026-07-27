import hashlib

from tools_hubspot import verify_webhook_signature


def test_verify_signature_match():
    secret = "test-secret"
    body = b'[{"objectId":1}]'
    sig = hashlib.sha256(secret.encode("utf-8") + body).hexdigest()
    assert verify_webhook_signature(secret, body, sig)


def test_verify_signature_reject():
    assert not verify_webhook_signature("secret", b"{}", "bad")


def test_verify_skips_when_no_secret():
    assert verify_webhook_signature("", b"{}", None)
