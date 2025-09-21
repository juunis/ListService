import json
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lambda")))

from list_service import lambda_handler

def make_event(path, data_list, method="POST"):
    return {
        "body": json.dumps({"data": data_list}),
        "httpMethod": method,
        "rawPath": path,
        "requestContext": {
            "http": {"method": method}
        }
    }

def test_head():
    event = make_event("/head", ["a", "b", "c"])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["head"] == "a"

def test_tail():
    event = make_event("/tail", ["a", "b", "c"])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["tail"] == ["b", "c"]

def test_empty_list():
    event = make_event("/head", [])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert "Data must be a non-empty list of strings" in body.get("ERROR", "")

def test_empty_string_in_list():
    event = make_event("/head", ["", "b"])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert "List cannot contain empty or whitespace strings" in body.get("ERROR", "")

def test_invalid_type_in_list():
    event = make_event("/head", [1, "b"])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert "All items in list must be strings" in body.get("ERROR", "")

def test_invalid_route():
    event = make_event("/unknown", ["a", "b"])
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 404
    assert "Route not found" in body.get("ERROR", "")

def test_invalid_method():
    event = make_event("/head", ["a", "b"], method="GET")
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 405
    assert "Invalid method. Only POST is supported." in body.get("ERROR", "")
