import sys
import os
import json
import azure.functions as func

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_app import ShortenUrl, Redirect, url_store


def setup_function():
    url_store.clear()


def make_post_request(body_dict):
    return func.HttpRequest(
        method="POST",
        url="/api/ShortenUrl",
        body=json.dumps(body_dict).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def make_get_request(params=None):
    return func.HttpRequest(
        method="GET",
        url="/api/Redirect",
        body=None,
        params=params or {},
    )


# =========================
# TESTY ShortenUrl
# =========================

def test_shorten_url_success():
    req = make_post_request({"url": "https://example.com"})
    resp = ShortenUrl(req)

    assert resp.status_code == 200

    data = json.loads(resp.get_body())
    assert data["originalUrl"] == "https://example.com"
    assert "shortCode" in data
    assert isinstance(data["shortCode"], str)
    assert len(data["shortCode"]) > 0


def test_shorten_url_missing_url():
    req = make_post_request({})
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing or invalid 'url' field."


def test_shorten_url_invalid_url_type():
    req = make_post_request({"url": 123})
    resp = ShortenUrl(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing or invalid 'url' field."


def test_shorten_url_invalid_scheme():
    req = make_post_request({"url": "ftp://example.com"})
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


# =========================
# TESTY Redirect
# =========================

def test_redirect_success():
    req = make_post_request({"url": "https://example.com"})
    resp = ShortenUrl(req)

    data = json.loads(resp.get_body())
    short_code = data["shortCode"]

    redirect_req = make_get_request({"shortCode": short_code})
    redirect_resp = Redirect(redirect_req)

    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["Location"] == "https://example.com"


def test_redirect_missing_short_code():
    req = make_get_request()
    resp = Redirect(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing 'shortCode' query parameter."


def test_redirect_empty_short_code():
    req = make_get_request({"shortCode": ""})
    resp = Redirect(req)

    assert resp.status_code == 400

    data = json.loads(resp.get_body())
    assert data["error"] == "Missing 'shortCode' query parameter."


def test_redirect_short_code_not_found():
    req = make_get_request({"shortCode": "unknown123"})
    resp = Redirect(req)

    assert resp.status_code == 404

    data = json.loads(resp.get_body())
    assert data["error"] == "Short code not found."


def test_redirect_uses_existing_mapping():
    url_store["abc123"] = "https://openai.com"

    req = make_get_request({"shortCode": "abc123"})
    resp = Redirect(req)

    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://openai.com"


def test_redirect_after_multiple_shortened_urls():
    req1 = make_post_request({"url": "https://example.com"})
    resp1 = ShortenUrl(req1)
    data1 = json.loads(resp1.get_body())

    req2 = make_post_request({"url": "https://openai.com"})
    resp2 = ShortenUrl(req2)
    data2 = json.loads(resp2.get_body())

    redirect_req1 = make_get_request({"shortCode": data1["shortCode"]})
    redirect_resp1 = Redirect(redirect_req1)

    redirect_req2 = make_get_request({"shortCode": data2["shortCode"]})
    redirect_resp2 = Redirect(redirect_req2)

    assert redirect_resp1.status_code == 302
    assert redirect_resp1.headers["Location"] == "https://example.com"

    assert redirect_resp2.status_code == 302
    assert redirect_resp2.headers["Location"] == "https://openai.com"


def test_redirect_is_case_sensitive():
    url_store["AbC123"] = "https://example.com"

    req = make_get_request({"shortCode": "abc123"})
    resp = Redirect(req)

    assert resp.status_code == 404

    data = json.loads(resp.get_body())
    assert data["error"] == "Short code not found."