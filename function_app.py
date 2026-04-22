import azure.functions as func
import json
import logging
import random
import string

app = func.FunctionApp()

# Globalny magazyn w pamięci aplikacji
url_store = {}


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(chars, k=length))
        if short_code not in url_store:
            return short_code


@app.route(route="ShortenUrl", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def ShortenUrl(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("ShortenUrl endpoint called.")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Request body must be valid JSON."}),
            status_code=400,
            mimetype="application/json"
        )

    original_url = req_body.get("url")

    if not original_url or not isinstance(original_url, str):
        return func.HttpResponse(
            json.dumps({"error": "Missing or invalid 'url' field."}),
            status_code=400,
            mimetype="application/json"
        )

    if not (original_url.startswith("http://") or original_url.startswith("https://")):
        return func.HttpResponse(
            json.dumps({"error": "URL must start with http:// or https://."}),
            status_code=400,
            mimetype="application/json"
        )

    short_code = generate_short_code()
    url_store[short_code] = original_url

    response_body = {
        "shortCode": short_code,
        "originalUrl": original_url
    }

    return func.HttpResponse(
        json.dumps(response_body),
        status_code=200,
        mimetype="application/json"
    )

@app.route(route="Redirect", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def Redirect(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Redirect endpoint called.")

    short_code = req.params.get("shortCode")

    if not short_code:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'shortCode' query parameter."}),
            status_code=400,
            mimetype="application/json"
        )

    original_url = url_store.get(short_code)

    if not original_url:
        return func.HttpResponse(
            json.dumps({"error": "Short code not found."}),
            status_code=404,
            mimetype="application/json"
        )

    return func.HttpResponse(
        status_code=302,
        headers={"Location": original_url}
    )
