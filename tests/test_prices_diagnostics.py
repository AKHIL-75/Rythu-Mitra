"""Connection diagnostics must never log URLs or credentials."""
import logging
import pytest
import requests
from urllib.error import URLError
from ml import prices

@pytest.mark.parametrize("kind", [requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout])
def test_safe_provider_diagnostics(monkeypatch, caplog, kind):
    monkeypatch.setattr(prices.sys, "platform", "linux")
    def fail(*args, **kwargs):
        raise kind("https://example.invalid/?api-key=PRIVATE_TEST_SECRET")
    monkeypatch.setattr(prices.requests, "get", fail)
    with caplog.at_level(logging.WARNING, logger="ml.prices"):
        with pytest.raises((URLError, TimeoutError)):
            prices._open_provider("https://example.invalid/?api-key=PRIVATE_TEST_SECRET", 25)
    assert "PRIVATE_TEST_SECRET" not in caplog.text
    assert "example.invalid" not in caplog.text
    assert "api.data.gov.in" in caplog.text
    assert kind.__name__ in caplog.text
