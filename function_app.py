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

@app.route(route="Redirect", auth_level=func.AuthLevel.ANONYMOUS)
def Redirect(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )