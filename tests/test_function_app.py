import sys
import os
import json
import azure.functions as func

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_app import ShortenUrl, url_store


def setup_function():
    url_store.clear()


def make_request(body_dict):
    return func.HttpRequest(
        method="POST",
        url="/api/ShortenUrl",
        body=json.dumps(body_dict).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def test_shorten_url_success():
    req = make_request({"url": "https://example.com"})
    resp = ShortenUrl(req)

    assert resp.status_code == 200

    data = json.loads(resp.get_body())
    assert data["originalUrl"] == "https://example.com"
    assert "shortCode" in data
    assert isinstance(data["shortCode"], str)
    assert len(data["shortCode"]) > 0


def test_shorten_url_missing_url():
    req = make_request({})
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing or invalid 'url' field."


def test_shorten_url_invalid_url_type():
    req = make_request({"url": 123})
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing or invalid 'url' field."


def test_shorten_url_invalid_scheme():
    req = make_request({"url": "ftp://example.com"})
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "URL must start with http:// or https://."


def test_shorten_url_invalid_json():
    req = func.HttpRequest(
        method="POST",
        url="/api/ShortenUrl",
        body=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Request body must be valid JSON."