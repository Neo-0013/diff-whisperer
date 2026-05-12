import pytest
from privacy_shield import PrivacyShield

def test_privacy_shield_redaction():
    shield = PrivacyShield()
    test_text = 'API_KEY = "AIzaSyDummyKey12345678901234567890123"'
    shield.scan(test_text)
    redacted = shield.redact(test_text)
    assert "[REDACTED]" in redacted
    assert "AIzaSy" not in redacted

def test_privacy_shield_no_false_positives():
    shield = PrivacyShield()
    test_text = 'OTHER_VAR = "Hello World"'
    findings = shield.scan(test_text)
    assert len(findings) == 0
    redacted = shield.redact(test_text)
    assert "Hello World" in redacted
