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

def _validate_data(data):
    if not data or not isinstance(data, list):
        return False, "Data must be a non-empty list of strings"

    for string_value in data:
        if not isinstance(string_value, str):
            return False, "All items in list must be strings"
        if string_value.strip() == "":
            return False, "List cannot contain empty or whitespace strings"

    return True, None

def _handle_request(event, raw_path):
    try:
        body = json.loads(event.get("body") or "{}")
        data = body.get("data")
        
        is_valid, error = _validate_data(data)
        if not is_valid:
            return _response(400, {"ERROR": error})

        if raw_path.endswith("/head"):
            return _response(200, {"head": data[0]})
        if raw_path.endswith("/tail"):
            return _response(200, {"tail": data[1:]})

        return _response(404, {"ERROR": "Route not found"})

    except Exception as e:
        logger.exception("Error in _handle_request")
        return _response(500, {"ERROR": str(e)})

def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event))

    method = event.get("requestContext", {}).get("http", {}).get("method", event.get("httpMethod"))
    raw_path = event.get("rawPath", event.get("path", ""))

    if method != "POST":
        return _response(405, {"ERROR": "Invalid method. Only POST is supported."})

    return _handle_request(event, raw_path)
