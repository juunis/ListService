import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event))

    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", event.get("httpMethod"))
    raw_path = event.get("rawPath", event.get("path", ""))

    if method == "POST" and raw_path.endswith("/head"):
        return get_head(event)
    if method == "POST" and raw_path.endswith("/tail"):
        return get_tail(event)

    return _response(404, {"ERROR": "Route not found"})

def get_head(event):
    try:
        body = json.loads(event.get("body") or "{}")
        data = body.get("data")
        if not data or not isinstance(data, list):
            return _response(400, {"ERROR": "Data must be a non-empty list"})
        return _response(200, {"head": data[0]})
    except Exception as e:
        logger.exception("Error in get_head")
        return _response(500, {"ERROR": str(e)})

def get_tail(event):
    try:
        body = json.loads(event.get("body") or "{}")
        data = body.get("data")
        if not data or not isinstance(data, list):
            return _response(400, {"ERROR": "Data must be a non-empty list"})
        return _response(200, {"tail": data[1:]})
    except Exception as e:
        logger.exception("Error in get_tail")
        return _response(500, {"ERROR": str(e)})
